from OSMPythonTools.api import Api
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
import numpy as np
from helpers import *
from objectif1 import *

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
                x.ltree.append([tuple[0],0])


    for i in range(0, len(ltree_of_point)):
        if i < len(ltree_of_point)-1:
            ltree_of_point[i].uv = (ltree_of_point[i+1].c - ltree_of_point[i].c)/np.linalg.norm((ltree_of_point[i+1].c - ltree_of_point[i].c))
        else:
            ltree_of_point[i].uv = ltree_of_point[i-1].uv

    for i in range(0, len(ltree_of_point)):
        obj = ltree_of_point[i]
        biss_vect = None
        if i < len(ltree_of_point)-1 and i > 1:
            biss_vect = ltree_of_point[i].uv - ltree_of_point[i-1].uv
            orth_biss = np.array([biss_vect[1], -biss_vect[0]])

        if biss_vect is None: #sur les extremités on fait pas de bissectrice
            for j in range(0, len(obj.ltree)):
                tree = obj.ltree[j][0]
                obj.ltree[j][1] = np.dot(obj.uv, tree-obj.c)
            obj.ltree.sort(key=lambda x: x[1])

        else: #sinon bissectrice etc
            one_side = []
            another_side = []
            for j in range(0, len(obj.ltree)):
                if np.dot(orth_biss, obj.ltree[j][0]-obj.c) > 0:
                    one_side.append(obj.ltree[j])
                else:
                    another_side.append(obj.ltree[j])
            if np.dot(orth_biss, obj.uv) > 0:
                for tree in one_side:
                    tree[1] = np.dot(ltree_of_point[i].uv, tree[0]-ltree_of_point[i].c)
                for tree in another_side:
                    tree[1] = np.dot(ltree_of_point[i-1].uv, tree[0] - ltree_of_point[i-1].c)
            else:
                for tree in one_side:
                    tree[1] = np.dot(ltree_of_point[i-1].uv, tree[0]-ltree_of_point[i-1].c)
                for tree in another_side:
                    tree[1] = np.dot(ltree_of_point[i].uv, tree[0] - ltree_of_point[i].c)

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


def main(ltree):

    first_tree = np.array(ltree[3])
    result1, result2, new_geom, old_geom = segment(first_tree[0], first_tree[1])
    sorted_list, origin = obj2_knowing_trees_of_way(ltree, new_geom, result1, result2)
    print("En partant de "+ origin.obj.tags()['name'] + ' , ', end='')
    for i in range(0, len(sorted_list)):
        print(str(sorted_list[i])+' est le ' + str(i+1)+ ' ème arbre')

if __name__ == '__main__':
    main(ltree = [np.array([43.60146784122481, 1.4419696626057792]), np.array([43.601733940239484, 1.4413447078974355]), np.array([43.601963134067844, 1.4416021999661093]), np.array([43.60183, 1.4416]),
         np.array([43.6017009207177, 1.4417711791361765]), np.array([43.60189321061956, 1.4410603937382749]), np.array([43.60178444064956, 1.4409691986306195]), np.array([43.60187, 1.44163])])