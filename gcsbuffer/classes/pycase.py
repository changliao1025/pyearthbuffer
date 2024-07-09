import os
from pathlib import Path
import json
from json import JSONEncoder
import datetime
import importlib.util
from shutil import copy2
import numpy as np
from osgeo import ogr, osr, gdal

from pyearth.system.define_global_variables import *
from pyearth.toolbox.data.geoparquet.convert_geojson_to_geoparquet import convert_geojson_to_geoparquet

from gcsbuffer.classes.timer import pytimer
from gcsbuffer.classes.vertex import pyvertex
from gcsbuffer.classes.flowline import pyflowline
from gcsbuffer.classes.edge import pyedge

iFlag_kml = importlib.util.find_spec("simplekml")
iFlag_cython = importlib.util.find_spec("cython")
if iFlag_cython is not None:
    from tinyr import RTree
    iFlag_use_rtree = 1
else:
    iFlag_use_rtree =0
    pass

gdal.UseExceptions()
pDate = datetime.datetime.today()
sDate_default = "{:04d}".format(pDate.year) + "{:02d}".format(pDate.month) + "{:02d}".format(pDate.day)

class CaseClassEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.float32):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, list):
            pass
        if isinstance(obj, pyvertex):
            return json.loads(obj.tojson())
        if isinstance(obj, pyedge):
            return obj.lEdgeID
        if isinstance(obj, pyflowline):
            return obj.lFlowlineID


        return JSONEncoder.default(self, obj)

class flowlinecase(object):
    """
    The flowline case class

    Args:
        object (obj): None

    Returns:
        flowlinecase: A flowlinecase object
    """
    iCase_index= 0

    sMesh_type = 1
    iFlag_standalone=1
    iFlag_flowline = 1
    iFlag_global = 0
    iFlag_antarctic = 0
    iFlag_multiple_outlet = 0
    iFlag_mesh_boundary = 0
    #iFlag_use_shapefile_extent=1
    iFlag_use_mesh_dem=0
    iFlag_save_mesh = 0
    iFlag_simplification = 1 #user can turn on/off
    iFlag_create_mesh=1
    iFlag_intersect = 1
    iFlag_rotation=0
    iFlag_break_by_distance = 0  #if the distance between two vertice are far,
    iResolution_index = 10
    iFlag_dggrid = 0
    nOutlet = 1 #by default , there shoule ne only one ouelet
    dResolution_degree=0.0
    dResolution_meter=0.0
    dThreshold_small_river=0.0
    dThreshold_break_by_distance = 5000.0
    dLongitude_left = -180
    dLongitude_right = 180
    dLatitude_bot = -90
    dLatitude_top = 90
    dElevation_mean=-9999.0
    sFilename_model_configuration=''
    sFilename_mesh_boundary = ''
    sWorkspace_input=''
    sWorkspace_output=''
    #sWorkspace_output_case=''
    sRegion=''
    sModel=''
    sMesh_type ='hexagon'
    sDggrid_type = 'ISEA3H'

    sCase=''
    sDate=''

    sFilename_dggrid=''

    sFilename_spatial_reference=''
    sFilename_dem=''

    sFilename_mesh=''
    sFilename_mesh_info=''
    sFilename_mesh_netcdf=''
    sFilename_mesh_kml=''

    aBasin = list()
    aFlowline_simplified=list()
    aFlowline_conceptual=list()
    aCellID_outlet = list()
    aCell=list()

    pRTree_mesh = None #only when rtree is used

    iFlag_visual = importlib.util.find_spec("cartopy")
    if iFlag_visual is not None:
        pass
    else:
        pass

    from ._hpc import _gcsbuffer_create_hpc_job

    def __init__(self, aConfig_in,
                 iFlag_standalone_in= None,
                 sModel_in = None,
                 sDate_in = None,
                 sWorkspace_output_in = None):
        """
        Initialize a flowlinecase object

        Args:
            aConfig_in (dict): A dictionary of parameters
            iFlag_standalone_in (int, optional): Flag for whether run the case standalone. Defaults to None.
            sModel_in (str, optional): The model name. Defaults to None.
            sDate_in (str, optional): The case date. Defaults to None.
            sWorkspace_output_in (str, optional): The output workspace. Defaults to None.
        """
        #flags
        if iFlag_standalone_in is not None:
            self.iFlag_standalone = iFlag_standalone_in
        else:
            if 'iFlag_standalone' in aConfig_in:
                self.iFlag_standalone = int(aConfig_in['iFlag_standalone'])
            else:
                self.iFlag_standalone=1


        if 'iFlag_flowline' in aConfig_in:
            self.iFlag_flowline             = int(aConfig_in[ 'iFlag_flowline'])
        else:
            #without iFlag_flowline the model is a mesh generator
            self.iFlag_flowline=1

        if 'iFlag_global' in aConfig_in:
            self.iFlag_global             = int(aConfig_in[ 'iFlag_global'])

        if 'iFlag_antarctic' in aConfig_in:
            self.iFlag_antarctic             = int(aConfig_in[ 'iFlag_antarctic'])

        if 'iFlag_mesh_boundary' in aConfig_in:
            self.iFlag_mesh_boundary             = int(aConfig_in[ 'iFlag_mesh_boundary'])
        else:
            self.iFlag_mesh_boundary=0

        if 'iFlag_multiple_outlet' in aConfig_in:
            self.iFlag_multiple_outlet             = int(aConfig_in[ 'iFlag_multiple_outlet'])

        if 'iFlag_simplification' in aConfig_in:
            self.iFlag_simplification = int(aConfig_in['iFlag_simplification'])
            #if simplification is desired, then we must activate flowline flag
            #it can be turn off only when a previous simplification was done and you dont want to redo it
        else:
            self.iFlag_simplification  = 1
        if self.iFlag_simplification ==1:
            self.iFlag_flowline = 1

        if 'iFlag_create_mesh' in aConfig_in:
            self.iFlag_create_mesh = int(aConfig_in['iFlag_create_mesh'])
        else:
            self.iFlag_create_mesh=1

        if 'iFlag_save_mesh' in aConfig_in:
            self.iFlag_save_mesh             = int(aConfig_in[ 'iFlag_save_mesh'])

        if 'iFlag_use_mesh_dem' in aConfig_in:
            self.iFlag_use_mesh_dem = int(aConfig_in['iFlag_use_mesh_dem'])

        #if 'iFlag_use_shapefile_extent' in aConfig_in:
        #    self.iFlag_use_shapefile_extent = int(aConfig_in['iFlag_use_shapefile_extent'])

        if 'iFlag_rotation' in aConfig_in:
            self.iFlag_rotation = int(aConfig_in['iFlag_rotation'])


        if 'iFlag_intersect' in aConfig_in:
            self.iFlag_intersect = int(aConfig_in['iFlag_intersect'])
        else:
            self.iFlag_intersect=1

        if self.iFlag_flowline == 1:
            pass
        else:
            self.iFlag_intersect=0

        if 'iFlag_break_by_distance' in aConfig_in:
            self.iFlag_break_by_distance = int(aConfig_in['iFlag_break_by_distance'])
        else:
            self.iFlag_break_by_distance=0

        if 'iFlag_dggrid' in aConfig_in:
            self.iFlag_dggrid = int(aConfig_in['iFlag_dggrid'])
        else:
            self.iFlag_dggrid=0

        if 'iResolution_index' in aConfig_in:
            self.iResolution_index = int(aConfig_in['iResolution_index'])
        else:
            self.iResolution_index=10

        if 'sDggrid_type' in aConfig_in:
            self.sDggrid_type = aConfig_in['sDggrid_type']
        else:
            self.sDggrid_type='ISEA3H'

        if 'nOutlet' in aConfig_in:
            self.nOutlet = int(aConfig_in['nOutlet'])

        if 'iCase_index' in aConfig_in:
            iCase_index = int(aConfig_in['iCase_index'])
        else:
            iCase_index = 1

        sCase_index = "{:03d}".format( iCase_index )
        self.iCase_index =   iCase_index

        if 'dResolution_degree' in aConfig_in:
            self.dResolution_degree = float(aConfig_in['dResolution_degree'])

        if 'dResolution_meter' in aConfig_in:
            self.dResolution_meter = float(aConfig_in['dResolution_meter'])
        else:
            print('Please specify resolution.')



        if 'dThreshold_break_by_distance' in aConfig_in:
            self.dThreshold_break_by_distance = float(aConfig_in['dThreshold_break_by_distance'])

        if 'dLongitude_left' in aConfig_in:
            self.dLongitude_left = float(aConfig_in['dLongitude_left'])

        if 'dLongitude_right' in aConfig_in:
            self.dLongitude_right = float(aConfig_in['dLongitude_right'])

        if 'dLatitude_bot' in aConfig_in:
            self.dLatitude_bot = float(aConfig_in['dLatitude_bot'])

        if 'dLatitude_top' in aConfig_in:
            self.dLatitude_top = float(aConfig_in['dLatitude_top'])

        if 'sFilename_model_configuration' in aConfig_in:
            self.sFilename_model_configuration    = aConfig_in[ 'sFilename_model_configuration']

        if 'sFilename_mesh_boundary' in aConfig_in:
            self.sFilename_mesh_boundary    = aConfig_in[ 'sFilename_mesh_boundary']

            if self.iFlag_mesh_boundary==1:
                if not os.path.isfile(self.sFilename_mesh_boundary ):
                    print("The mesh boundary file does not exist, you should update this parameter before running the model!")
                    #exit()
                pass

        if 'sFilename_spatial_reference' in aConfig_in:
            self.sFilename_spatial_reference = aConfig_in['sFilename_spatial_reference']


        if 'sFilename_dem' in aConfig_in:
            self.sFilename_dem = aConfig_in['sFilename_dem']

        if self.iFlag_dggrid == 1:
            if 'sFilename_dggrid' in aConfig_in:
                self.sFilename_dggrid = aConfig_in['sFilename_dggrid']
                if not os.path.isfile(self.sFilename_dggrid ):
                    print("The dggrid binary file does not exist, you need to update this parameter before running the model!")
                    exit()
                pass

            else:
                print('Please specify the dggrid binary file.')
                exit()

        if 'sFilename_mesh_netcdf' in aConfig_in:
            self.sFilename_mesh_netcdf = aConfig_in['sFilename_mesh_netcdf']

        if 'sWorkspace_bin' in aConfig_in:
            self.sWorkspace_bin= aConfig_in[ 'sWorkspace_bin']

        if 'sWorkspace_input' in aConfig_in:
            self.sWorkspace_input = aConfig_in[ 'sWorkspace_input']


        if sWorkspace_output_in is not None:
            self.sWorkspace_output = sWorkspace_output_in
        else:
            if 'sWorkspace_output' in aConfig_in:
                self.sWorkspace_output = aConfig_in[ 'sWorkspace_output']

        if 'sJob' in aConfig_in:
            self.sJob =  aConfig_in['sJob']
        if 'sRegion' in aConfig_in:
            self.sRegion               = aConfig_in[ 'sRegion']

        if sModel_in is not None:
            self.sModel = sModel_in
        else:
            if 'sModel' in aConfig_in:
                self.sModel                = aConfig_in[ 'sModel']


        sDate   = aConfig_in[ 'sDate']
        if sDate is not None:
            self.sDate= sDate
        else:
            self.sDate = sDate_default


        sCase = self.sModel  + self.sDate + sCase_index
        self.sCase = sCase

        if 'sMesh_type' in aConfig_in:
            self.sMesh_type =  aConfig_in['sMesh_type']
        else:
            self.sMesh_type = 'hexagon'



        sMesh_type = self.sMesh_type
        if sMesh_type =='hexagon': #hexagon
            self.iMesh_type = 1
        else:
            if sMesh_type =='square': #square
                self.iMesh_type = 2
            else:
                if sMesh_type =='latlon': #latlon
                    self.iMesh_type = 3
                else:
                    if sMesh_type =='mpas': #mpas
                        self.iMesh_type = 4
                    else:
                        if sMesh_type =='dggrid':
                            self.iMesh_type = 5
                        else:
                            if sMesh_type =='tin': #
                                self.iMesh_type = 6
                            else:
                                print('Unsupported mesh type?')


        #the model can be run as part of hexwatershed or standalone
        if self.iFlag_standalone == 1:
            #in standalone case, will add case information and update output path
            sPath = str(Path(self.sWorkspace_output)  /  sCase)
            self.sWorkspace_output = sPath
        else:
            #use specified output path, also do not add output or input tag
            sPath = self.sWorkspace_output

        Path(sPath).mkdir(parents=True, exist_ok=True)






    def gcsbuffer_analyze(self):
        """
        Analyze the domain results for every watershed
        """

        return

    def gcsbuffer_setup(self):


        return

    def gcsbuffer_change_model_parameter(self, sVariable_in, dValue, iFlag_basin_in = None):
        if iFlag_basin_in is None:
            if hasattr(self, sVariable_in):
                #get default data type
                sType_default = type(getattr(self, sVariable_in))
                #get the data type of the input value
                sType_input = type(dValue)
                if sType_default == sType_input:
                    setattr(self, sVariable_in, dValue)
                    pass
                else:
                    print('Incorrect data type for the input value: ' + sVariable_in)
                return True
            else:
                print("This model parameter is unknown, please check the full parameter list in the documentation: " + sVariable_in)
                return False



        else:
            #this mean the variable is in the basin object
            pass

    def gcsbuffer_run(self):
        """
        Run the flowlinecase simulation

        Returns:
            list: A list of cell objects
        """


        return

    def gcsbuffer_evaluate(self):
        """
        Evaluate the model performance
        """

        return

    def gcsbuffer_export(self):
        """
        Export the model outputs
        """
        print('gcsbuffer started export results')
        ptimer = pytimer()
        ptimer.start()

        ptimer.stop()
        return



    def tojson(self):
        """
        Convert the flowline case object to a json string

        Returns:
            json str: A json string
        """
        aSkip = ['aBasin', \
                 'aFlowline_simplified','aFlowline_conceptual','aCellID_outlet',
                 'aCell', 'pRTree_mesh']

        obj = self.__dict__.copy()
        for sKey in aSkip:
            obj.pop(sKey, None)
            pass

        sJson = json.dumps(obj,\
                               sort_keys=True, \
                               indent = 4, \
                               ensure_ascii=True, \
                               cls=CaseClassEncoder)
        return sJson

    def gcsbuffer_print(self):
        """
        Print the flowline case object
        """
        print(self.tojson())
        return

    def gcsbuffer_export_config_to_json(self, sFilename_output_in = None):
        """
        Export the configuration to a json file

        Args:
            sFilename_output_in (str, optional): The json filename. Defaults to None.
        """


        return

    def gcsbuffer_export_basin_config_to_json(self, sFilename_output_in= None):
        """
        Export the member basin configuration to a json file

        Args:
            sFilename_output_in (str, optional): The json filename. Defaults to None.
        """


        return
