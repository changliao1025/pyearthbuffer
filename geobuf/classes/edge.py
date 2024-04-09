import os
import json
from json import JSONEncoder
import importlib.util
import numpy as np
from osgeo import ogr, gdal, osr
from geographiclib.geodesic import Geodesic
from geobuf.classes.vertex import pyvertex
from geobuf.algorithms.split_by_length import split_edge_by_length
from geobuf.algorithms.find_minimal_enclosing_polygon import find_minimal_enclosing_polygon

iFlag_cython = importlib.util.find_spec("cython") 
if iFlag_cython is not None:
    from pyflowline.algorithms.cython.kernel import calculate_angle_betwen_vertex
    from pyflowline.algorithms.cython.kernel import calculate_distance_to_plane
else:
    from pyearth.gis.geometry.calculate_angle_betwen_vertex import  calculate_angle_betwen_vertex
    from pyearth.gis.geometry.calculate_distance_to_plane import calculate_distance_to_plane

class EdgeClassEncoder(JSONEncoder):
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
          
            
        return JSONEncoder.default(self, obj)

class pyedge(object):
    """The pyedge class

    Args:
        object (object): None

    Returns:
        pyedge: A edge object
    """


    lEdgeID=-1
    lEdgeIndex=-1
    pVertex_start = None
    pVertex_end = None
    dLength=0.0    
    lIndex_upstream=-1
    lIndex_downstream=-1
    pBound=None

    def __init__(self, pVertex_start_in, pVertex_end_in):
        """
        Initilize a pyedge object

        Args:
            pVertex_start_in (pyvertex): The starting vertex
            pVertex_end_in (pyvertex): The ending vertex
        """
        if pVertex_start_in == pVertex_end_in:
            print('The two vertices are the same')    
        else:
            self.pVertex_start = pVertex_start_in
            self.pVertex_end = pVertex_end_in
            self.dLength = self.calculate_length()
            self.calculate_edge_bound()

        return
    
    def calculate_buffer_zone_polygon(self, dRadius, nPoint = 12, sFilename_out=None, sFolder_out=None):
        # Create a geodesic object
        
        pVertex_start = self.pVertex_start
        pVertex_end = self.pVertex_end
        pDriver = ogr.GetDriverByName('GEOJSON')
        
        # Calculate the geodesic buffer  
        aLongitude_degree = []
        aLatitude_degree = []
        ring = ogr.Geometry(ogr.wkbLinearRing)
        aVertex_start = pVertex_start.calculate_buffer_zone_circle(dRadius, nPoint)
        for i in range(nPoint):
            pVertex_buffer0 = aVertex_start[i]
            aLongitude_degree.append(pVertex_buffer0.dLongitude_degree)
            aLatitude_degree.append(pVertex_buffer0.dLatitude_degree)
            ring.AddPoint(pVertex_buffer0.dLongitude_degree, pVertex_buffer0.dLatitude_degree)

        #add the first point to close the ring
        ring.AddPoint( aVertex_start[0].dLongitude_degree, aVertex_start[0].dLatitude_degree) 
        if sFolder_out is not None:
            sFilename_dummy = os.path.join(sFolder_out, 'buffer_zone_start.geojson')
            if os.path.exists(sFilename_dummy):
                os.remove(sFilename_dummy)
            pDS = pDriver.CreateDataSource(sFilename_dummy)
            pLayer = pDS.CreateLayer('buffer_zone', geom_type=ogr.wkbPolygon)
            pArea_field = ogr.FieldDefn('area', ogr.OFTReal)
            pArea_field.SetWidth(20)
            pArea_field.SetPrecision(2)
            pLayer.CreateField(pArea_field)
            pLayerDefn = pLayer.GetLayerDefn()
            pFeature = ogr.Feature(pLayerDefn)     
            pPolygon = ogr.Geometry(ogr.wkbPolygon)        
            pPolygon.AddGeometry(ring)    
            pFeature.SetGeometry(pPolygon)
            dArea = pPolygon.GetArea()
            pFeature.SetField("area", dArea )
            pLayer.CreateFeature(pFeature)
            #close the file
            pDS = None
            pLayer = None
            pFeature = None

        #reset ring
        ring = None
        ring = ogr.Geometry(ogr.wkbLinearRing)
        aVertex_end = pVertex_end.calculate_buffer_zone_circle(dRadius, nPoint)
        for i in range(nPoint):
            pVertex_buffer1 = aVertex_end[i]
            aLongitude_degree.append(pVertex_buffer1.dLongitude_degree)
            aLatitude_degree.append(pVertex_buffer1.dLatitude_degree)
            ring.AddPoint(pVertex_buffer1.dLongitude_degree, pVertex_buffer1.dLatitude_degree)
        ring.AddPoint( aVertex_end[0].dLongitude_degree, aVertex_end[0].dLatitude_degree) 
        if sFolder_out is not None:
            sFilename_dummy = os.path.join(sFolder_out, 'buffer_zone_end.geojson')
            if os.path.exists(sFilename_dummy):
                os.remove(sFilename_dummy)
            pDS = pDriver.CreateDataSource(sFilename_dummy)
            pLayer = pDS.CreateLayer('buffer_zone', geom_type=ogr.wkbPolygon)
            pArea_field = ogr.FieldDefn('area', ogr.OFTReal)
            pArea_field.SetWidth(20)
            pArea_field.SetPrecision(2)
            pLayer.CreateField(pArea_field)
            pLayerDefn = pLayer.GetLayerDefn()
            pFeature = ogr.Feature(pLayerDefn)     
            pPolygon = ogr.Geometry(ogr.wkbPolygon)        
            pPolygon.AddGeometry(ring)    
            pFeature.SetGeometry(pPolygon)
            dArea = pPolygon.GetArea()
            pFeature.SetField("area", dArea )
            pLayer.CreateFeature(pFeature)
            #close the file
            pDS = None
            pLayer = None
            pFeature = None

        #combine them using convex function       

        pPolygon_out = find_minimal_enclosing_polygon(aLongitude_degree, aLatitude_degree)
        #return as a list of vectex is more friendly
        aVertex_out = list()
        for p in pPolygon_out:
            point0= dict()
            point0['dLongitude_degree'] = p[0]
            point0['dLatitude_degree'] = p[1]
            pVertex_out = pyvertex(point0)  
            aVertex_out.append(pVertex_out)
        return aVertex_out
    
    def calculate_edge_bound(self):
        
        dLon_max = np.max( [self.pVertex_start.dLongitude_degree, self.pVertex_end.dLongitude_degree] )
        dLon_min = np.min( [self.pVertex_start.dLongitude_degree, self.pVertex_end.dLongitude_degree] )
        dLat_max = np.max( [self.pVertex_start.dLatitude_degree, self.pVertex_end.dLatitude_degree] )
        dLat_min = np.min( [self.pVertex_start.dLatitude_degree, self.pVertex_end.dLatitude_degree] )
        
        self.pBound = (dLon_min, dLat_min, dLon_max, dLat_max)
        return self.pBound

    def calculate_length(self):
        """
        Calcualate the length of the edge

        Returns:
            float: The length of the edge
        """
        dLength =0.0
        dLength = self.pVertex_start.calculate_distance( self.pVertex_end)
        self.dLength= dLength
        return dLength

    def check_shared_vertex(self, other):
        """
        Check whether two edges are sharing the same vertex

        Args:
            other (pyedge): The other edge object to be checked

        Returns:
            int: Flag, 1: shared; 0: non-sharing
        """
        iFlag_shared = -1
        v0 = self.pVertex_start
        v1 = self.pVertex_end
        v2 = other.pVertex_start
        v3 = other.pVertex_end
        if v0 == v2 or v0 == v3 or v1==v2 or v1==v3:
            iFlag_shared = 1
        else:
            iFlag_shared = 0

        return iFlag_shared
    
    def check_upstream(self, other):
        """
        Check whether another edge is the upstream of current edge

        Args:
            other (pyedge): The other edge object to be checked

        Returns:
            int: Flag, 1: upstream; 0: non-upstream
        """
        iFlag_upstream = -1
        v0 = self.pVertex_start
        v1 = self.pVertex_end
        v2 = other.pVertex_start
        v3 = other.pVertex_end
        if v0 == v3:
            iFlag_upstream =1
        else:
            iFlag_upstream=0

        return iFlag_upstream

    def check_downstream(self, other):
        """
        Check whether another edge is the downstream of current edge


        Args:
            other (pyedge): The other edge object to be checked

        Returns:
            int: Flag, 1: downstream; 0: non-downstream
        """
        iFlag_downstream = -1
        v0 = self.pVertex_start
        v1 = self.pVertex_end
        v2 = other.pVertex_start
        v3 = other.pVertex_end
        if v1 == v2:
            iFlag_downstream =1
        else:
            iFlag_downstream=0

        return iFlag_downstream
    
    def split_by_length(self,dLength_in):
        """
        Split an edge using the threshold

        Args:
            dLength_in (float): The length threshold

        Returns:
            list [pyedge]: A list of edge objects, length of 1 if it meets the requirement
        """
        aEdge_out=list()
        if self.dLength <=aEdge_out:
            aEdge_out.append(self)
        else:
            #find location from up to down
            aEdge_out = split_edge_by_length(self, dLength_in)
            pass
        return aEdge_out

    def reverse(self):
        """
        Reverse an edge
        """
        v0 = self.pVertex_start
        v1 = self.pVertex_end
        self.pVertex_start = v1
        self.pVertex_end = v0
        return
    
    def is_overlap(self, pEdge_in):
        """
        Check if two edges overlap each other

        Args:
            pEdge_in (pyedge): The other edge to be checked

        Returns:
            int: 1 if overlap; 0 if not
        """
        iFlag_overlap = 0
        pVertex_start1 = self.pVertex_start
        pVertex_end1 = self.pVertex_end
        pVertex_start2 = pEdge_in.pVertex_start
        pVertex_end2 = pEdge_in.pVertex_end

        if pVertex_start1 == pVertex_start2 and pVertex_end1 == pVertex_end2:
            iFlag_overlap = 1
        else:
            if  pVertex_start1 == pVertex_end2 and pVertex_end1 == pVertex_start2:
                iFlag_overlap = 1
            else:
                iFlag_overlap = 0

        return iFlag_overlap

    def check_vertex_on_edge(self, pVertex_in):
        """
        Check if a vertex on an edge

        Args:
            pVertex_in (pyvertex): The vertex to be checked

        Returns:
            tuple[int, float, float]: 1 if it is on; 0 if not. Length and distance are calculated if on.
        """
        iFlag =0 
        dDistance = -1
        dDistance_plane = 9999
        pVertex_start = self.pVertex_start
        pVertex_end = self.pVertex_end
        self.dLength = pVertex_start.calculate_distance(pVertex_end)
        if pVertex_in != pVertex_start and pVertex_in!=pVertex_end:
            d1 = pVertex_start.calculate_distance(pVertex_in)            
            d2 = pVertex_end.calculate_distance(pVertex_in)  
            d3 = d1 + d2 - self.dLength
            angle3deg = calculate_angle_betwen_vertex(\
                 pVertex_start.dLongitude_degree, pVertex_start.dLatitude_degree,\
                 pVertex_in.dLongitude_degree, pVertex_in.dLatitude_degree,\
                 pVertex_end.dLongitude_degree,pVertex_end.dLatitude_degree)

            dDistance_plane = calculate_distance_to_plane(\
                 pVertex_start.dLongitude_degree, pVertex_start.dLatitude_degree,\
                 pVertex_in.dLongitude_degree, pVertex_in.dLatitude_degree,\
                 pVertex_end.dLongitude_degree,pVertex_end.dLatitude_degree)
            #lons = [pVertex_start.dLongitude_degree,pVertex_in.dLongitude_degree,pVertex_end.dLongitude_degree]
            #lats = [pVertex_start.dLatitude_degree, pVertex_in.dLatitude_degree, pVertex_end.dLatitude_degree]
            #dArea = calculate_polygon_area(lons, lats)

            if  angle3deg > 178 and d3 < 1.0: #care
                iFlag = 1
                dDistance = d1
            else:
                iFlag = 0
            
        else:
            iFlag = 0 

        return iFlag, dDistance, dDistance_plane
    
    def __eq__(self, other):
        """
        Check if two edges are equivalent

        Args:
            other (pyedge): The other edge
            how about direction?

        Returns:
            int: 1 if equivalent; 0 if not
        """
        return int( self.pVertex_start == other.pVertex_start and self.pVertex_end == other.pVertex_end )

    def __ne__(self, other):
        """
        Check if two edges are equivalent

        Args:
            other (pyedge): The other edge

        Returns:
            int: 0 if equivalent; 1 if not
        """
        return not self.__eq__(other)

    def tojson(self):
        """
        Convert an edge object to a json string

        Returns:
            json str: A json string
        """

        obj = self.__dict__.copy()
        
        sJson = json.dumps(obj, \
            sort_keys=True, \
                indent = 4, \
                    ensure_ascii=True, \
                        cls=EdgeClassEncoder)
        return sJson

