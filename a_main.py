
from b_service_azure_speech import recognize_from_microphone
from c_service_ner import extract_city, extract_horizon
from d_service_geocoding import city_to_coordinates
from e_service_weather_forecast import weather_forecast_from_coord
from f_service_db_storage import connect_to_db, save_to_database, read_from_database


# Part 1 - Vocal command
#text_input = 'quelle est la météo à tours pour les 3 prochains jours'
print("==== PART 1 : Vocal command ====================")
text_input = recognize_from_microphone()
print(f"Reconnaissande de l'audio - Statut : {text_input['speech_info']}")
print(f"La transcription de l'audio est : {text_input['speech_text']}")


# Part 2 - NLP NER
# To be done : improve horizon extraction
print("==== PART 2 - NLP NER ====================")
city_input = extract_city(text = text_input['speech_text'])
print(f"Extraction de la ville à partir de l'audio - Statut : {city_input['city_extracted_info']}")
print(f"La ville extraite de l'audio est : {city_input['city_extracted']}")

horizon_input = extract_horizon(text = text_input['speech_text'])
print(f"Extraction de l'horizon à partir de l'audio - Statut : {horizon_input['horizon_extracted_info']}")
print(f"L'horizon des prévision est : {horizon_input['horizon_extracted']}")


# Part 3 - Geocoding from API
print("==== PART 3 - Geocoding from API ====================")
coord_input = city_to_coordinates(city = city_input['city_extracted'])
print(f"Geocoding à partir de l'audio - Statut : {coord_input['geocoding_info']}")
print(f"Les coordonnées de la ville de {coord_input['city']} sont : lat={coord_input['lat']} & lon={coord_input['lon']}")


# Part 4 - Weather forecast from API
print("==== PART 4 - Weather forecast from API ====================")
meteo_input = weather_forecast_from_coord(lat=coord_input['lat'], lon=coord_input['lon'], horizon=[horizon_input['horizon_extracted'] if horizon_input['horizon_extracted'] is not None else None])
print(f"Prévision météo à partir de l'audio - Statut : {meteo_input['weather_info']}")


# Part 5 - Data storage into Azure DB for monitoring
print("==== PART 5 - Data storage into Azure DB for monitoring ====================")
save_to_database(speech = text_input,
                 city = city_input,
                 horizon = horizon_input,
                 geocoding = coord_input,
                 weather = meteo_input)#(meteo_input['weather_info'], meteo_input['weather_data']))

read_from_database()