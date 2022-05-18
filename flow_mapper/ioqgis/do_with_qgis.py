from ..treebuilder.treebuilder import buildTree
from ..treebuilder.spiraltree import connectionsToWkt, spiraltreeToPandas
from qgis.core import QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsVectorFileWriter, QgsProject
from qgis.PyQt.QtCore import QVariant
from qgis import processing

def do(namestring, lyr, expr, vol_flds=None, alpha=25, proj=None, stop_dst=0):
    result = processing.run("native:reprojectlayer", {
        "INPUT": lyr,
        "TARGET_CRS": proj,
        "OUTPUT": 'TEMPORARY_OUTPUT'
    })
    lyr = result['OUTPUT']
    T = input(lyr, expr, vol_flds, alpha, stop_dst)
    out_lyr = output(T, namestring, vol_flds, proj)
    return out_lyr


def input(in_lyr, expression, vol_flds=None, alpha=25, stop_dst=0):
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
    connectionsToWkt(T)
    return T


def output(T, namestring, vol_flds, proj):
    pdtb = spiraltreeToPandas(T)
    out_lyr = QgsVectorLayer(f"LineString?crs={proj}", namestring, "memory")
    out_lyr.startEditing()
    pr = out_lyr.dataProvider()
    pr.addAttributes([QgsField("type", QVariant.String)] + [QgsField(f"{name}", QVariant.Double) for name in vol_flds])
    out_lyr.updateFields()

    for index, row in pdtb.iterrows():
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromWkt(str(row["Wkt"])))
        attrs = [row["type"]]
        for fld in vol_flds:
            attrs.append(row[fld])
        fet.setAttributes(attrs)
        pr.addFeatures([fet])
    
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