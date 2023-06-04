'''utilities for making geometries'''

def makeGeoJsonPoint(longitude, latitude):
    '''construct a geojson point
    
    Parameters
    ----------
    longitude : float
        longitude
    latitude : float
        latitude

    Returns
    -------
    Returns GeoJson Point geometry
    
    '''

    point = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [float(longitude), float(latitude)]
        }
    }

    return point