import sqlite3
import pandas as pd
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path=ROOT_DIR+"/_data"

def create_database():
    # Connexion à la base de données SQLite
    conn = sqlite3.connect(f'{path}/WebScrapping.db')

    create_table_queries=["CREATE TABLE IF NOT EXISTS processors (Model TEXT PRIMARY KEY,'TDP (W)' REAL);",
                          "CREATE TABLE IF NOT EXISTS gpu (Model TEXT PRIMARY KEY,'TDP (Watts)' REAL);",
                          "CREATE TABLE IF NOT EXISTS games (Title TEXT PRIMARY KEY,'Main Story (Hours)' REAL,Platforms TEXT,Genres TEXT,Images TEXT,CPU TEXT,GPU TEXT,RAM REAL);",
                          "CREATE TABLE IF NOT EXISTS boavizta_data ( manufacturer TEXT, name TEXT PRIMARY KEY, category TEXT, subcategory TEXT, gwp_total INTEGER, gwp_use_ratio REAL, yearly_tec INTEGER, lifetime INTEGER, use_location TEXT, report_date TEXT, sources TEXT, sources_hash TEXT, gwp_error_ratio REAL, gwp_manufacturing_ratio REAL, weight REAL, assembly_location TEXT, screen_size INTEGER, server_type TEXT, hard_drive TEXT, memory TEXT, number_cpu INTEGER, height REAL, added_date TEXT, add_method TEXT, gwp_transport_ratio REAL, gwp_eol_ratio REAL, gwp_electronics_ratio REAL, gwp_battery_ratio REAL, gwp_hdd_ratio REAL, gwp_ssd_ratio REAL, gwp_othercomponents_ratio REAL, comment TEXT );"
                          ]
    
    try:
        for query in create_table_queries:
            conn.execute(query)
    except sqlite3.Error as e:
        print(f"Erreur lors de la création de la table : {e}")
    
    # Fermer la connexion à la base de données
    return conn

def connect_to_database():
    # Vérifier si la base de données existe
    db_path = f"{path}/WebScrapping.db"

    db_exists = os.path.exists(db_path)

    # Connexion à la base de données SQLite
    conn = sqlite3.connect(db_path)

    if not db_exists:
        # Si la base de données n'existe pas, créer la base de données
        conn = create_database()
    else:
        conn = sqlite3.connect(db_path)
    
    print(f"\nSuccessfuly connected to dabase : {db_path}")

    return conn

import pandas as pd

import pandas as pd

def clean_games_dataframe(dataframe):

    dataframe = dataframe.astype('string')
    dataframe["Main Story (Hours)"] = pd.to_numeric(dataframe["Main Story (Hours)"].str.extract('(\d+)', expand=False), errors='coerce')

    return dataframe

