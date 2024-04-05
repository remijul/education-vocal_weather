# Educational project - AI powered webapp for weather forecast

## Project's objectives

- Develop a voice-controlled weather application to allow more accessible and natural uses of the application.
- Voice recognition must be able to identify the location and forecast horizon.

## Developed Features

- Integrate connection to Azure Cognitives Services API.
- Integrate calls with speech to text functions.
- Develop NER for automatic detection of city and date.
- Integrate connection to the weather prediction API.
- Configure the call to the weather prediction API according to the voice instruction (location, prediction horizon, etc.)
- Monitor the quality of the result taking into account the uncertainty linked to the weather prediction and that linked to speech to text
- Define the procedure in the event of results below a minimum quality threshold
- Store the results in a database on Azure.
- Expose and integrate forecast results in a simple web interface.

## Technical stack

- Azure : Azure Cognitives Services Speech to Test, SQL Database.
- Spacy : NER for localities (city).
- Transformers : NER for date (forecast horizon) with Hugging Face - Camembert models.
- Streamlit : simple web app.

## Requirements

- Susbscription available to Azure Cognitives Services and SQL Database.
- Authentification available to Hugging Face API.
- Virtual environment available in the `requirements.txt` file.
