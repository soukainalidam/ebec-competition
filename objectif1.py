from OSMPythonTools.api import Api
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
import numpy as np
from helpers import *

def segment(lat, long):
    """
    Main function defining the segment in wich the point is
    :param long: coords
    :param lat: coords
    :return: two way-objects such as our point is in between these two ways, and the road between them, and the main road
    (for later uses)
    """
    long, lat = lat, long
    point = np.array([long, lat])
    bbox, id, name = geo_to_way_info(long, lat)
    query = overpassQueryBuilder(bbox=bbox, elementType=['way'], selector=['highway', 'name'], includeGeometry=True)
    result = Overpass().query(query)

    for x in result.elements():
        if x.id() == id:
            closet_road = x

    IWW_list = []
    for x in result.elements():
        if x.id() != id and x.tags()['name'] != name:
            cc = closest_point_on_way(closet_road.geometry()["coordinates"], x.geometry()["coordinates"])
            dtm = np.linalg.norm(point-cc)
            IWW_list.append(IWW(x, dtm, cc))

    IWW_list.sort(key=lambda x: x.dtm)
    result1 = IWW_list[0]

    for iww in IWW_list:
        if iww.obj != result1.obj:
            if np.dot(result1.cc-point, iww.cc-point) < 0:
                result2 = iww
                break

    new_geometry = []
    bool_add = False
    for point in closet_road.geometry()["coordinates"]:
        point = np.array([point[1], point[0]])
        if  np.array_equal(point, result1.cc) or np.array_equal(point, result2.cc):
            bool_add = not(bool_add)
        if bool_add:
            new_geometry.append(point)
    closet_road_geom = []
    for x in closet_road.geometry()["coordinates"]:
        closet_road_geom.append(np.array([x[1],x[0]]))

    return result1, result2, new_geometry, closet_road_geom

def main(lat, long):
    """
    Returning only what we want for obj1
    """
    result1, result2, x, y = segment(lat, long)
    return "Entre " + result1.obj.tags()['name'] + " et " + result2.obj.tags()['name']

if __name__ == '__main__':
    main(48.89525193, 2.247122897)