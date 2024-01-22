import pandas as pd
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
path=ROOT_DIR+"/_data"

def calculate_consumption(game_title:str,plateform:str):

    df_games=pd.read_csv(path+"/games.csv")
    games_data=df_games[df_games["Title"]==game_title]

    ### Default values

    gametime=15 

    # TDP (W)
    TDP_screen=12    # Source : Dell E2222H Monitor
    TDP_processor=23   # Source : Boavizta
    TDP_gpu=120         # Source : Gigabyte GTX 1060
    TDP_ssd=2.5      # Source : BarraCuda 120 SSD
    TDP_motherboard=80 # Source : Gigabyte Z370 AORUS Gaming
    TDP_ram=3          # Source : Buildcomputers

    # Carbon footprint (kgCO2)
    co2_per_kwh_fr=0.04 # Source : EDF
    ssd_co2=5.34     # Source : BarraCuda 120 SSD (6 kgCO2 *(100-11))
    screen_co2=357.445  # Source : Dell E2222H Monitor (485 kgCO2*(100-26.3))
    gpu_co2=33.68        # Source : Gigabyte GTX 1060 
    motherboard_co2=81   # Source : Gigabyte Z370 AORUS Gaming
    processor_co2=23     # Source : Boavizta
    box_co2=34           # Source : Boavizta
    ram_co2=11           # Source : Boavizta

    

    Total_power=TDP_powersupply+TDP_graphic_card+TDP_screen+TDP_harddrive+TDP_processor
    print(f"Puissance totale : {Total_power} W")

    kWh=round(Total_power*time/1000)
    TDP_light=40
    TDP_light/1000
    light_time=round((kWh*1000/TDP_light)/24) #In days
