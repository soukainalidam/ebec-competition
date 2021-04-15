from OSMPythonTools.api import Api
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
import numpy as np

ltree = [np.array([43.60146784122481, 1.4419696626057792]), np.array([43.601733940239484, 1.4413447078974355]), np.array([43.601963134067844, 1.4416021999661093]), np.array([43.60183, 1.4416]),
         np.array([43.6017009207177, 1.4417711791361765]), np.array([43.60189321061956, 1.4410603937382749]), np.array([43.60178444064956, 1.4409691986306195]), np.array([43.60187, 1.44163])]


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
    name = JSON['address']['road']
    bbox = JSON["boundingbox"]
    id = JSON["osm_id"]
    realbbox = [float(bbox[0]), float(bbox[2]), float(
        bbox[1]) + 0.005, float(bbox[3]) + 0.005]
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
    query = overpassQueryBuilder(bbox=bbox, elementType=['way'], selector=[
                                 'highway', 'name'], includeGeometry=True)
    result = Overpass().query(query)

    for x in result.elements():
        if x.id() == id:
            closet_road = x

    IWW_list = []
    for x in result.elements():
        if x.id() != id and x.tags()['name'] != name:
            cc = closest_point_on_way(closet_road.geometry(
            )["coordinates"], x.geometry()["coordinates"])
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
        if np.array_equal(point, result1.cc) or np.array_equal(point, result2.cc):
            bool_add = not(bool_add)
        if bool_add:
            new_geometry.append(point)
    closet_road_geom = []
    for x in closet_road.geometry()["coordinates"]:
        closet_road_geom.append(np.array([x[1], x[0]]))

    return result1, result2, new_geometry, closet_road_geom


def obj2_knowing_trees_of_way(list_tree, newgeom, result1, result2):

    temp_ltree_of_point = []
    for tree in list_tree:
        min = - 1
        for point in newgeom:
            dist = np.linalg.norm(tree-point)
            if dist < min or min == -1:
                min = dist
                associated_point = point
        temp_ltree_of_point.append((tree, associated_point))

    ltree_of_point = []
    for pointw in newgeom:
        ltree_of_point.append(WayP(pointw, [], None))
    for x in ltree_of_point:
        for tuple in temp_ltree_of_point:
            if np.array_equal(tuple[1], x.c):
                x.ltree.append([tuple[0], 0])

    for i in range(0, len(ltree_of_point)):
        if i < len(ltree_of_point)-1:
            ltree_of_point[i].uv = (ltree_of_point[i+1].c - ltree_of_point[i].c) / \
                np.linalg.norm((ltree_of_point[i+1].c - ltree_of_point[i].c))
        else:
            ltree_of_point[i].uv = ltree_of_point[i-1].uv

    for i in range(0, len(ltree_of_point)):
        obj = ltree_of_point[i]
        biss_vect = None
        if i < len(ltree_of_point)-1 and i > 1:
            biss_vect = ltree_of_point[i].uv - ltree_of_point[i-1].uv
            orth_biss = np.array([biss_vect[1], -biss_vect[0]])

        if biss_vect is None:  # sur les extremités on fait pas de bissectrice
            for j in range(0, len(obj.ltree)):
                tree = obj.ltree[j][0]
                obj.ltree[j][1] = np.dot(obj.uv, tree-obj.c)
            obj.ltree.sort(key=lambda x: x[1])

        else:  # sinon bissectrice etc
            one_side = []
            another_side = []
            for j in range(0, len(obj.ltree)):
                if np.dot(orth_biss, obj.ltree[j][0]-obj.c) > 0:
                    one_side.append(obj.ltree[j])
                else:
                    another_side.append(obj.ltree[j])
            if np.dot(orth_biss, obj.uv) > 0:
                for tree in one_side:
                    tree[1] = np.dot(ltree_of_point[i].uv,
                                     tree[0]-ltree_of_point[i].c)
                for tree in another_side:
                    tree[1] = np.dot(ltree_of_point[i-1].uv,
                                     tree[0] - ltree_of_point[i-1].c)
            else:
                for tree in one_side:
                    tree[1] = np.dot(ltree_of_point[i-1].uv,
                                     tree[0]-ltree_of_point[i-1].c)
                for tree in another_side:
                    tree[1] = np.dot(ltree_of_point[i].uv,
                                     tree[0] - ltree_of_point[i].c)

            one_side.sort(key=lambda x: x[1])
            another_side.sort(key=lambda x: x[1])

            if np.dot(orth_biss, obj.uv) > 0:
                obj.ltree = another_side + one_side
            else:
                obj.ltree = one_side + another_side

    sorted_tree_list = []
    for x in ltree_of_point:
        for tree in x.ltree:

            sorted_tree_list.append(tree[0])

    if np.array_equal(newgeom[0], result1.cc):
        origin = result1
    else:
        origin = result2

    return sorted_tree_list, origin


def obj2_knowing_every_trees(list_tree, way_id, new_geom, result1, result2):
    true_list = []
    for tree in list_tree:
        way = Nominatim().query(tree[0], tree[1], reverse=True, zoom=17)
        id = way.toJSON()[0]["osm_id"]
        if id == way_id:
            true_list.append(tree)
    obj2_knowing_trees_of_way(true_list, new_geom, result1, result2)


def obj3(tree1, tree2):

    start1, end1, new_geom1, old_geom = segment(tree1[0], tree1[1])
    start2, end2, new_geom2, old_geom = segment(tree2[0], tree2[1])
    print(old_geom)
    l_seg = [start1, start2, end1, end2]
    for x in l_seg:
        print(x.cc)
    for point in old_geom:
        for iww in l_seg:
            if np.array_equal(iww.cc, point):
                if len(l_seg) == 1:
                    main_end = iww
                elif len(l_seg) in [2, 3]:
                    l_seg.remove(iww)
                elif len(l_seg) == 4:
                    main_start = iww
                    l_seg.remove(iww)

    print(len(l_seg))

    return main_start, main_end


obj3(np.array([48.897121406, 2.2479852324]),
     np.array([48.89627806, 2.248657510]))
