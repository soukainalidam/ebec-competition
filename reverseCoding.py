#pip install geocoder
import geocoder
import pandas as pd

def reverse_coding(Lat,Lng):
    g = geocoder.osm([Lat,Lng], method='reverse')
    g.json
    town=g.town
    street=g.street
    return ({'Lat':Lat,'Lng':Lng,'Ville':town,'Nom de la voie':street,'Début du tronçon':'deb', 'Fin de tronçon':'fin'})
