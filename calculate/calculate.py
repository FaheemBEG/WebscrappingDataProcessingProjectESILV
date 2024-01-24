import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database import clean_games_dataframe

ROOT_DIR =os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(ROOT_DIR)
path=ROOT_DIR+"/_data"

def calculate_consumption(game_title:str,plateform:str):

    ## Loading data files
    boavizta=pd.read_csv(path+"/boavizta_data.csv")
    boavizta=boavizta.astype({"name":"string"})
    default_pc=boavizta[boavizta["name"]=="IdeaCentre T540 Gaming"]
    df_games=clean_games_dataframe(pd.read_csv(path+"/games.csv"))
    processors=pd.read_csv(path+"/processors.csv")
    gpu=pd.read_csv(path+"/gpu.csv")

    try:
        if not df_games[df_games["Title"].str.lower()==game_title.lower()].empty:
            games_data=df_games[df_games["Title"].str.lower()==game_title.lower()]
            print(games_data.head())
        else:
            print(f"\n{game_title} not found in our database")
            return None
    except Exception as e:
        print(e)
        print(f"\n{game_title} not found in our database")
        return None
    
    ### Default values
    if games_data["Platforms"].empty:
        print("EMPTY")
    gametime=15 # Game time default value

    # TDP (W)
    TDP_screen=12    # Source : Dell E2222H Monitor
    TDP_processor=23   # Source : Boavizta
    TDP_gpu=120         # Source : Gigabyte GTX 1060
    TDP_ssd=2.5      # Source : BarraCuda 120 SSD
    TDP_motherboard=80 # Source : Gigabyte Z370 AORUS Gaming
    TDP_ram=3          # Source : Buildcomputers
    TDP_powersupply=600
    TDP_light=40
    TDP_ps5=209.8   # Source : Sony
    TDP_ps4=97.2 # Source : Sony
    TDP_xbox_one= 150
    TDP_xbox_series_x= 200 # Source : TechPowerUp


    # Carbon footprint (kgCO2)
    co2_per_kwh_fr=0.04 # Source : EDF

    default_pc_co2=default_pc['gwp_total'].values[0]  # Source : IdeaCentre T540 Gaming (boavizta)
    ssd_co2=5.34     # Source : BarraCuda 120 SSD (6 kgCO2 *(100-11))
    screen_co2=357.445  # Source : Dell E2222H Monitor (485 kgCO2*(100-26.3))
    gpu_co2=33.68        # Source : Gigabyte GTX 1060 
    motherboard_co2=81   # Source : Gigabyte Z370 AORUS Gaming
    processor_co2=23     # Source : Boavizta
    box_co2=34           # Source : Boavizta
    ram_co2=11           # Source : Boavizta 
    xbox_one_co2=boavizta[boavizta["name"]=="Xbox One S"]["gwp_total"].values[0]*(1-boavizta[boavizta["name"]=="Xbox One S"]["gwp_use_ratio"].values[0])  # Extracting carbon footprint without usage percentage
    xbox_series_x_co2=boavizta[boavizta["name"]=="Xbox Series X"]["gwp_total"].values[0]*(1-boavizta[boavizta["name"]=="Xbox Series X"]["gwp_use_ratio"].values[0]) # Extracting carbon footprint without usage percentage
    ps4_co2= xbox_one_co2 # No Data
    ps5_co2=xbox_series_x_co2 # No Data

        ## Values according to game and plateform
    if not games_data["Main Story (Hours)"].empty and games_data["Main Story (Hours)"].any():
        try:
            gametime=games_data["Main Story (Hours)"].values[0]
        except Exception as e:
            print(e)
            pass
    else:
        print("No game time information")
    

    if not games_data["CPU"].empty:
        try:
            TDP_processor=processors.at[games_data["CPU"].values[0],"TDP (W)"]
        except Exception as e:
            pass
    
    if not games_data["GPU"].empty:
        try:
            TDP_gpu=gpu.at[games_data["GPU"].values[0],"TDP (Watts)"]
        except Exception as e:
            pass
    
    if not pd.isnull(games_data["Platforms"].values[0]) and not plateform.lower() in games_data["Platforms"].values[0].lower():
        print(f"\nThe platform {plateform} is not supported by {game_title}")
        return None

    if "playstation 4" in plateform.lower():
        TDP_plateform=TDP_ps4
        plateform_co2=ps4_co2

    elif "playstation 5" in plateform.lower():
        TDP_plateform=TDP_ps5
        plateform_co2=ps5_co2

    elif "xbox one" in plateform.lower():
        TDP_plateform=TDP_xbox_one
        plateform_co2=xbox_one_co2

    elif "xbox series x" in plateform.lower():
        TDP_plateform=TDP_xbox_series_x
        plateform_co2=xbox_series_x_co2

    else: # PC by default, even if not platform because games are really often on PC
        TDP_plateform=TDP_powersupply+TDP_gpu+TDP_motherboard+TDP_processor+TDP_ram+TDP_ssd
        plateform_co2=box_co2+gpu_co2+processor_co2+ssd_co2+ram_co2+motherboard_co2
        #plateform_co2=default_pc_co2
    

    Total_power=TDP_plateform+TDP_screen
    #print(f"Puissance totale : {Total_power} W")

    kWh=round(Total_power*gametime/1000)
    light_time=round((kWh*1000/TDP_light)/24) #In days

    Total_co2=round(plateform_co2+screen_co2+co2_per_kwh_fr*kWh)

    calcul_dict={"Carbon_footprint_kgco2":Total_co2,"Total_kWh":kWh,"light_time_days":light_time}
    print(f"""En jouant à {games_data["Title"].values[0]} durant {gametime} heures, tu consommeras:\n{kWh} kWh d'electricité, soit {kWh*3600} kJ d'energie.\nCela correspond à laisser la lumière de ton joli salon allumé pendant {light_time} jours !\nL'empreinte carbone de ton materiel et de ton temps de jeu est estimé à environ {Total_co2} kg de CO2 émis ! Pense à la planète !""")

    return calcul_dict

def add_consumption(games_file_path: str = path+"/games_extrait.csv"):

    df_games = pd.read_csv(games_file_path)
    consoles = ["PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X"]

    if "carbon_footprint_pc" not in df_games.columns:
        # Creating new_columns applying calculate_consumption function
        df_games["carbon_footprint_pc"] = df_games.apply(lambda row: calculate_consumption(row["Title"], "PC")["Carbon_footprint_kgco2"], axis=1)

        # Saving dataframe to csv
        df_games.to_csv(games_file_path, index=False)
        print(f"\nColumn 'carbon_footprint_pc' added to {games_file_path}!")
    else:
        print("Column 'carbon_footprint_pc' already exists in the dataframe.")

    # Add a column for each column
    for console in consoles:
        # Définir la fonction calculate_consumption pour la console spécifique
        def calculate_consumption_console(row):
            if pd.notna(row["Platforms"]):  # Vérifier si la valeur n'est pas NaN
                plateform = row["Platforms"].lower()
                if console.lower() in plateform:
                    return calculate_consumption(row["Title"], plateform=console)["Carbon_footprint_kgco2"]
            return None  # Retourner None si la valeur est NaN

        # Appliquer la fonction calculate_consumption_console à chaque ligne du dataframe
        df_games[f"carbon_footprint_{console.lower().replace(' ', '_')}"] = df_games.apply(calculate_consumption_console, axis=1)




dic=calculate_consumption("Interstellar transport company","Pc")
print(dic)
#add_consumption()