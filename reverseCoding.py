#pip install geocoder
import geocoder
import pandas as pd

def reverse_coding(Lat,Lng):
    g = geocoder.osm([Lat,Lng], method='reverse')
    g.json
    town=g.town
    street=g.street
    return ({'Lat':Lat,'Lng':Lng,'Ville':town,'Nom de la voie':street,'Début du tronçon':'deb', 'Fin de tronçon':'fin'})

##Return the trees count in an area or a bounding box
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
from OSMPythonTools.nominatim import Nominatim
nominatim = Nominatim()
areaId = nominatim.query('Courbevoie, France').areaId()
overpass = Overpass()
query = overpassQueryBuilder(area=areaId, elementType='node', selector='"natural"="tree"', out='count')
result = overpass.query(query)
result.countElements()
