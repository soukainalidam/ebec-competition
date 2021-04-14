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


def geo_to_address(lat, long):
    """
    Return the address corresponding to a point
    """
    return Nominatim().query(lat, long, reverse=True, zoom=20)


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


def segment(long, lat):
    """
    Main function defining the segment in wich the point is
    :param long: coords
    :param lat: coords
    :return: two way-objects such as our point is in between these two ways
    """
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

    return result1, result2, new_geometry



ltree = [np.array([43.60146784122481, 1.4419696626057792]), np.array([43.601733940239484, 1.4413447078974355]), np.array([43.601963134067844, 1.4416021999661093]),
         np.array([43.6017009207177, 1.4417711791361765]), np.array([43.60189321061956, 1.4410603937382749]), np.array([43.60178444064956, 1.4409691986306195])]


def obj2_knowing_trees_of_way(list_tree, way, main_tree, result1, result2):

    main_tree = np.array(main_tree)
    temp_ltree_of_point = []
    for tree in list_tree:
        min = - 1
        for point in way:
            dist = np.linalg.norm(tree-point)
            if dist < min or min == -1:
                min = dist
                associated_point = point
        temp_ltree_of_point.append((tree, associated_point))

    ltree_of_point = []
    for pointw in way:
        ltree_of_point.append(WayP(pointw, [], None))
    for x in ltree_of_point:
        for tuple in temp_ltree_of_point:
            if np.array_equal(tuple[1], x.c):
                x.ltree.append([tuple[0],0])


    for i in range(0, len(ltree_of_point)):
        if i < len(ltree_of_point)-1:
            ltree_of_point[i].uv = (ltree_of_point[i+1].c - ltree_of_point[i].c)/np.linalg.norm((ltree_of_point[i+1].c - ltree_of_point[i].c))
        else:
            ltree_of_point[i].uv = ltree_of_point[i-1].uv

    for obj in ltree_of_point: #here select only bissectrice
        for i in range(0, len(obj.ltree)):
            tree = obj.ltree[i][0]
            obj.ltree[i][1] = np.dot(obj.uv, tree-obj.c)
        obj.ltree.sort(key=lambda x: x[1])

    c = 0
    for x in ltree_of_point:
        for tree in x.ltree:
            c = c + 1
            if np.array_equal(tree[0], main_tree):
                print(str(c)+ 'eme tree en partant de ')

    if np.array_equal(way[0], result1.cc):
        print(result1.obj.tags()['name'])
    else:
        print(result2.obj.tags()['name'])






result1, result2, new_geometry = segment(43.60186173065864, 1.4415735545641217)

obj2_knowing_trees_of_way(ltree, new_geometry, (43.60189321061956, 1.4410603937382749), result1, result2)