from flowmapper.core.treebuilder import buildTree
from flowmapper.core.drawer import pptr, thcktr
from flowmapper.core import plotting

try:
    """
    For correct access of @qgsfunction decorated methods from QGIS expression builder
    it is critically important to run flowmapper.io.apiqis module at least once
    """
    from flowmapper.io.apiqgis import flowTreeBuildAction
except ModuleNotFoundError:
    print("\nUnable to import QGIS Python API\n")