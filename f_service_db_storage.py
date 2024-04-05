"""
Service for storage data into the MS SQL database hosted on Azure
=====================

First, actions are needed on Azure :
- Create a ressource group and set it up
- Create a MS SQL server and set it up
- Create a MS SQL database and set it up

Then, this module can be processed as following :
- Credentials are available as environnement variables
- One function is dedicated to store data
- One function is dedicated to retrieve data from the db

Ressources :
- ODBC Driver : https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16
- https://learn.microsoft.com/fr-fr/azure/azure-sql/database/connectivity-settings?view=azuresql&tabs=azure-portal#deny-public-network-access
- Create Table MSSQL : https://stackoverflow.com/questions/6520999/create-table-if-not-exists-equivalent-in-sql-server

"""

import pyodbc
import pandas as pd
from dotenv import dotenv_values
from time import gmtime, strftime

# Function dedicated for connection to the DB
def connect_to_db():
    
    # Load credentials
    credentials = dotenv_values(".env")
    
    # This example requires environment variables named "AZURE_SPEECH_KEY" and "AZURE_SPEECH_REGION"  
    driver = credentials["AZURE_ODBC_DRIVER"]
    server = credentials["AZURE_SQL_SERVER_NAME"]
    port = credentials["AZURE_SQL_SERVER_PORT"]
    database = credentials["AZURE_SQL_DB_NAME"]
    uid = credentials["AZURE_SQL_DB_USER"]
    pwd = credentials["AZURE_SQL_DB_PWD"]
        
    # ODBC connection
    connection_string = (
        f"Driver={driver};"
        f"Server={server},{port};"
        f"Database={database};"
        f"Uid={uid};"
        f"Pwd={pwd};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

    # Establish the connection
    try:
        connection = pyodbc.connect(connection_string)
    except:
        print('Failed to connect to DB.')
        connection = None
    # End
    return connection


# Function dedicated to store data
def save_to_database(speech, city, horizon, geocoding, weather):

    # Establish the connection to the DB
    connection = connect_to_db()
        
    if connection:
        cursor = connection.cursor()

        # Create table if not exists
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'weather_app_monitoring')
            BEGIN
                CREATE TABLE weather_app_monitoring (
                    timestamp NVARCHAR(100),
                    speech_status NVARCHAR(100),
                    speech_text NVARCHAR(1000),
                    extract_city_status NVARCHAR(100),
                    extract_city_text NVARCHAR(1000),
                    extract_horizon_status NVARCHAR(100),
                    extract_horizon_text NVARCHAR(1000),
                    geocoding_status NVARCHAR(100),
                    geocoding_city NVARCHAR(1000),
                    geocoding_lat FLOAT(16),
                    geocoding_lon FLOAT(16),
                    weather_status NVARCHAR(100),
                    weather_data NVARCHAR(100)          
                );
            END;
        ''')
        
        # Insert data into the table
        cursor.execute("""
                    INSERT INTO weather_app_monitoring
                    (timestamp, speech_status, speech_text, extract_city_status, extract_city_text, extract_horizon_status, extract_horizon_text,
                    geocoding_status, geocoding_city, geocoding_lat, geocoding_lon, weather_status, weather_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (str(strftime("%Y-%m-%d %H:%M:%S", gmtime())),
                        speech['speech_info'],
                        speech['speech_text'],
                        city['city_extracted_info'],
                        city['city_extracted'],
                        horizon['horizon_extracted_info'],
                        horizon['horizon_extracted'],
                        geocoding['geocoding_info'],
                        geocoding['city'],
                        geocoding['lat'],
                        geocoding['lon'],
                        weather['weather_info'],
                        weather['weather_data'])
                    )

        # Close the connection
        connection.commit()
        connection.close()
    
    else:
        print('Data not saved to DB.')

# Test :
# save_to_database()


# Function dedicated to retrieve data from the db
def read_from_database():

    # Establish the connection to the DB
    connection = connect_to_db()
    
    if connection:
        cursor = connection.cursor()
        
        # Read data from the table
        cursor.execute("SELECT * FROM weather_app_monitoring")
        for row in cursor.fetchall():
            print(row)
        
        # Close the connection
        connection.commit()
        connection.close()
    
    else:
        print('Impossible to read data from DB.')

# Test :    
# test_database()


# Function dedicated to drop table from the db
def drop_table_from_database():

    # Establish the connection to the DB
    connection = connect_to_db()
    cursor = connection.cursor()
    
    # Read data from the table
    cursor.execute("DROP TABLE dbo.weather_app_monitoring")

    # Close the connection
    connection.commit()
    connection.close()



# Execution du script seulement s'il est appelé directement dans le terminal, sinon chargement uniquement sans exécution
if __name__ == "__main__":
    
    read_from_database()