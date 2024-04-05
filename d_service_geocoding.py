"""
Service for geocoding :
=====================

This module can be processed as following :
- `city` as a string is passed from the user input.
- The Nominatim geocoder (from Open Street Map) is invoked.
- The `user_agent` should be declared for OSM' monitoring purpose. `user_agent` is the name of your service.


Ressources :
- Geopy : https://github.com/geopy/geopy
- Open Street Map : https://www.openstreetmap.fr/
"""

from geopy.geocoders import Nominatim
from sys import argv

def city_to_coordinates(city):
    
    # Define the name of your app (for external service monitoring)
    geolocator = Nominatim(user_agent="vocal_weather_app")
    
    if city is None:
        city = "Tours" # default value if city recognition failed
        geocoding_info = "Failed. No city from user input, city of Tours as default value."
    else :
        geocoding_info = "Successed"
    
    # Send the user' city to geocode service
    location = geolocator.geocode(city)
    # Extract desired data : coordinates
    lat = location.latitude
    lon = location.longitude    
        
    if (lat or lon) is None :
        geocoding_info = "Failed. OSM API service failed to return coordinates."


    # Return
    #print(f'Latitude, Longitude : {lat, lon}')
    return({'city' : city,
            'lat' : lat,
            'lon' : lon,
            'geocoding_info' : geocoding_info})

# Test
# city_to_coordinates(city='Tours')

# Execution du script seulement s'il est appelé directement dans le terminal, sinon chargement uniquement sans exécution
if __name__ == "__main__":

    city_to_coordinates(argv[1])