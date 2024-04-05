"""
Service for NER - Named Entity Recognition :
=====================

The service is dedicated for extrcationC CITY and HORIZON of forecast from a given text input.
First, actions are needed on VS Code Terminal :
- Load the French pipeline optimized for CPU from spacy with :
python -m spacy download fr_core_news_md


Then, this module can be processed as following :
- One function is dedicated to extrcat the city
- One function is dedicated to extrcat the horizon of forecasting (1 or several days)

Ressources :
- https://spacy.io/usage#quickstart
- https://spacy.io/models/fr#fr_core_news_sm
- https://www.turing.com/kb/a-comprehensive-guide-to-named-entity-recognition
"""

from sys import argv
from os.path import basename
import requests
from dotenv import dotenv_values
import spacy
import datefinder
import datetime


# Load the French NLP model from SpaCy
#en_core_web_sm => OK sur DATE recognition !!!
#nlp = spacy.load("fr_core_news_md") #"fr_core_news_lg"

# Cities are handled with SPACY - NER
def extract_city(text):
    
    nlp = spacy.load("fr_core_news_md")
    
    # Process if text is not NONE
    if text:
        # Process the text using SpaCy
        doc = nlp(text)

        # Extract entities (locations) from the processed text
        locations = [ent.text for ent in doc.ents if ent.label_ in ("LOC", "GPE")]

        # If there are multiple locations, you may need additional logic to choose the correct one
        if locations:
            #print(locations[0])
            return{'city_extracted' : locations[0],
                'city_extracted_info' : 'Successed'}
        else:
            #print('None')
            return{'city_extracted' : None,
                'city_extracted_info' : 'Failed'}
    else:
        #print('None')
        return{'city_extracted' : None,
               'city_extracted_info' : 'Failed'}        

# Test
# extract_city(text='quelle est la météo à tours')#je voudrais connaitre la météo à tours')# en France')


# Dates are handled with transformers - CAMEMBERT - from Hugging Face Inference API
def extract_horizon(text):

    # Part 1 - Extract NER with Hugging Face API
    # Load credentials
    credentials = dotenv_values(".env")
    HF_API_TOKEN = credentials["HF_USER_ACCESS_TOKENS"]

    # Define Hugging Face end point 
    API_URL = "https://api-inference.huggingface.co/models/Jean-Baptiste/camembert-ner-with-dates"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
        
    # Get response from Hugging Face inference API
    response = requests.post(API_URL, headers=headers, json=text)
    #print(response.status_code)
    
    # Part 2 - Convert date to horizon with datefinder
    # Code status
    if response.status_code == 200:
        
        status = "Successed"
        
        # Extract date only
        time_entitiy = [ent['word'] for ent in response.json() if ent['entity_group'] == 'DATE'][0]
        #print(time_entitiy)
        
        # Convert to a convenient format
        for matches in datefinder.find_dates(time_entitiy):
            date_find = matches 

        # Calculate horizon in days with datetime.now()
        horizon_in_days = (date_find - datetime.datetime.now()).days
    
    else:
        horizon_in_days = None
        status = "Failed"

    # End 
    return({'horizon_extracted_info': status,
            'horizon_extracted_code': response.status_code,
            'horizon_extracted': horizon_in_days})

# Test
# extract_horizon(text='je voudrais connaitre la météo à tours en France pour 7 mars 2024') #le 7 mars 2024


# Execution du script seulement s'il est appelé directement dans le terminal, sinon chargement uniquement sans exécution
# "lundi dernier était le premier jour de Juillet à Blois et Paris"
if __name__ == "__main__":

    extract_city(argv[1])
    extract_horizon(argv[1])