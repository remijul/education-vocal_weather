@echo off

rem Créer un environnement virtuel
python -m venv venv

rem Activer l'environnement virtuel
venv\Scripts\activate

rem Installer les dépendances (par exemple, TensorFlow)
pip install -r requirements.txt

rem Désactiver l'environnement virtuel
rem deactivate

