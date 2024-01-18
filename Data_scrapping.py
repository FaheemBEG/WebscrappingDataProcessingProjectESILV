import requests
import pandas as pd
from io import StringIO

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

import wget
import os

path="C:/Users/fahee/OneDrive/Bureau/ETUDE/S9/Webscapping_and_Data_Processing/WebscrappingDataProcessingProjectESILV/_data"

def scrap_processors_en():
    
    def multicolumn(column:str,level:int):
        multicolumns=[]
        if level==1:
            return column
        
        for k in range(level):
            multicolumns.append(column)
        return tuple(multicolumns)

    url_processor_list=["https://en.wikipedia.org/wiki/List_of_Intel_processors"]
    
    df_processor=pd.DataFrame()
    for url in url_processor_list:
        print(f"\n>>> Scrapping Intel processors list from : {url} ...")
        # Faire la requête HTTP et obtenir le contenu de la page
        response_processor = requests.get(url)
        html_processor = BeautifulSoup(response_processor.text, 'html.parser')

        dataframes=[]
        # Finding all tables
        tables = html_processor.find_all('table',class_=lambda x: x and "wikitable" in x)

        for table in tables:
            df=pd.read_html(StringIO(str(table)))
            df=pd.concat(df)


            try:
                if 'Processor family' in df.columns and 'Model' in df.columns:
                    df["Model"]=df[multicolumn("Processor family",df.columns.nlevels)]+ ' '+ df[multicolumn("Model",df.columns.nlevels)]
                
                df=df[["Model","TDP (W)"]]
                df=df.dropna()
                df=df.astype('string')
                
                df1=pd.DataFrame()
                df1['Model'] = df.iloc[:, 0]
                df1['TDP (W)'] = df.iloc[:, 1]
                dataframes.append(df1)

            except KeyError as k:
                    
                if 'TDP (W)' not in df.columns and 'TDP' not in df.columns:
                    df[multicolumn("TDP (W)",df.columns.nlevels)]= ""

                # if 'Processor family' in df.columns and 'Model' in df.columns:
                #     df["Model"]=df[multicolumn("Processor family",df.columns.nlevels)]+ ' '+ df[multicolumn("Model",df.columns.nlevels)]
                
                if 'Model' not in df.columns:
                    try:
                        df["Model"]=df[multicolumn("Model",df.columns.nlevels)]
                    except Exception:
                        df['Model'] = ""

                try:
                    df=df[["Model","TDP (W)"]]

                except KeyError as k:
                    try:
                        df=df[["Model","TDP"]]
                    except Exception:
                        pass

                df=df.dropna()
                df=df.astype('string')
                dataframe=pd.DataFrame()

                # Ajouter les données des colonnes "(Modèle, Modèle)" à "Modèle"
                dataframe['Model'] = df.iloc[:, 0]
                dataframe['TDP (W)'] = df.iloc[:, 1]
                dataframes.append(dataframe)

    df_processor=pd.concat(dataframes, ignore_index=True)

    df_processor=df_processor[df_processor["Model"] !="<NA>"]
    df_processor=df_processor[df_processor["Model"] !=""]

    return df_processor

def scrap_processors(path:str=path):
    url_processor_list=["https://fr.wikipedia.org/wiki/Liste_des_microprocesseurs_Intel"]    
    
    for url in url_processor_list:
        print(f"\n>>> Scrapping Intel processors list from : {url} ...")

        # Faire la requête HTTP et obtenir le contenu de la page
        response_processor = requests.get(url)
        html_processor = BeautifulSoup(response_processor.text, 'html.parser')

        dataframes=[]
        # Finding all tables
        tables = html_processor.find_all('table',class_=lambda x: x and "wikitable" in x)

        for table in tables:
            df=pd.read_html(StringIO(str(table)))
            df=pd.concat(df)

            try:
                df=df[["Modèle","TDP "]]
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
    df_processor['TDP'] = pd.to_numeric(df_processor['TDP'].str.rstrip('W').str.replace(',', '.'), errors='coerce').fillna(65)
    # On fixe à 65W les TDP non mentionnés

    df_processor['Modèle'] = df_processor['Modèle'].str.replace('-', " ", regex=True)
    df_processor = df_processor.reset_index(drop=True)

    df_processor=df_processor.rename(columns={"Modèle":"Model","TDP":"TDP (W)"})

    df_processor2=scrap_processors_en()
    df_processor=pd.concat([df_processor,df_processor2],ignore_index=True)

    df_processor = df_processor.drop_duplicates(subset='Model')
    df_processor.to_csv(f"{path}/processors.csv",index=False)

    print(f"\nProcessors list data file successfuly created !")

    return
    
def scrap_graphiccards(path:str=path):

    return

def scrap_howlongtobbeat():

    print(f"\n>>> Scrapping games data from HowLongToBeat.com ...")

    # Configuration pour le mode headless
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://howlongtobeat.com/?q=recently%2520updated')
    #driver.get('https://howlongtobeat.com/?q=')
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

    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options)
    requirements_list=[]
    url = "https://www.systemrequirementslab.com/all-games-list/?filter="
    end_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


    for letter in end_list: # Browsing all games pages starting with a specific caracter in end_list 
        driver.get(url + letter)
        wait = WebDriverWait(driver, 10)
        driver.implicitly_wait(10)

        # Accepting cookies
        try:
            driver.find_element(By.XPATH,'//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]').click()
        except NoSuchElementException:
            pass

        # Waiting that class: "pt-3 pb-1 pl-3" is there
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'pt-3.pb-1.pl-3')))

        # Finding all element having the class: "page-item". It corresponds to games.
        page_items = driver.find_elements(By.CSS_SELECTOR, '.list-unstyled .page-item')

        max=1 #maximum number of games to scrap per page

        # Parcourir les éléments cliquables et cliquer sur chacun
        if len(page_items) >=max:
            iter=max

        else:
            iter= len(page_items)
        for k in range(iter):
            xpath=f'//*[@id="main-table"]/tbody/tr/td[2]/div/div[2]/main/div/div[1]/div/ul/li[{k+1}]/a'
            page_item=driver.find_element(By.XPATH, xpath)

            # Scrapping game title
            title = page_item.text.strip()

            # Clicking on game page
            try:
                driver.execute_script("arguments[0].scrollIntoView();", page_item)
                wait.until(EC.element_to_be_clickable(page_item))
                driver.execute_script("arguments[0].click();", page_item)

            except Exception as e:
                print(f"Erreur lors du clic : {e}")
                continue

            # Scrapping data :
            try:
                element_to_scrape = driver.find_element(By.XPATH, '//*[@id="main-table"]/tbody/tr/td[2]/div/div[2]/main/div/div[1]/div/div[4]/div[1]/div[1]')
                driver.execute_script("arguments[0].scrollIntoView();", element_to_scrape)

                # Fulfilling dictionnary
                table=element_to_scrape.text
                result = [line.split(": ") for line in table.split("\n")[:4]]
                data_dict={}
                dict = {item[0]: item[1] for item in result}

                data_dict['Title'] = title
                if 'CPU' in dict.keys():
                    data_dict['CPU']=dict['CPU'] 
                if 'VIDEO CARD' in dict.keys():
                    data_dict['GPU']=dict['VIDEO CARD']
                if 'RAM' in dict.keys():
                    data_dict['RAM']=dict['RAM']

                requirements_list.append(data_dict)

            except NoSuchElementException:
                pass

            # Go back to games list page
            driver.back()

    driver.quit()
    requirements_df = pd.DataFrame(requirements_list)
    final_df = pd.merge(df, requirements_df, on='Title', how='outer')

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
