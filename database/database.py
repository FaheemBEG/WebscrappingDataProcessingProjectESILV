import pandas as pd
import os
import wget
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datascrapping import *

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path=ROOT_DIR+"/_data"

def create_data_files(path=path,bool_scrap_howlongtobeat:bool=False,bool_scrap_canyourunit:bool=False):  # False by default because data already scraped in /_data
    print(f"\n Creating data files . . .")

    scrap_processors()
    scrap_graphiccards()

    while bool_scrap_howlongtobeat:
        try:
            scrap_howlongtobbeat()
        except Exception as e:
            print(e)
            pass

    if bool_scrap_canyourunit:
        # Scrapping Can You Run It website by avoiding games that are already scrapped :
        games_scrapped=get_games_scrapped_number()
        while "9" not in games_scrapped.keys():
            try:
                print("\nGames already scrapped : ",games_scrapped)
                scrap_canyourunit(games_scrapped=games_scrapped)
                games_scrapped=get_games_scrapped_number()
            except Exception as e:
                games_scrapped=get_games_scrapped_number()
                print(e)
                continue
    try:
        games_part_1 = pd.read_csv(f"{path}/games_part_1.csv")
        games_part_2 = pd.read_csv(f"{path}/games_part_2.csv")
    except Exception:
        print(e)
        pass

    try:

        games_part_1['Title'] = games_part_1['Title'].str.lower()
        games_part_2['Title'] = games_part_2['Title'].str.lower()

        # Merging games data files
        final_df = pd.merge(games_part_2, games_part_1, on='Title', how='outer', suffixes=('', '_part_2'))
        final_df['Image'] = final_df['Image'].combine_first(final_df['Image_part_2'])

        # Deleting duplicated columns
        final_df.drop(['Image_part_2'], axis=1, inplace=True)

        final_df['Title'] = final_df['Title'].str.capitalize()

        final_df.to_csv(f"{path}/games.csv",index=False)
        print(f"\nComplete games data file successfuly created !")

    except Exception as e:
        print(e)
        pass
    
    print(f"\n>>> Downloading Boavizta data file")
    if os.path.exists(f"{path}/boavizta_data.csv"):
        os.remove(f"{path}/boavizta_data.csv")

    wget.download("https://raw.githubusercontent.com/Boavizta/environmental-footprint-data/main/boavizta-data-us.csv",f"{path}/boavizta_data.csv")
    print(f"\nData scrapped and data files successfuly created in : {path}")

def clean_games_dataframe(dataframe):

    dataframe = dataframe.astype('string')
    dataframe["Main Story (Hours)"] = pd.to_numeric(dataframe["Main Story (Hours)"].str.extract('(\d+)', expand=False), errors='coerce')
    dataframe.fillna(value={'Main Story (Hours)':-1,'CPU':"",'GPU':"",'Platforms':"",'Genres':"",'RAM':"",'Image':""},inplace=True)

    return dataframe

def csv_to_json(file_path:str=path):
    return

if __name__ == "__main__":
    create_data_files()
    csv_to_json()