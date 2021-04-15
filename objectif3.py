from OSMPythonTools.api import Api
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
import numpy as np
from helpers import *
from objectif1 import *

def obj3(tree1, tree2):

    start1, end1, new_geom1, old_geom = segment(tree1[0], tree1[1])
    start2, end2, new_geom2, old_geom = segment(tree2[0], tree2[1])

    l_seg = [start1, start2, end1, end2]
    temp = []
    for iww in l_seg:
        min = -1
        for point in old_geom:
            dist = np.linalg.norm(iww.cc-point)
            if min == -1 or dist < min:
                min = dist
                associated_point = point
        temp.append([iww, associated_point])

    PwS_list = []
    for point in old_geom:
        l = []
        for x in temp:
            if np.array_equal(x[1], point):
                l.append(x[0])
        PwS_list.append(Pws(point, l))


    for PwS in PwS_list:
        for seg in PwS.l_seg:
            if len(l_seg) == 1:
                main_end = seg
            if len(l_seg) == 4:
                main_start = seg

            l_seg.remove(seg)


    return main_start, main_end


def main(lat1, long1, lat2, long2):
    """

    :param 4 float = 2 geocodes
    :return: the main segment
    """
    one_tree = np.array([lat2, long2])
    another_tree = np.array([lat1, long1])
    start, end = obj3(one_tree, another_tree)
    return "Entre " + start.obj.tags()['name'] + " et " + end.obj.tags()['name']


if __name__ == '__main__':
    print(main(48.897121406, 2.2479852324, 48.89627806,2.248657510))