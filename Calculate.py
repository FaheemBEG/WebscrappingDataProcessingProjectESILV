import sqlite3
import pandas as pd
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
path=ROOT_DIR+"/_data"

def load_games():
    conn = sqlite3.connect('WebScrapping.db')
    query = "SELECT * FROM games"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df



def calculate(game:str,plateform:str,country:str):
    conn = sqlite3.connect('WebScrapping.db')

