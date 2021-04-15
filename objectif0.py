from OSMPythonTools.nominatim import Nominatim


def geo_to_address(lat, long):
    """
    Return the response of the query corresponding to a point
    """
    return Nominatim().query(lat, long, reverse=True, zoom=20)


def main(lat, long):
    """
    Return the address
    """
    query = geo_to_address(lat, long)
    address = query.toJSON()[0]['address']
    return "A " + address['town'] + " , " + address['road']


print(main(48.897121406, 2.2479852324))

