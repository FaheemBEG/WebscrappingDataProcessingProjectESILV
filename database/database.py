""" Importing modules """

import pandas as pd
import os
import wget
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datascrapping import *
from calculate import add_consumption

# Root path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = ROOT_DIR + "/_data"

""" Functions """

def create_data_files(
    path=path,
    bool_scrap_howlongtobeat: bool = False,
    bool_scrap_canyourunit: bool = False,
):  # False by default because data already scraped in /_data
    """This function creates all data files needed by using functions in 'datascrapping.py'.
    Creates:
        boavizta_data.csv : Boavizta data useful to estimate carboon footprint
        games.csv : Fusion of games_part_1.csv and games_part_2.csv to an unique and complete .csv file
        processors.csv : CPUs data
        gpu.csv : GPUs data
    """

    print(f"\n Creating data files . . .")

    # scrap_processors()
    # scrap_graphiccards()

    if bool_scrap_howlongtobeat:
        # Scrapping HowLongToBeat website by avoiding games that are already scrapped :
        games_scrapped = get_games_scrapped_number(file_path=f"{path}/games_part_1.csv")
        while "9" not in games_scrapped.keys():
            try:
                print("\nHowLongToBeat games already scrapped : ", games_scrapped)
                scrap_howlongtobbeat(games_scrapped=games_scrapped)
                games_scrapped = get_games_scrapped_number()
            except Exception as e:
                games_scrapped = get_games_scrapped_number()
                print(e)
                continue

    if bool_scrap_canyourunit:
        # Scrapping Can You Run It website by avoiding games that are already scrapped :
        games_scrapped = get_games_scrapped_number()
        while "9" not in games_scrapped.keys():
            try:
                print("\nGames already scrapped : ", games_scrapped)
                scrap_canyourunit(games_scrapped=games_scrapped)
                games_scrapped = get_games_scrapped_number()
            except Exception as e:
                games_scrapped = get_games_scrapped_number()
                print(e)
                continue
    try:
        games_part_1 = pd.read_csv(f"{path}/games_part_1.csv")
        games_part_2 = pd.read_csv(f"{path}/games_part_2.csv")
    except Exception:
        print(e)
        pass

    try:
        games_part_1["Title"] = games_part_1["Title"].str.lower()
        games_part_2["Title"] = games_part_2["Title"].str.lower()

        # Merging games data files
        final_df = pd.merge(
            games_part_2,
            games_part_1,
            on="Title",
            how="outer",
            suffixes=("", "_part_2"),
        )
        final_df["Image"] = final_df["Image"].combine_first(final_df["Image_part_2"])
        final_df['Platforms'] = final_df['Platforms'].combine_first(final_df['Platforms_part_2'])

        # Deleting duplicated columns
        final_df.drop(["Image_part_2"], axis=1, inplace=True)
        final_df.drop(["Platforms_part_2"], axis=1, inplace=True)

        final_df["Title"] = final_df["Title"].str.capitalize()

        final_df.to_csv(f"{path}/games.csv", index=False)
        print(f"\nComplete games data file successfuly created !")

    except Exception as e:
        print(e)
        pass

    print(f"\n>>> Downloading Boavizta data file")
    if os.path.exists(f"{path}/boavizta_data.csv"):
        os.remove(f"{path}/boavizta_data.csv")

    wget.download(
        "https://raw.githubusercontent.com/Boavizta/environmental-footprint-data/main/boavizta-data-us.csv",
        f"{path}/boavizta_data.csv",
    )
    print(f"\nData scrapped and data files successfuly created in : {path}")


def clean_games_dataframe(dataframe):
    """
    This function returns a cleaned games dataframe.
    Input:
        dataframe : games dataframe to clean
    """
    dataframe = dataframe.astype("string")
    dataframe["Main Story (Hours)"] = pd.to_numeric(
        dataframe["Main Story (Hours)"].str.extract("(\d+)", expand=False),
        errors="coerce",
    )
    dataframe.fillna(
        value={
            "Main Story (Hours)": -1,
            "CPU": "",
            "GPU": "",
            "Platforms": "",
            "Genres": "",
            "RAM": "",
            "Image": "",
        },
        inplace=True,
    )

    return dataframe


def csv_to_json(folder_path: str = path):
    """
    This function converts all .csv files in the '_data/' folder to a .json format
    """
    for file in os.listdir(folder_path):
        if file.endswith('.csv'):
            file_path = os.path.join(folder_path, file)
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.replace(' ', '_')
            output_file_path = file_path.split(".")[0] + ".json"
            df.to_json(output_file_path,orient="records",indent=4, force_ascii=False)

    return


if __name__ == "__main__":
    create_data_files()
    add_consumption()
    csv_to_json()