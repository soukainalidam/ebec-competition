from OSMPythonTools.api import Api
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
import numpy as np

def geo_to_address(lat, long):
    return Nominatim().query(lat, long, reverse=True, zoom=20)


def geo_to_way_info(lat, long):
    way = Nominatim().query(lat, long, reverse=True, zoom=17)
    JSON = way.toJSON()[0]
    name = JSON ['address']['road']
    bbox = JSON["boundingbox"]
    id = JSON["osm_id"]
    realbbox = [float(bbox[0]), float(bbox[2]), float(bbox[1]) + 0.005, float(bbox[3]) + 0.005]
    return realbbox, id, name


def closest_point_on_way(first_line_list, second_line_list):
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




class IWW:
    def __init__(self, way_object, distance_to_main_road,  crossing_coords):
        self.obj = way_object
        self.dtm = distance_to_main_road
        self.cc = crossing_coords


def segment(long, lat):

    point = np.array([long, lat])
    bbox, id, name = geo_to_way_info(long, lat)
    query = overpassQueryBuilder(bbox=bbox, elementType=['way'], selector=['highway', 'name'], includeGeometry=True)
    result = Overpass().query(query)
    for x in result.elements():
        if x.id() == id:
            closet_road = x

    IWW_list = []
    for x in result.elements():
        print(x.tags()['name'])
        if x.id() != id and x.tags()['name'] != name:
            cc = closest_point_on_way(closet_road.geometry()["coordinates"], x.geometry()["coordinates"])
            dtm = np.linalg.norm(point-cc)
            IWW_list.append(IWW(x, dtm, cc))

    IWW_list.sort(key=lambda x: x.dtm)
    result1 = IWW_list[0]

    for iww in IWW_list:
        if iww.obj.id() != id and iww.obj != result1.obj:

            if np.dot(result1.cc-point, iww.cc-point) < 0:
                result2 = iww
                break
    print(result1.obj.tags(), result2.obj.tags())


segment(43.60160410486647, 1.4505549320362405)

