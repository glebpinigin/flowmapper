from ..core.treebuilder import buildTree
from ..core.distributor.spiraltree import spiraltreeToPandas
from ..core.drawer.pptr import ppTr, ptsToSpline
from ..core.drawer.thcktr import thckTr, nodeOffset, linScale
from shapely import wkt
from shapely.geometry import LineString
import numpy as np

from qgis.core import QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsVectorFileWriter, QgsProject, QgsRenderContext, QgsUnitTypes
from qgis.core import qgsfunction, QgsPointXY, QgsLineString
from qgis.PyQt.QtCore import QVariant
from qgis import processing
from qgis.utils import iface


def flowTreeBuildAction(namestring, lyr, expr, vol_flds=None, alpha=25, proj=None, stop_dst=0, geom_n=4):
    result = processing.run("native:reprojectlayer", {
        "INPUT": lyr,
        "TARGET_CRS": proj,
        "OUTPUT": 'TEMPORARY_OUTPUT'
    })
    lyr = result['OUTPUT']
    T = _input(lyr, expr, vol_flds, alpha, stop_dst, geom_n)
    out_lyr = _output(T, namestring, vol_flds, proj)
    return out_lyr


def _input(in_lyr, expression, vol_flds=None, alpha=25, stop_dst=0, geom_n=4):
    in_lyr.selectByExpression(expression, QgsVectorLayer.SetSelection)
    root = in_lyr.selectedFeatures()[0]
    rootpt = root.geometry().asPoint()
    root_x = rootpt.x()
    root_y = rootpt.y()
    bias = (root_x, root_y)
    in_lyr.invertSelection()
    other = in_lyr.selectedFeatures()

    leaves = []
    volumes = []
    for feature in other:
        geom = feature.geometry()
        pt = geom.asPoint()
        x = pt.x() - root_x
        y = pt.y() - root_y
        leaves.append((x, y))
        onevolume = []
        for fld in vol_flds:
            onevolume.append(feature[fld])
        volumes.append(onevolume)

    T = buildTree(leaves=leaves, bias=bias, alpha=alpha, vol_attrs=[vol_flds, volumes], stop_dst=stop_dst)
    ppTr(T, geom_n)
    return T


def _output(T, namestring, vol_names, proj):
    pdtb = spiraltreeToPandas(T)
    out_lyr = QgsVectorLayer(f"LineString?crs={proj}", namestring, "memory")
    out_lyr.startEditing()
    pr = out_lyr.dataProvider()
    vol_attrs = [QgsField(f"{name}", QVariant.Double) for name in vol_names]
    service_flds = ["type", "source", "target"]
    service_attrs = [QgsField(f"{name}", QVariant.String) for name in service_flds]
    flds = service_flds + vol_names # field names
    attrs = service_attrs + vol_attrs # attributes
    pr.addAttributes(attrs)
    out_lyr.updateFields()

    features = []
    for index, row in pdtb.iterrows():
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromWkt(str(row["raw_geom"])))
        values = [row[fld] for fld in flds]
        fet.setAttributes(values)
        features.append(fet)
    pr.addFeatures(features)
    
    out_lyr.commitChanges()
    out_lyr.updateExtents()
    QgsProject.instance().addMapLayer(out_lyr)
    return out_lyr


def write(out_lyr, path):
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "ESRI Shapefile"
    transform_context = QgsProject.instance().transformContext()
    error = QgsVectorFileWriter.writeAsVectorFormatV2(out_lyr, path, transform_context, options)
    if error[0] == QgsVectorFileWriter.NoError:
        print("success again!")
    else:
        print(error)

@qgsfunction(args='auto', group='FlowMapper')
def soft_scale_linear(value, domain_min, domain_max, range_min, range_max, feature, parent):
    """
    Transforms a given value from an input domain to an output range using linear interpolation,
    but keeps 0-values 0.
    
    Syntax and arguments same as standard qgsfunction "scale_linear"
    """
    return linScale(value, domain_min, domain_max, range_min, range_max)

@qgsfunction(args='auto', group='FlowMapper', usesGeometry=True)
def splineLine(ptsnum, feature, parent):
    """ Returns geometry interpolated with spline """
    linestr = feature.geometry().asWkt()
    line = wkt.loads(linestr)
    pts = np.array(line.coords)
    pts = ptsToSpline(pts, ptsnum)
    new_line = LineString(pts)
    linestr = new_line.wkt
    geometry = QgsGeometry().fromWkt(linestr)
    return geometry

@qgsfunction(args='auto', group='FlowMapper', usesGeometry=True, handlesnull=True)
def drawTree(ptsnum, p_feature, attrs, unitname, feature, parent):
    """ Returns geometry of tree that should be drawn """
    if feature["type"] == "root-connection":
        return feature.geometry()
    # распаковка геометрии
    pts = feature.geometry().asPolyline() # point to move
    p_geom = p_feature.geometry()
    pt = pts[0]
    try:
        # handling interactive editing case: edited geometry is NULL
        backpt = p_geom.asPolyline()[-2] # backpt
    except ValueError:
        pts = ptsToSpline(pts, ptsnum)
        geometry = QgsGeometry(QgsLineString(pts))
        return geometry
    # распаковка типа
    type = feature["type"][-5:]
    type = "left" if type == "-left" else "right"

    width_pt = 0
    width_back = 0
    for attr in attrs:
        width_pt += feature[f"{attr}_width"]
        width_back += p_feature[f"{attr}_width"]
    

    set = iface.mapCanvas().mapSettings()
    unit = QgsUnitTypes().decodeRenderUnit(unitname)[0]
    width_pt = QgsRenderContext().fromMapSettings(set).convertToMapUnits(width_pt, unit)
    width_back = QgsRenderContext().fromMapSettings(set).convertToMapUnits(width_back, unit)
    lastpt = nodeOffset(pt, backpt, type, width_pt, width_back)
    pts[0] = QgsPointXY(*lastpt)
    pts = ptsToSpline(pts, ptsnum)
    geometry = QgsGeometry(QgsLineString(pts))
    return geometry