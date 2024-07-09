
import os
import copy
import json
from json import JSONEncoder
import numpy as np
from osgeo import ogr, gdal, osr
import alphashape

from gcsbuffer.classes.vertex import pyvertex
from gcsbuffer.classes.edge import pyedge
from gcsbuffer.algorithms.find_minimal_enclosing_polygon import find_minimal_enclosing_polygon
from gcsbuffer.formats.save_vertex_as_polygon import save_vertex_as_polygon

class PolygonClassEncoder(JSONEncoder):
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

class pypolygon(object):
    """The pyflowline class

    Args:
        object (object): None

    Returns:
        pyflowline: The flowline object
    """

    lPolygonID=-1
    lPolygonIndex=-1


    pVertex_start=None
    pVertex_end=None
    aEdge=None
    aVertex=None

    dLength=0.0

    iStream_segment=-1
    iStream_order = -1

    nEdge=0
    nVertex=0
    iFlag_right = 0
    iFlag_left = 0

    #for stream topology

    pBound=None

    def __init__(self, aEdge):
        """
        Initilize a polygon object

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

        self.calculate_polygon_bound()

        return

    def __hash__(self):
        return hash((self.pVertex_start, self.pVertex_end))

    def calculate_buffer_zone_polygon(self, dRadius, sFilename_out = None, sFolder_out=None):
        """
        Calculate the buffer zone polygon

        Args:
            dRadius (float): The buffer zone distance

        Returns:
            list: A list of buffer zone points
        """
        aVertex_out = list()
        aLongitude_degree = list()
        aLatitude_degree = list()
        aVertex_2d = list()
        for i in range(self.nEdge):
            edge = self.aEdge[i]
            aVertex, aVertex_center, aVertex_circle = edge.calculate_buffer_zone_polygon(dRadius)
            for pVertex in aVertex:
                aLongitude_degree.append(pVertex.dLongitude_degree)
                aLatitude_degree.append(pVertex.dLatitude_degree)
                aVertex_2d.append([pVertex.dLongitude_degree, pVertex.dLatitude_degree])

            for pVertex in aVertex_center:
                aLongitude_degree.append(pVertex.dLongitude_degree)
                aLatitude_degree.append(pVertex.dLatitude_degree)
                aVertex_2d.append([pVertex.dLongitude_degree, pVertex.dLatitude_degree])

            for pVertex in aVertex_circle:
                aLongitude_degree.append(pVertex.dLongitude_degree)
                aLatitude_degree.append(pVertex.dLatitude_degree)
                aVertex_2d.append([pVertex.dLongitude_degree, pVertex.dLatitude_degree])

            #save out for debug
            if sFolder_out is not None:
                sFilename_dummy= os.path.join(sFolder_out, 'buffer_zone_edge_%d.geojson' % i)
                save_vertex_as_polygon(aVertex, sFilename_dummy)

        aVertex_2d = np.array(aVertex_2d)
        pPolygon_out = alphashape.alphashape(aVertex_2d, 2.0)
        #return as a list of vectex is more friendly
        aVertex_out = list()
        for dLongtitude, dLatitude in pPolygon_out.exterior.coords:
            point0= dict()
            point0['dLongitude_degree'] = dLongtitude
            point0['dLatitude_degree'] = dLatitude
            pVertex_out = pyvertex(point0)
            aVertex_out.append(pVertex_out)
        if sFilename_out is not None:
            save_vertex_as_polygon(aVertex_out, sFilename_out)

        pPolygon_out = alphashape.alphashape(aVertex_2d, 0.0)
        aVertex_dummy = list()
        for dLongtitude, dLatitude in pPolygon_out.exterior.coords:
            point0= dict()
            point0['dLongitude_degree'] = dLongtitude
            point0['dLatitude_degree'] = dLatitude
            pVertex_out = pyvertex(point0)
            aVertex_dummy.append(pVertex_out)
        if sFilename_out is not None:
            sFilename_dummy = sFilename_out.replace('.geojson', '_convex_hull.geojson')
            save_vertex_as_polygon(aVertex_dummy, sFilename_dummy)

        return aVertex_out

    def calculate_length(self):
        """
        Calcualte the length

        Returns:
            float: The length of the flowline
        """



        self.dLength = sum(edge.dLength for edge in self.aEdge)
        return self.dLength

    def calculate_polygon_bound(self):
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


    def __eq__(self, other):
        """
        Check whether two flowline are equivalent

        Args:
            other (pyflowline): The other flowline

        Returns:
            int: 1 if equivalent, 0 if not
        """
        if len(self.aEdge) != len(other.aEdge):
            return 0

        return int(all(edge1 == edge2 for edge1, edge2 in zip(self.aEdge, other.aEdge)))

    def __ne__(self, other):
        """
        Check whether two flowline are equivalent

        Args:
            other (pyflowline): The other flowline

        Returns:
            int: 0 if equivalent, 1 if not
        """
        return not self.__eq__(other)

    def tojson(self):
        """
        Convert a pyflowline object to a json string

        Returns:
            json str: A json string
        """
        aSkip = ['aEdge',
                'aVertex','aPolygonID_start_start','aPolygonID_start_end',
                'aPolygonID_end_start','aPolygonID_end_end']

        obj = self.__dict__.copy()
        for sKey in aSkip:
            obj.pop(sKey, None)
            pass


        sJson = json.dumps(obj,
            sort_keys=True,
                indent = 4,
                    ensure_ascii=True,
                        cls=PolygonClassEncoder)
        return sJson
