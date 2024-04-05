# -*- coding: utf-8 -*-
#!python -m streamlit run weather_app.py
"""
Streamlit Weather App
=====================

This is a basic Streamlit webapp displaying the current temperature, wind speed
and wind direction as well as the temperature and precipitation forecast for 
the week ahead at one of 40,000+ cities and towns around the globe. The weather
forecast is given in terms of the actual timezone of the city of interest.
Additionally, a map with the location of the requested city is displayed.

- The weather data is from http://open-meteo.com
- The list with over 40,000 cities around world stems from 
  https://simplemaps.com/data/world-cities

Enjoy exploring!
From : Nino Dakov on Github
- https://github.com/ndakov/streamlit-weather-app?tab=readme-ov-file

"""

import streamlit as st
import pandas as pd
import requests
import json
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from datetime import datetime
from datetime import timezone as tmz
#import pytz
#from tzwhere import tzwhere
import folium
from streamlit_folium import folium_static

# Internal services for serving app data
from b_service_azure_speech import recognize_from_microphone
from c_service_ner import extract_city, extract_horizon
from d_service_geocoding import city_to_coordinates
from e_service_weather_forecast import weather_forecast_from_coord
from f_service_db_storage import connect_to_db, save_to_database, read_from_database



# Title and description for your app ------------------------------------
st.title("Hi ! Welcome in Vocal Weather App !")
st.subheader(" How's the weather? :mostly_sunny: or :sun_behind_rain_cloud: or :rain_cloud: ...")



# Section Azure STT : Vocal command --------------------------------------
st.markdown("""---""")
st.subheader("Vocal command :studio_microphone:")
st.write("Please speak into your microphone to launch the app :microphone:")

# Initialisation
text_input = ({'speech_info' : None,
              'speech_text' : None})

# Process and render data
text_input = recognize_from_microphone()
#temp = text_input['speech_text']

if text_input:
    st.info(f'''The audio transcription from Speech-To-Text service is : "{text_input['speech_text']}"''')
else:
    st.info("Waiting for vocal command ...")
#print(f"Reconnaissande de l'audio - Statut : {text_input['speech_info']}")
#print(f"La transcription de l'audio est : {text_input['speech_text']}")

st.write("Azure API is used here for the speech-to-text service ([see Azure documentation](https://azure.microsoft.com/en-us/products/ai-services/speech-to-text)).""")



# Section NLP : City and horizon inputs from vocal command --------------------------------------
st.markdown("""---""")
st.subheader("Extraction of entities :cityscape: & :date:")
st.write("From NLP magics, your vocal command is processed as following :magic_wand:")

# Initialisation
city_input = None
horizon_input = None

# Process and render data
#if text_input['speech_info']:
#    city_input = extract_city(text = text_input['speech_text'])['city_extracted']
#    horizon_input = extract_horizon(text = text_input['speech_text'])['horizon_extracted']
with st.spinner('Loading...'):    
    col1, col2 = st.columns(2)
    with col1:    
        city_input = extract_city(text = text_input['speech_text'])['city_extracted']
        st.info(f'''The city extracted from the vocal command is "{city_input}"''')
    with col2:
        horizon_input = extract_horizon(text = text_input['speech_text'])['horizon_extracted']
        st.info(f'''The horizon extracted from the vocal command is "{horizon_input}"''')

st.write("""LOC entities are processed with the Spacy' Python library and the `fr_core_news_md`,
         a French pipeline optimized for CPU ([see Spacy documentation](https://spacy.io/models/fr#fr_core_news_md)).""")
st.write("""DATE entities are processed with the Transformer technologie.
         The model `Jean-Baptiste/camembert-ner-with-dates` is a dedicated BERT Transformer for French named `CamemBERT`, specifically trained for dates and
         hosted on Hugging Face Inference API ([see the HF Inference API documentation](https://huggingface.co/Jean-Baptiste/camembert-ner-with-dates)).""")


# Section Geocoding : --------------------------------------
st.markdown("""---""")
st.subheader("Geocoding :world_map:")
st.write("From your vocal command the geocoding service returns the spatial coordinates.")

# Initialisation
#coord_input = None

# Process and render data
#if city_input:
with st.spinner('Loading...'):
    coord_input = city_to_coordinates(city = city_input)
    st.info(f"Information from Geocoding service : {coord_input['geocoding_info']}")
    st.info(f"Spatial coordinates of `{coord_input['city']}` are : `latitude={coord_input['lat']}` & `lon={coord_input['lon']}`.")
#else:
#    st.info(f"Spatial coordinates are uknown due to a failure during the LOC extraction process.")

st.write("The Geopy' Python library is used here for the geocoding service and based on Open Street Map API ([see Geopy documentation](https://geopy.readthedocs.io/en/stable/)).""")



# Section Weather : --------------------------------------
st.markdown("""---""")
st.subheader("Weather information :sun_with_face:")


# Process and render data table
with st.spinner('Loading...'):
    st.subheader('Weather table :', divider='rainbow')
    weather_input = weather_forecast_from_coord(lat=coord_input['lat'],
                                          lon=coord_input['lon'],
                                          horizon=[horizon_input if horizon_input is not None else None])

    weather_df = weather_input['weather_df']
    st.write(f"Finally the weather is shown here after for the city of {coord_input['city']} and considering a forecast horizon of {weather_input['forecast_horizon']} days.")
    st.dataframe(data=weather_df)

# Process and render graph

with st.spinner('Loading...'):
    st.subheader('Weather graph :', divider='rainbow')
    # Create figure with secondary y axis
    fig = make_subplots(specs=[[{"secondary_y":True}]])
    week_ahead = pd.to_datetime(weather_df['date'],format="%Y-%m-%dT%H:%M")
    
    # Add traces
    fig.add_trace(go.Scatter(x = weather_df['date'],#week_ahead,#+tzoffset, 
                             y = weather_df['temperature_2m'],
                             name = "Temperature °C"),
                  secondary_y = False)
    
    fig.add_trace(go.Bar(x = weather_df['date'],#week_ahead,#+tzoffset, 
                         y = weather_df['precipitation'],
                         name = "Precipitation mm"),
                  secondary_y = True)
    
    time_now = datetime.now(tmz.utc)#+tzoffset
    
    fig.add_vline(x = time_now, line_color="red", opacity=0.4)
    fig.add_annotation(x = time_now, y=max(weather_df['temperature_2m'])+5,
                text = time_now.strftime("%d %b %y, %H:%M"),
                showarrow=False,
                yshift=0)
    
    fig.update_yaxes(range=[min(weather_df['temperature_2m'])-10,
                            max(weather_df['temperature_2m'])+10],
                      title_text="Temperature °C",
                     secondary_y=False,
                     showgrid=False,
                     zeroline=False)
        
    fig.update_yaxes(range=[min(weather_df['precipitation'])-2,
                            max(weather_df['precipitation'])+8], 
                      title_text="Precipitation (rain/showers/snow) mm",
                     secondary_y=True,
                     showgrid=False)
    
    
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=0.7
    ))


    # Section Map 
with st.spinner('Loading...'):
    st.subheader('Weather map :', divider='rainbow')
    m = folium.Map(location=[coord_input['lat'], coord_input['lon']], zoom_start=7)
    folium.Marker([coord_input['lat'], coord_input['lon']], 
              popup=coord_input['city'], 
              tooltip=f'Il fait toujours beau à {coord_input["city"]} 😃').add_to(m)
    
    # call to render Folium map in Streamlit
    
    # Make folium map responsive to adapt to smaller display size (
    # e.g., on smartphones and tablets)
    make_map_responsive= """
     <style>
     [title~="st.iframe"] { width: 100%}
     </style>
    """
    st.markdown(make_map_responsive, unsafe_allow_html=True)
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Display map
    st_data = folium_static(m, height = 370)
    


# Concluding remarks --------------------------------------
st.write('Weather data source: [http://open-meteo.com](http://open-meteo.com) \n\n'+
        
        'Original Github repository: [streamlit-weather-app](https://github.com/ndakov/streamlit-weather-app)')
st.write('Thanks for visiting me and I love cheese :joy:')



