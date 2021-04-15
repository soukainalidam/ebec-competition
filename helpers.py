from OSMPythonTools.api import Api
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
import numpy as np


class IWW:
    """
    InWayWay
    A class just to simplify the use of 3-uplets, object way, distance point-crossing point, and crossing coords
    """
    def __init__(self, way_object, distance_to_main_point,  crossing_coords):
        self.obj = way_object
        self.dtm = distance_to_main_point
        self.cc = crossing_coords


class WayP:
    def __init__(self, coords, ltree, unit_vector):
        self.c = coords
        self.ltree = ltree
        self.uv = unit_vector


class Pws:
    def __init__(self, point, l_seg):
        self.c = point
        self.l_seg = l_seg


def geo_to_way_info(lat, long):
    """
    Return some information corresponding to the way in wich the point is: bbox, id, name
    """
    way = Nominatim().query(lat, long, reverse=True, zoom=17)
    JSON = way.toJSON()[0]
    name = JSON ['address']['road']
    bbox = JSON["boundingbox"]
    id = JSON["osm_id"]
    realbbox = [float(bbox[0]), float(bbox[2]), float(bbox[1]) + 0.005, float(bbox[3]) + 0.005]
    return realbbox, id, name


def closest_point_on_way(first_line_list, second_line_list):
    """
    Return the coords of the point where the second line cross the first line
    :param first_line_list: a list of tuples
    :param second_line_list: a list of tuples
    :return: a 2-d np-array
    """
    if len(second_line_list) == 1:
        second_line_list = second_line_list[0]

    if len(first_line_list) == 1:
        first_line_list = first_line_list[0]

    global_min = -1
    local_coords = None
    global_coords = None

    for a, b in first_line_list:
        local_min = -1

        for x, y in second_line_list:
            dist = (a - x) ** 2 + (b - y) ** 2
            if dist < local_min or local_min == -1:
                local_min = dist
                local_coords = (x, y)

        if local_min < global_min or global_min == -1:
            global_min = local_min
            global_coords = local_coords

    return np.array([global_coords[1], global_coords[0]])

