import pandas as pd
import os
import sys
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT_DIR =os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path=ROOT_DIR+"/_data"


def standardize_models(data_string, model_type):
    if pd.isna(data_string):
        return None
    pattern = ''
    if model_type == 'gpu':
        pattern = r'([A-Za-z]+\s*[A-Za-z]*\s*\d+[A-Za-z]*)'  # GPU pattern
    elif model_type == 'cpu':
        pattern = r'([A-Za-z]+\s*\d+\s*[A-Za-z]*\s*\d*[A-Za-z]*)'  # Modified CPU pattern
    extracted_models = re.findall(pattern, data_string)
    standardized_models = [model.replace(" ", "").upper() for model in extracted_models]
    return standardized_models

def find_best_match(standardized_models, model_df):
    if not standardized_models:
        return None
    model_matches = {model: 0 for model in model_df['Model']}
    for s_model in standardized_models:
        for model in model_df['Model']:
            if s_model in model.upper().replace(" ", ""):
                model_matches[model] += 1
    best_match = max(model_matches, key=model_matches.get)
    return best_match if model_matches[best_match] > 0 else None


def calculate_consumption(game_row, boavizta):
    """
    This function calculate the estimation of the carbon footprint of a game by using :
    Gametime, the total platform's carbon footprint without the percentage of usage and other default values.
    It is almost impossible to estimate the carbon footprint of components because of the lack of transparency by manufacturers.
    """
    # Extraction des données nécessaires de la ligne de jeu
    platform = game_row['Platforms']
    main_story_hours = float(game_row['Main Story (Hours)'])

    TDP_processor = game_row['CPU_TDP'] if game_row['CPU_TDP'] > 0 else 23
    TDP_gpu = game_row['GPU_TDP'] if game_row['GPU_TDP'] > 0 else 120

    # Détermination des TDP par défaut
    TDP_screen = 12    # Dell E2222H Monitor
    #TDP_processor = 23   # Boavizta
    #TDP_gpu = 120         # Gigabyte GTX 1060
    TDP_ssd = 2.5      # BarraCuda 120 SSD
    TDP_motherboard = 80 # Gigabyte Z370 AORUS Gaming
    TDP_ram = 3          # Buildcomputers
    TDP_powersupply = 600
    TDP_light = 40
    TDP_ps5 = 209.8   # Sony
    TDP_ps4 = 97.2    # Sony
    TDP_xbox_one = 150
    TDP_xbox_series_x = 200 # TechPowerUp

    # Carbon footprint constants
    co2_per_kwh_fr = 0.04 # EDF

    # Default PC carbon footprint
    default_pc_co2 = 675
    ssd_co2 = 5.34
    screen_co2 = 357.445
    gpu_co2 = 33.68
    motherboard_co2 = 81
    processor_co2 = 23
    box_co2 = 34
    ram_co2 = 11
    xbox_one_co2 = 431.775
    xbox_series_x_co2 = 179.85

    ps4_co2 = xbox_one_co2  # No specific data
    ps5_co2 = xbox_series_x_co2  # No specific data

    # Game time determination
    gametime = 15  # Default value
    if main_story_hours and main_story_hours != -1 and not pd.isna(main_story_hours):
        gametime = main_story_hours


    # Platform specific adjustments
    if "playstation 4" in platform.lower():
        TDP_platform = TDP_ps4
        platform_co2 = ps4_co2
    elif "playstation 5" in platform.lower():
        TDP_platform = TDP_ps5
        platform_co2 = ps5_co2
    elif "xbox one" in platform.lower():
        TDP_platform = TDP_xbox_one
        platform_co2 = xbox_one_co2
    elif "xbox series x" in platform.lower():
        TDP_platform = TDP_xbox_series_x
        platform_co2 = xbox_series_x_co2
    else:
        platform = "PC"
        TDP_platform = TDP_powersupply + TDP_gpu + TDP_motherboard + TDP_processor + TDP_ram + TDP_ssd
        platform_co2 = box_co2 + gpu_co2 + processor_co2 + ssd_co2 + ram_co2 + motherboard_co2

    # Calculations
    total_power = TDP_platform + TDP_screen
    kWh = round(total_power * gametime / 1000)
    light_time = round((kWh * 1000 / TDP_light) / 24)  # In days
    total_co2 = round(platform_co2 + screen_co2 + co2_per_kwh_fr * kWh)

    # Result dictionary
    calcul_dict = {
        "Carbon_footprint_kgco2": total_co2,
        "Total_kWh": kWh,
        "light_time_days": light_time,
        "gametime": gametime,
        "platform": platform
    }

    return calcul_dict

def add_consumption(data_path:str = path):
    # Chargement du DataFrame de jeux
    df_games = pd.read_csv(data_path + "/games.csv")
    processors = pd.read_csv(data_path + "/processors.csv")
    gpu = pd.read_csv(data_path + "/gpu.csv")
    boavizta = pd.read_csv(data_path + "/boavizta_data.csv")
    boavizta = boavizta.astype({"name": "string"})

    # Standardisation et correspondance des modèles GPU et CPU
    df_games['Standardized_GPU'] = df_games['GPU'].apply(lambda x: standardize_models(x, 'gpu'))
    df_games['Standardized_CPU'] = df_games['CPU'].apply(lambda x: standardize_models(x, 'cpu'))
    df_games['Matched_GPU'] = df_games['Standardized_GPU'].apply(lambda x: find_best_match(x, gpu))
    df_games['Matched_CPU'] = df_games['Standardized_CPU'].apply(lambda x: find_best_match(x, processors))

    # Jointures pour ajouter la valeur TDP du GPU et du CPU
    df_games = df_games.merge(gpu, left_on='Matched_GPU', right_on='Model', how='left')
    df_games.rename(columns={'TDP (Watts)': 'GPU_TDP'}, inplace=True)
    df_games.drop('Model', axis=1, inplace=True)

    df_games = df_games.merge(processors, left_on='Matched_CPU', right_on='Model', how='left')
    df_games.rename(columns={'TDP (W)': 'CPU_TDP'}, inplace=True)
    df_games.drop(['Model', 'Standardized_GPU', 'Matched_GPU', 'Standardized_CPU', 'Matched_CPU'], axis=1, inplace=True)

    # Convertir CPU_TDP et GPU_TDP en numérique
    df_games['CPU_TDP'] = pd.to_numeric(df_games['CPU_TDP'], errors='coerce')
    df_games['GPU_TDP'] = pd.to_numeric(df_games['GPU_TDP'], errors='coerce')

    # Remplacer les valeurs NaN par 0 après la conversion
    df_games['CPU_TDP'].fillna(0, inplace=True)
    df_games['GPU_TDP'].fillna(0, inplace=True)

    df_games["Main Story (Hours)"] = pd.to_numeric(df_games["Main Story (Hours)"].str.extract('(\d+)', expand=False), errors='coerce')

    # Liste des consoles à traiter
    consoles = ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X"]

    # Application de calculate_consumption à chaque ligne de df_games
    for console in consoles:
        column_name = f"carbon_footprint_{console.lower().replace(' ', '_')}"
        if column_name not in df_games.columns:
            df_games[column_name] = df_games.apply(
                lambda row: calculate_consumption(row, boavizta)["Carbon_footprint_kgco2"]
                if pd.notna(row["Platforms"]) and console.lower() in row["Platforms"].lower()
                else None,
                axis=1
            )
        column_name = f"Total_kWh_{console.lower().replace(' ', '_')}"
        if column_name not in df_games.columns:
            df_games[column_name] = df_games.apply(
                lambda row: calculate_consumption(row, boavizta)["Total_kWh"]
                if pd.notna(row["Platforms"]) and console.lower() in row["Platforms"].lower()
                else None,
                axis=1
            )


    # Enregistrement des modifications dans le fichier CSV
    df_games.to_csv(data_path + "/games_consumption.csv", index=False)