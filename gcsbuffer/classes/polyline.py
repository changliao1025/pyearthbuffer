
import os
import copy
import json
from json import JSONEncoder
import numpy as np
from osgeo import ogr, gdal, osr

from gcsbuffer.classes.vertex import pyvertex
from gcsbuffer.classes.edge import pyedge
from gcsbuffer.formats.save_vertex_as_polygon import save_vertex_as_polygon

class PolylineClassEncoder(JSONEncoder):
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

        return JSONEncoder.default(self, obj)

class pypolyline(object):
    """The pypolyline class

    Args:
        object (object): None

    Returns:
        pypolyline: The polyline object
    """

    lPolylineID=-1
    lPolylineIndex=-1
    lIndex_upstream=-1
    lIndex_downstream=-1

    iFlag_dam = 0
    lNHDPlusID=-1

    pVertex_start=None
    pVertex_end=None
    aEdge=None
    aVertex=None

    dLength=0.0
    dSinuosity=0.0

    iStream_segment=-1
    iStream_order = -1

    nEdge=0
    nVertex=0
    iFlag_right = 0
    iFlag_left = 0
    aPolylineID_start_start = None
    aPolylineID_start_end = None
    aPolylineID_end_start = None
    aPolylineID_end_end = None

    #for stream topology
    lPolyline_downstream = None #only store the index, not the actual objects
    aPolyline_upstream = None #only store the index, not the actual objects

    pBound=None

    def __init__(self, aEdge):
        """
        Initilize a polyline object

        Args:
            aEdge (list [pyedge]): A list of edge objects
        """
        self.aEdge = aEdge
        nEdge = len(aEdge)
        self.nEdge = nEdge
        self.pVertex_start = aEdge[0].pVertex_start
        self.pVertex_end =  aEdge[ nEdge-1  ].pVertex_end
        nVertex = nEdge +1
        self.aVertex=list()
        for i in range(nEdge):
            self.aVertex.append( aEdge[i].pVertex_start )
            pass

        self.aVertex.append( aEdge[nEdge-1].pVertex_end )
        self.nVertex = nVertex
        self.dLength= self.calculate_length()
        self.aPolylineID_start_start = list()
        self.aPolylineID_start_end = list()
        self.aPolylineID_end_start = list()
        self.aPolylineID_end_end = list()

        self.calculate_polyline_bound()

        return

    def __hash__(self):
        return hash((self.pVertex_start, self.pVertex_end))

    def calculate_buffer_zone(self, dRadius, sFilename_out = None, sFolder_out=None):
        """
        Calculate the buffer zone polygon

        Args:
            dRadius (float): The buffer zone distance

        Returns:
            list: A list of buffer zone points
        """
        pMultiPolygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for i in range(self.nEdge):
            edge = self.aEdge[i]
            sWkt = edge.calculate_buffer_zone(dRadius)
            pPolygon =  ogr.CreateGeometryFromWkt(sWkt)
            # Add the polygon to the MultiPolygon
            pMultiPolygon.AddGeometry(pPolygon)
            #save out for debug
            if sFolder_out is not None:
                sFilename_dummy= os.path.join(sFolder_out, 'buffer_zone_edge_%d.geojson' % i)
                pass

        pUnionPolygon = pMultiPolygon.UnionCascaded()
        sWkt = pUnionPolygon.ExportToWkt()
        if sFilename_out is not None:
            #save_vertex_as_polygon(aVertex_out, sFilename_out)
            pass
        return sWkt

    def calculate_length(self):
        """
        Calcualte the length

        Returns:
            float: The length of the polyline
        """
        #dLength =0.0
        #loop though
        #for i in range(self.nEdge):
        #for edge in self.aEdge:
        #    self.aEdge[i].calculate_length()
        #    dLength = dLength + self.aEdge[i].dLength

        #assing
        #self.dLength= dLength


        self.dLength = sum(edge.dLength for edge in self.aEdge)
        return self.dLength

    def calculate_polyline_bound(self):
        dLat_min = 90
        dLat_max = -90
        dLon_min = 180
        dLon_max = -180
        for i in range(self.nVertex):
            dLon_max = np.max( [dLon_max, self.aVertex[i].dLongitude_degree] )
            dLon_min = np.min( [dLon_min, self.aVertex[i].dLongitude_degree] )
            dLat_max = np.max( [dLat_max, self.aVertex[i].dLatitude_degree] )
            dLat_min = np.min( [dLat_min, self.aVertex[i].dLatitude_degree] )

        self.pBound = (dLon_min, dLat_min, dLon_max, dLat_max)
        return self.pBound

    def check_upstream(self, other):
        """
        Check whether another polyline is upstream or not

        Args:
            other (pypolyline): The other polyline

        Returns:
            int: 1 if it is, 0 if not
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
        Check whether another polyline is downstream or not

        Args:
            other (pypolyline): The other polyline

        Returns:
            int: 1 if it is, 0 if not
        """
        iFlag_downstream =-1
        v0 = self.pVertex_start
        v1 = self.pVertex_end
        v2 = other.pVertex_start
        v3 = other.pVertex_end
        if v1 == v2:
            iFlag_downstream =1
        else:
            iFlag_downstream=0

        return iFlag_downstream

    def reverse(self):
        """
        Reverse a polyline
        """
        aVertex = self.aVertex
        nVertex = self.nVertex
        aVertex_new = list()
        for i in range(nVertex-1,-1,-1) :
            aVertex_new.append( aVertex[i] )

        self.aVertex = aVertex_new
        nVertex  = len(aVertex)
        aEdge = list()
        for i in range(nVertex-1):
            pEdge = pyedge( self.aVertex[i], self.aVertex[i+1] )
            aEdge.append(pEdge)
            pass

        self.aEdge = aEdge
        nEdge = len(aEdge)
        self.pVertex_start = aEdge[0].pVertex_start
        self.pVertex_end =  aEdge[ nEdge-1  ].pVertex_end

    def merge_upstream(self, other):
        """
        Merge two polylines as one

        Args:
            other (pypolyline): The other polyline

        Returns:
            pypolyline: The merged polyline
        """
        pPolyline_out = copy.deepcopy(other)

        iFlag_dam1 = other.iFlag_dam
        pVertex_start1 = other.pVertex_start
        pVertex_end1 = other.pVertex_end
        nVertex1 = other.nVertex
        nEdge1 = other.nEdge

        pVertex_start2 = self.pVertex_start
        pVertex_end2 = self.pVertex_end
        nVertex2 = self.nVertex
        nEdge2 = self.nEdge
        iFlag_dam2 = self.iFlag_dam


        if pVertex_end1 == pVertex_start2:
            #this is the supposed operation because they should connect

            nVertex = nVertex1 + nVertex2 - 1
            nEdge = nVertex -1
            aEdge = copy.deepcopy(other.aEdge )
            for i in range(nEdge2):
                aEdge.append( self.aEdge[i] )
                pass

            aVertex = copy.deepcopy(other.aVertex)
            for i in range(1, nVertex2):
                aVertex.append( self.aVertex[i] )
                pass

            pPolyline_out.iFlag_dam = max(iFlag_dam1, iFlag_dam2)
            pPolyline_out.aEdge = aEdge
            pPolyline_out.aVertex = aVertex
            pPolyline_out.nEdge = nEdge
            pPolyline_out.nVertex = nVertex
            pPolyline_out.dLength = self.dLength + other.dLength
            pPolyline_out.pVertex_start = pVertex_start1
            pPolyline_out.pVertex_end = pVertex_end2
            pass
        else:
            pass

        #is this necessary
        #pPolyline_out.iStream_segment = self.iStream_segment

        return pPolyline_out

    def split_edge_by_length(self, dDistance):
        """
        Split a polyline using the length threshold

        Args:
            dDistance (float): The length threshold for each edge

        Returns:
            pypolyline: The updated polyline
        """
        aEdge=list()
        pPolyline_out=None
        for edge in self.aEdge:
            #edge.calculate_length()
            if edge.dLength > dDistance:
                #break it
                aEdge0=edge.split_by_length(dDistance)
                for edge0 in aEdge0:
                    aEdge.append(edge0)
                pass
            else:
                aEdge.append(edge)
                pass
        pPolyline_out=pypolyline(aEdge)
        return pPolyline_out

    def calculate_polyline_sinuosity(self):
        """
        Calculate the sinuosoty of a polyline
        """
        pVertex_start = self.pVertex_start
        pVertex_end = self.pVertex_end
        dDistance = pVertex_start.calculate_distance(pVertex_end)
        self.dSinuosity = self.dLength / dDistance
        return

    def __eq__(self, other):
        """
        Check whether two polylines are equivalent

        Args:
            other (pypolyline): The other polyline

        Returns:
            int: 1 if equivalent, 0 if not
        """
        if len(self.aEdge) != len(other.aEdge):
            return 0

        return int(all(edge1 == edge2 for edge1, edge2 in zip(self.aEdge, other.aEdge)))

    def __ne__(self, other):
        """
        Check whether two polylines are equivalent

        Args:
            other (pypolyline): The other polyline

        Returns:
            int: 0 if equivalent, 1 if not
        """
        return not self.__eq__(other)

    def tojson(self):
        """
        Convert a pypolyline object to a json string

        Returns:
            json str: A json string
        """
        aSkip = ['aEdge',
                'aVertex','aPolylineID_start_start','aPolylineID_start_end',
                'aPolylineID_end_start','aPolylineID_end_end']

        obj = self.__dict__.copy()
        for sKey in aSkip:
            obj.pop(sKey, None)
            pass


        sJson = json.dumps(obj,
            sort_keys=True,
                indent = 4,
                    ensure_ascii=True,
                        cls=PolylineClassEncoder)
        return sJson
