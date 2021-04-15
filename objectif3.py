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
    temp = []               #now, we just attribute to each crossing point between a segment and the road
    for iww in l_seg:       #a point on the road (because theses crossing point aren't on the road they are only
        min = -1            #the closest point of the segment to the road
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


    for PwS in PwS_list:        #when 4 segments are remaining and we meet one, it's the start of our segment
        for seg in PwS.l_seg:   #when 1 segment is remaining and we meet him, it's the last one
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

    lat1 = 48.897121406
    long1 = 2.2479852324
    lat2 = 48.89627806
    long2 =2.248657510
    print(main(lat1, long1, lat2, long2))