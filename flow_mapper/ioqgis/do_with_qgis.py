from ..treebuilder.treebuilder import buildTree
from ..treebuilder.spiraltree import connectionsToWkt, spiraltreeToPandas
from qgis.core import QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsCoordinateTransformContext, QgsVectorFileWriter, QgsProject
from qgis.PyQt.QtCore import QVariant
from qgis import processing

def do(namestring, lyr, expr, vol_flds=None, alpha=25, proj=None):
    result = processing.run("native:reprojectlayer", {
        "INPUT": lyr,
        "TARGET_CRS": proj,
        "OUTPUT": 'TEMPORARY_OUTPUT'
    })
    lyr = result['OUTPUT']
    T = input(lyr, expr, vol_flds, alpha)
    out_lyr = output(T, namestring)
    return out_lyr


def input(in_lyr, expression, vol_flds=None, alpha=25):
    in_lyr.selectByExpression(expression, QgsVectorLayer.SetSelection)
    root = in_lyr.selectedFeatures()[0]
    rootpt = root.geometry().asPoint()
    root_x = rootpt.x()
    root_y = rootpt.y()
    bias = (root_x, root_y)
    in_lyr.invertSelection()
    other = in_lyr.selectedFeatures()

    leaves = []
    for feature in other:
        geom = feature.geometry()
        pt = geom.asPoint()
        x = pt.x() - root_x
        y = pt.y() - root_y
        leaves.append((x, y))

    T = buildTree(leaves=leaves, bias=bias, alpha=alpha)
    connectionsToWkt(T)
    return T


def output(T, namestring):
    pdtb = spiraltreeToPandas(T)
    out_lyr = QgsVectorLayer("LineString?crs=EPSG:2163", namestring, "memory")
    out_lyr.startEditing()
    pr = out_lyr.dataProvider()
    pr.addAttributes([QgsField("type", QVariant.String),
                    QgsField("volume", QVariant.Double)])
    out_lyr.updateFields()

    for index, row in pdtb.iterrows():
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromWkt(str(row["Wkt"])))
        fet.setAttributes([row["type"], row["volume"]])
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