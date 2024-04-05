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
- https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-speech-to-text?tabs=windows%2Cterminal&pivots=programming-language-python

"""

from dotenv import dotenv_values
import azure.cognitiveservices.speech as speechsdk


def recognize_from_microphone():
    
    # Load credentials
    credentials = dotenv_values(".env")
    
    # This example requires environment variables named "AZURE_SPEECH_KEY" and "AZURE_SPEECH_REGION"  
    speech_key = credentials["AZURE_SPEECH_KEY"]
    #print(speech_key)
    speech_region = credentials["AZURE_SPEECH_REGION"]
    
    # Set the configuration of the Azure service
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language = credentials["AZURE_SPEECH_LANG"]

    # Audio from microphone
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    
    # OR ----------- Audio from audio file
    #audio_config = speechsdk.audio.AudioConfig(filename="YourAudioFile.wav")
    
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        #print("Recognized: {}".format(speech_recognition_result.text))
        return({'speech_text' : speech_recognition_result.text,
               'speech_info' : "Successed"})
    
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        #print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
        return({'speech_text' : None,
               'speech_info' : "Failed. Error : no speech recognized"})
        
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        #print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        return({'speech_text' : None,
               'speech_info' : "Failed. Error : speech recognition canceled"})
        
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            #print("Error details: {}".format(cancellation_details.error_details))
            #print("Did you set the speech resource key and region values?")
            return({'speech_text' : None,
               'speech_info' : "Failed. Error : Azure recognition service failed to connect"})
            

# Test
# recognize_from_microphone()

# Execution du script seulement s'il est appelé directement dans le terminal, sinon chargement uniquement sans exécution
if __name__ == "__main__":

    recognize_from_microphone()
