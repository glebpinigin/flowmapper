from ..treebuilder.treebuilder import buildTree
from ..treebuilder.spiraltree import connectionsToWkt, spiraltreeToPandas
from qgis.core import QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsCoordinateTransformContext, QgsVectorFileWriter, QgsProject
from qgis.PyQt.QtCore import QVariant

def do(iface, path):
    T = input(iface)
    out_lyr = output(T)
    write(out_lyr, path)


def input(iface):
    lyr = iface.activeLayer()
    lyr.selectByExpression('"name"=\'Texas\'', QgsVectorLayer.SetSelection)
    root = lyr.selectedFeatures()[0]
    rootpt = root.geometry().asPoint()
    root_x = rootpt.x()
    root_y = rootpt.y()
    bias = (root_x, root_y)
    lyr.selectByExpression('"name"!=\'Texas\'', QgsVectorLayer.SetSelection)
    other = lyr.selectedFeatures()

    leaves = []
    for feature in other:
        geom = feature.geometry()
        pt = geom.asPoint()
        x = pt.x() - root_x
        y = pt.y() - root_y
        leaves.append((x, y))

    T = buildTree(leaves=leaves, bias=bias)
    connectionsToWkt(T)
    return T


def output(T):
    pdtb = spiraltreeToPandas(T)
    out_lyr = QgsVectorLayer("lines", "out_lines", "memory")
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
    # QgsProject.instance().addMapLayer(out_lyr)
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