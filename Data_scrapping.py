from bs4 import BeautifulSoup
import requests
import pandas as pd
from io import StringIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import wget
import os

path="C:/Users/fahee/OneDrive/Bureau/ETUDE/S9/Webscapping_and_Data_Processing/WebscrappingDataProcessingProjectESILV/_data"

def scrap_processors(path:str=path):
    url_processor_list=["https://fr.wikipedia.org/wiki/Liste_des_microprocesseurs_Intel"]    
    
    for url in url_processor_list:
        print(f"\n>>> Scrapping Intel processors list from : {url} ...")

        # Faire la requête HTTP et obtenir le contenu de la page
        response_processor = requests.get(url)
        html_processor = BeautifulSoup(response_processor.text, 'html.parser')

        dataframes=[]
        # Finding all tables
        tables = html_processor.find_all('table')

        for table in tables:
            df=pd.read_html(StringIO(str(table)))
            df=pd.concat(df)

            try:
                df=df[["Modèle","TDP"]]
                df=df.dropna()
                df=df.astype('string')
                dataframes.append(df)

            except KeyError as k:
                if 'TDP' not in df.columns:
                    df['TDP'] = ""
                
                if 'Modèle' not in df.columns:
                    if 'Nom' in df.columns and 'Numéro de modèle' in df.columns:
                        df['Modèle']=df['Numéro de modèle']+' '+ df['Nom']
                    else:
                        df['Modèle'] = ""
                
                df=df[["Modèle","TDP"]]
                df=df.astype('string')
                dataframes.append(df)

        df_processor=pd.concat(dataframes, ignore_index=True)

    # Supprimer les colonnes en double
    df_processor = df_processor.loc[:, ~df_processor.columns.duplicated()]

    dataframe=pd.DataFrame()
    # Ajouter les données des colonnes "(Modèle, Modèle)" à "Modèle"
    dataframe['Modèle'] = df_processor.iloc[:,2]

    # Ajouter les données des colonnes "(TDP, TDP)" à "TDP"
    dataframe['TDP'] = df_processor.iloc[:,3]

    df_processor=pd.concat([df_processor,dataframe], ignore_index=True)

    # Supprimer les colonnes temporaires "(Modèle, Modèle)" et "(TDP, TDP)"
    df_processor = df_processor.drop(df_processor.columns[[2,3]], axis=1)

    df_processor = df_processor[df_processor['TDP'].str.endswith('W')]
    df_processor['Modèle'] = df_processor['Modèle'].str.replace('-', " ", regex=True)
    df_processor = df_processor.reset_index(drop=True)

    df_processor.to_csv(f"{path}/processors.csv",index=False)

    print(f"\nProcessors list data file successfuly created !")
    return

def scrap_howlongtobbeat():

    print(f"\n>>> Scrapping games data from HowLongToBeat.com ...")

    # Configuration pour le mode headless
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://howlongtobeat.com/?q=recently%2520updated')
    wait = WebDriverWait(driver, 10)
    popup_button = wait.until(EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler')))
    popup_button.click()    
    wait.until(EC.invisibility_of_element_located((By.ID, 'onetrust-accept-btn-handler')))
    max_for_test = 5 #A ENLEVER LORSQUE LA PHASE DE DEV SERA FINIE
    games_data = {}
    next_page_button = driver.find_elements(By.XPATH, "//button[@class='Pagination_right__GwBE_ form_button Pagination_inactive__dnoZF' and text()='>']")
    cpt = 0
    while next_page_button and cpt <= max_for_test:
        cpt+=1
        next_page_button = driver.find_elements(By.XPATH, "//button[@class='Pagination_right__GwBE_ form_button Pagination_inactive__dnoZF' and text()='>']")
        list_items = driver.find_elements(By.XPATH, "//div[@class='content_100']/ul/li")
        for item in list_items:
            title = item.find_element(By.XPATH, ".//h3").text.strip()
            game_details = {}
            time_details_div = item.find_element(By.XPATH, ".//div[@class='GameCard_search_list_details_block__XEXkr']")
            time_details = time_details_div.find_elements(By.XPATH, ".//div[@class='GameCard_search_list_tidbit__0r_OP text_white shadow_text']")
            for detail in time_details:
                category = detail.text.strip()
                time = detail.find_element(By.XPATH, "./following-sibling::div").text.strip()
                game_details[category] = time
            games_data[title] = game_details
        wait = WebDriverWait(driver, 10)
        next_page_button[0].click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='Pagination_right__GwBE_ form_button Pagination_inactive__dnoZF' and text()='>']")))
    driver.quit()

    df = pd.DataFrame.from_dict(games_data, orient='index')
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Title'}, inplace=True)

    return df

def scrap_canyourunit():

    df=scrap_howlongtobbeat()

    # WORK IN PROGRESS
    print(f"\n>>> Scrapping games system requirements from the CanYouRunIt website ...")

    # Configuration pour le mode headless
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://www.systemrequirementslab.com/cyri')
    wait = WebDriverWait(driver, 10)
    popup_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'css-47sehv')))
    popup_button.click()
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'css-47sehv')))
    requirements_list = []
    for title in df.head(1)['Title']:
        input_field = driver.find_element(By.ID, 'select-repo-ts-control')
        input_field.clear()
        input_field.send_keys(title)
        # if exist
        element_to_click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "select-repo-opt-1")))
        element_to_click.click()
        #element_to_click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "button-cyri-bigblue")))
        element_to_click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='button-cyri-bigblue' or @id='requirements-button']")))
        element_to_click.click()
        latest_graphics_cards_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='container']//div[@class='row']//ul")))
        requirements = driver.find_elements(By.XPATH, "//div[@class='container']//div[@class='row']//ul")[1]
        results = requirements.text.strip()
        result = [line.split(": ") for line in results.split("\n")[:4]]
        data_dict = {item[0]: item[1] for item in result}
        data_dict['Title'] = title
        requirements_list.append(data_dict)
    driver.quit()
    requirements_df = pd.DataFrame(requirements_list)
    final_df = pd.merge(df, requirements_df, on='Title', how='left')

    final_df.to_csv(f"{path}/games.csv",index=False)

    print(f"\nGames data file successfuly created !")
    
    return

def scrap_data():
    print(f"\n Creating data files . . .")
    scrap_processors()
    scrap_canyourunit()
    print(f"\n>>> Downloading Boavizta data file")

    if os.path.exists(f"{path}/boavizta-data.csv"):
        os.remove(f"{path}/boavizta-data.csv")

    wget.download("https://raw.githubusercontent.com/Boavizta/environmental-footprint-data/main/boavizta-data-us.csv",f"{path}/boavizta-data.csv")
    print(f"\nData scrapped and data files successfuly created in : {path}")


if __name__ == "__main__":
    scrap_data()
