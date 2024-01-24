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
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import undetected_chromedriver as uc

from database import connect_to_database

import wget
import os
from csv import DictWriter


# Root directory:
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path=f"{ROOT_DIR}/_data"

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
                dataframe=dataframe[dataframe["Model"] !="<NA>"]
                dataframe=dataframe[dataframe["Model"] !=""]

                dataframes.append(dataframe)

    df_processor=pd.concat(dataframes, ignore_index=True)



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

    df_processor = df_processor.drop_duplicates(subset='Model')

    # Data Postprocessing
    df_processor["Model"] = df_processor["Model"].str.extract(r'([^\[]*)')

    mask = df_processor["Model"].str.contains("^i\d")
    # Add "Core " for intel core i processors
    df_processor.loc[mask, "Model"] = "Core " + df_processor.loc[mask, "Model"]

    # Merging both dataframes
    df_processor_final = pd.merge(df_processor, df_processor2, on='Model', how='outer',suffixes=('', '_processor2'))
    df_processor_final['TDP (W)'] = df_processor_final['TDP (W)'].combine_first(df_processor_final['TDP (W)_processor2'])


    df_processor.to_csv(f"{path}/processors.csv",index=False)

    print(f"\nProcessors list data file successfuly created !")

    return
    
def scrap_graphiccards(path:str=path):

    url_graphic_card="https://en.wikipedia.org/wiki/List_of_Nvidia_graphics_processing_units"
    print(f"\n>>> Scrapping NVIDIA GPU list from : {url_graphic_card} ...")
    # HTTP request
    response_gc = requests.get(url_graphic_card)
    html_gc = BeautifulSoup(response_gc.text, 'html.parser')

    dataframes=[]
    # Finding all tables
    tables = html_gc.find_all('table')

    for table in tables:
        df=pd.read_html(StringIO(str(table)))
        df=pd.concat(df)
        try:
            df=df[["Model","TDP (Watts)"]]
            
            #dataframes.append(df)
            #df.info()
        except KeyError as k:
            if 'TDP (Watts)' not in df.columns and ('TDP (watts)') not in df.columns:
                df['TDP (Watts)'] = ""
            
            if 'Model' not in df.columns:
                df['Model'] = ""

            if ('TDP (watts)')  in df.columns:
                df=df[["Model","TDP (watts)"]]

            elif ('TDP (watts)') not in df.columns:
                df=df[["Model","TDP (Watts)"]]

            #dataframes.append(df)
            #df.info()

        df=df.dropna()
        df=df.astype('string')

        # Supprimer les colonnes en double
        df = df.loc[:, ~df.columns.duplicated()]

        dataframe=pd.DataFrame()

        dataframe['Model'] = df.iloc[:,0]

        dataframe['TDP (Watts)'] = df.iloc[:,1]

        df=dataframe
        dataframes.append(df)


    df_gc=pd.concat(dataframes, ignore_index=True)
    df_gc=df_gc[df_gc["Model"] !=""]
    df_gc=df_gc[df_gc["Model"] !="Model"]

    # Data Postprocessing
    df_gc["TDP (Watts)"] = df_gc["TDP (Watts)"].str.extract('(\d+)[\s-]?').astype(float)
    df_gc["Model"] = df_gc["Model"].str.extract(r'([^\[]*)')

    df_gc.to_csv(f"{path}/gpu.csv",index=False)

    print(f"\nGraphic cards list data file successfuly created !")
    return


def get_games_scrapped_number(file_path=f"{path}/games_part_2.csv"):
    # Return a dict of number of games scrapped by 1st letter
    
    df = pd.read_csv(file_path)

    # Counting games by title's 1st letter
    title_count_by_first_letter = df['Title'].astype(str).str[0].str.lower().value_counts().to_dict()

    return title_count_by_first_letter

def scrap_howlongtobbeat():

    print(f"\n>>> Scrapping games data from HowLongToBeat.com ...")

    games_list=[]
    game_page=1 # Initialisation of this variable
    max_games_per_page=30 # Maximum number of games per page to scrap for example. Default 30
    max_pages=3600 # Maximum number of games list pages. Default 3600

    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument("start-maximized")
    #chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2,})
    chrome_options.add_argument('--headless')

    driver = uc.Chrome(options=chrome_options)
    # sets timeout to 30
    driver.set_page_load_timeout(30)
    #driver = webdriver.Chrome(options=chrome_options)

    driver.get('https://howlongtobeat.com/?q=') # Uncomment to scrapp all games
    #driver.get('https://howlongtobeat.com/?q=a') # Scrapping only games starting with 'a' for exemple

    wait = WebDriverWait(driver, 10)

    # Accepting cookies
    try:
        print("\nAccepting cookies ...")
        cookies_button = wait.until(EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler')))
        cookies_button.click()
        wait.until(EC.invisibility_of_element_located((By.ID, 'onetrust-accept-btn-handler')))
        print("\nCookies accepted")
    except NoSuchElementException as e:
        print(e)
        print("\nNo cookies button detected")
        pass
    except Exception as e:
        print(e)
        pass


    try:
        page_items = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'back_darkish.GameCard_search_list__IuMbi')))
    except TimeoutException:
        page_items = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'back_darkish GameCard_search_list__IuMbi')))
    except Exception as e:
        driver.quit()
        raise e

    if len(page_items) >=max_games_per_page:
        iter_games=max_games_per_page
    else:
        iter_games= len(page_items)

    try:
        number_of_pages=wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="__next"]/div/main/div/div/div[6]/div/button[2]')))
        driver.execute_script("arguments[0].scrollIntoView();", number_of_pages)
        number_of_pages = int(number_of_pages.text.strip())
        print(f"Number of pages : {number_of_pages}")

    except Exception as e:
        driver.quit()
        raise e

    if number_of_pages >=max_pages:
        iter_pages=max_pages
    else:
        iter_pages= number_of_pages

    try:
        for p in range(iter_pages):
            print("Page number: ",game_page)
            print("Number of games in this page: ",len(page_items))
            for k in range(iter_games):

                try:
                    wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="search-results-header"]/ul')))
                except TimeoutException:
                    driver.refresh()
                    wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="search-results-header"]/ul')))
                except Exception as e:
                    raise Exception

                xpath = f'//*[@id="search-results-header"]/ul/li[{k+1}]/div/div[2]/h3/a'

                # Clicking on game page
                try:
                    # Waiting for the page to load
                    page_item = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

                    driver.execute_script("arguments[0].scrollIntoView();", page_item)
                    print("\nScrolled")
                    wait.until(EC.element_to_be_clickable(page_item))
                    print("\nWaited for element to be clickable")

                    # Scrapping game title
                    title = page_item.text.strip()
                    driver.execute_script("arguments[0].click();", page_item)
                    print("\nAccessed to game page")

                except TimeoutException as e:
                    print(f"Erreur lors du clic : {e}")
                    # Go back to games list page
                    driver.back()

                    # Retry clicking on the element
                    try:
                        # Waiting for the page to load
                        page_item = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

                        driver.execute_script("arguments[0].scrollIntoView();", page_item)
                        print("\nScrolled")
                        wait.until(EC.element_to_be_clickable(page_item))
                        print("\nWaited for element to be clickable")

                        # Scrapping game title
                        title = page_item.text.strip()
                        driver.execute_script("arguments[0].click();", page_item)
                        print("\nAccessed to game page")

                    except TimeoutException:
                        print("La nouvelle page n'a pas été correctement chargée après le clic.")
                        driver.back()
                        continue
                    
                    print("Clic réussi et nouvelle page chargée avec succès.")


                # Scrapping data :
                try:
                    games_data={}
                    games_data["Title"]=title
                    print("\nTreating : ",title)

                    # Waiting for the page to load
                    wait = WebDriverWait(driver, 10)

                    # Scrapping main story game time
                    try:                                                      
                        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/main/div[2]/div/div[2]/div[1]/ul/li[1]')))
                        main_story_time_element = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div/div[2]/div[1]/ul/li[1]')
                        print("Main Story found")                            
                    except TimeoutException:
                        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/main/div[2]/div/div[2]/div[1]/ul/div/li[1]')))
                        main_story_time_element = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div/div[2]/div[1]/ul/div/li[1]')
                        print("Main Story found")
                    except Exception:
                        pass
                    
                    driver.execute_script("arguments[0].scrollIntoView();", main_story_time_element)
                    table=main_story_time_element.text.strip()
                    mainstory = table.partition("Main Story")[2].strip()
                    try:
                        mainstory = mainstory.partition("Hours")[0].strip()
                    except Exception:
                        mainstory = table.partition("Main Story")[2].strip()
                    games_data["Main Story (Hours)"]=mainstory
                    print("Main Story scrapped")


                    # Scrapping plateform
                    try:
                        plateform_element = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div/div[2]/div[2]/div[4]')
                        driver.execute_script("arguments[0].scrollIntoView();", plateform_element)
                        table=plateform_element.text.strip()
                        plateform = table.partition("Platforms:")[2].strip()
                        games_data["Platforms"]=plateform
                        print("Platforms scrapped")
                    except Exception:
                        pass

                    # Scrapping genres
                    try:
                        genres_element = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div/div[2]/div[2]/div[5]')
                        driver.execute_script("arguments[0].scrollIntoView();", genres_element)
                        table=genres_element.text.strip()
                        genres = table.partition("Genres:")[2].strip()
                        games_data["Genres"]=genres
                        print("Genres scrapped")
                    except Exception:
                        pass

                    # Scrapping game cover
                    try:
                        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/main/div[2]/div/div[1]/div[1]/div[1]/img')))
                        cover_element = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div/div[1]/div[1]/div[1]/img')
                        print("Cover found")
                        driver.execute_script("arguments[0].scrollIntoView();", cover_element)
                        cover = cover_element.get_attribute('src')
                        print(cover)
                        cover = cover.split("?")[0]
                        games_data["Image"]=cover
                        print("Game cover scrapped")
                    except Exception:
                        pass

                    print(games_data)
                    games_list.append(games_data)

                    csv_file_path = f"{path}/games_part_1.csv"

                    # Vérifier si le fichier CSV existe
                    if os.path.exists(csv_file_path):
                        # Charger le fichier CSV existant
                        existing_df = pd.read_csv(csv_file_path)
                        try:
                            existing_df["Main Story (Hours)"] = existing_df["Main Story (Hours)"].str.extract('(\d+)').astype(int)
                        except Exception:
                            pass

                        # Vérifier si la ligne existe déjà
                        if not existing_df[existing_df['Title'] == games_data['Title']].empty:
                            print("Data already exists in the file")
                        else:
                            # Ajouter la ligne au fichier CSV
                            with open(csv_file_path, 'a', newline='', encoding='utf-8') as f_object:
                                dictwriter_object = DictWriter(f_object, fieldnames=list(games_data.keys()))

                                # Passer le dictionnaire comme argument à writerow()
                                dictwriter_object.writerow(games_data)
                                # Close the file object
                                f_object.close()
                                print(f"\nGame data added to {csv_file_path} !")

                    # Si le fichier CSV n'existe pas, le créer avec les données
                    else:
                        final_df = pd.DataFrame([games_data])
                        try:
                            final_df["Main Story (Hours)"] = final_df["Main Story (Hours)"].str.extract('(\d+)').astype(int)
                        except Exception:
                            pass
                        final_df.to_csv(csv_file_path, index=False, encoding='utf-8')
                        print(f"\nCSV file successfuly created at {csv_file_path} !")

                    wait = WebDriverWait(driver, 10)
                    
                except NoSuchElementException:
                    continue

                # Go back to games list page
                driver.back()
            
            wait = WebDriverWait(driver, 20)

            if game_page==1:
                next_page_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div/main/div/div/div[6]/div/button[1]')))
                next_page_button = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div/div/div[6]/div/button[1]')
            else:
                next_page_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div/main/div/div/div[6]/div/button[3]')))
                next_page_button = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div/div/div[6]/div/button[3]')

            driver.execute_script("arguments[0].scrollIntoView();", next_page_button)
            wait.until(EC.element_to_be_clickable(next_page_button))

            game_page+=1

            # Clicking on next page
            try:
                driver.execute_script("arguments[0].scrollIntoView();", next_page_button)
                wait.until(EC.element_to_be_clickable(next_page_button))
                driver.execute_script("arguments[0].click();", next_page_button)

            except Exception as e:
                raise Exception
            
    except Exception as e:
        print(e)
        pass

    finally:
        driver.quit()
        
    print(f"\nGames data file successfuly created !")


def scrap_canyourunit(games_scrapped:dict={}):

    print(f"\n>>> Scrapping games system requirements from the CanYouRunIt website ...")

    max=1000 #maximum number of games to scrap per page. Default 1000

    # Chrome options
    chrome_options = Options()  
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')   
    #chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2,})

    driver = uc.Chrome(options=chrome_options)

    # sets timeout to 30
    driver.set_page_load_timeout(30)
    #driver = webdriver.Chrome(options=chrome_options)

    requirements_list=[]
    letter_scrapped=list(games_scrapped.keys())

    url = "https://www.systemrequirementslab.com/all-games-list/?filter="
    end_list = ['a','b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    # Uncomment if you want to scrapp all games

    #end_list = ['a','b','c'] # Only scrapping 1 page for exemple

    # Removing pages if already scrapped

    def insert_to_csv_part_2(data_dict):
        csv_file_path = f"{path}/games_part_2.csv"

        # Vérifier si le fichier CSV existe
        if os.path.exists(csv_file_path):
            # Charger le fichier CSV existant
            print("Reading CSV file")
            existing_df = pd.read_csv(csv_file_path)
            print("CSV file readed !")
            # Vérifier si la ligne existe déjà
            if not existing_df[existing_df['Title'] == data_dict['Title']].empty:
                print("Data already exists in the file")

            else:
                # Ajouter la ligne au fichier CSV
                with open(csv_file_path, 'a', newline='', encoding='utf-8') as f_object:
                    dictwriter_object = DictWriter(f_object, fieldnames=list(data_dict.keys()))

                    # Passer le dictionnaire comme argument à writerow()
                    dictwriter_object.writerow(data_dict)
                    # Close the file object
                    f_object.close()
                    print(f"\nGame data added to {csv_file_path} !")
                    games_scrapped[letter]+=1

        # Si le fichier CSV n'existe pas, le créer avec les données
        else:
            final_df = pd.DataFrame([data_dict])
            final_df.to_csv(csv_file_path, index=False, encoding='utf-8')
            print(f"\nCSV file successfuly created at {csv_file_path} !")
            games_scrapped[letter]+=1

    try:

        if len(letter_scrapped)>1:
            for k in range(1,len(letter_scrapped)):
                if letter_scrapped[k] in end_list:
                    end_list.remove(letter_scrapped[k-1])   

        for letter in end_list: # Browsing all games pages starting with a specific caracter in end_list 
            driver.get(url + letter)
            wait = WebDriverWait(driver, 10)
            driver.implicitly_wait(10)

            if letter not in letter_scrapped:
                games_scrapped[letter]=0

            # Accepting cookies
            try:
                print("\nAccepting cookies ...")
                cookies_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]')))
                cookies_button.click()
                print("\nCookies accepted")
            except NoSuchElementException as e:
                print(e)
                print("\nNo cookies button detected")
                pass
            except Exception as e:
                print(e)
                pass
            
            try:
                # Waiting that class: "pt-3 pb-1 pl-3" is there
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'pt-3.pb-1.pl-3')))

                # Finding all element having the class: "page-item". It corresponds to games.
                page_items = driver.find_elements(By.CSS_SELECTOR, '.list-unstyled .page-item')
                print(f"\nNumber of games on this page : {len(page_items)}")
            except Exception as e:
                print("\nErreur inattendue : ",e)
                continue

            # Parcourir les éléments cliquables et cliquer sur chacun
            if len(page_items) >=max:
                iter=max
            else:
                iter= len(page_items)

            for k in range(games_scrapped[letter],iter):
                xpath=f'//*[@id="main-table"]/tbody/tr/td[2]/div/div[2]/main/div/div[1]/div/ul/li[{k+1}]/a'
                try:
                    page_item=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    print("\nWaiting for the next game ...")
                    # Scrapping game title
                    title = page_item.text.strip()

                except TimeoutException:
                    driver.refresh()
                    print("\nWaiting for the next game ...")
                    page_item=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    # Scrapping game title
                    title = page_item.text.strip()

                except Exception as e:
                    print(e)
                    continue

                # Clicking on game page
                try:
                    page_item=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    print(f"\n------------------------------\nTreating : {title}")
                    driver.execute_script("arguments[0].scrollIntoView();", page_item)
                    print("\nScrolled")
                    wait.until(EC.element_to_be_clickable(page_item))
                    print("\nWaited for element to be clickable")
                    #page_item.click()
                    driver.execute_script("arguments[0].click();", page_item)
                    print("\nAccessed to the game page")

                except TimeoutException as e:
                    print(f"Erreur lors du clic : {e}")
                    # Go back to games list page
                    #driver.back()
                    driver.execute_script("window.history.go(-1)")
                    print("\nRetour à la page précedente")

                    # Retry clicking on the element
                    try:
                        driver.execute_script("arguments[0].scrollIntoView();", page_item)
                        print("\nScrolled")
                        wait.until(EC.element_to_be_clickable(page_item))
                        print("\nWaited for element to be clickable")
                        #page_item.click()
                        driver.execute_script("arguments[0].click();", page_item)

                    except TimeoutException:
                        print("\nTimed out waiting for the element to be clickable. Skipping this game.")
                        driver.back()
                        continue

                    except Exception as e:
                        print(e)
                        continue
                    
                    print("Clic réussi et nouvelle page chargée avec succès.")
                except Exception as e:
                    print(e)
                    continue

                # Scrapping data :
                data_dict={}
                    
                try:

                    element_to_scrape = driver.find_element(By.XPATH, '//*[@id="main-table"]/tbody/tr/td[2]/div/div[2]/main/div/div[1]/div/div[4]/div[1]/div[1]')
                    driver.execute_script("arguments[0].scrollIntoView();", element_to_scrape)
                    
                    # Fulfilling dictionnary
                    table=element_to_scrape.text
                    result = [line.split(": ") for line in table.split("\n")[:4]]

                    # Scrapping game cover
                    try:
                        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="box-shots"]/img')))
                        cover_element = driver.find_element(By.XPATH, '//*[@id="box-shots"]/img')
                        # print("Cover found")
                        driver.execute_script("arguments[0].scrollIntoView();", cover_element)
                        cover = cover_element.get_attribute('src')
                        # print(cover)
                        cover = cover.split("?")[0]
                        print("Game cover scrapped")

                    except Exception as e:
                        print(f"Erreur inattendue : {e}")
                        cover=""
                        pass

                    try:
                        dict = {item[0]: item[1] for item in result}
                        data_dict['Title'] = title
                        if 'CPU' in dict.keys():
                            data_dict['CPU']=dict['CPU'] 
                        if 'VIDEO CARD' in dict.keys():
                            data_dict['GPU']=dict['VIDEO CARD']
                        if 'RAM' in dict.keys():
                            data_dict['RAM']=dict['RAM']

                        data_dict["Image"]=cover

                        print(data_dict)
                        requirements_list.append(data_dict)
                        
                        insert_to_csv_part_2(data_dict=data_dict)

                    except Exception as e:
                        print(f"Erreur inattendue : {e}")
                        try:
                            data_dict['Title'] = title
                        except Exception:
                            data_dict['Title']=""
                        data_dict['CPU']=""
                        data_dict['GPU']=""
                        data_dict['RAM']=""
                        try:
                            data_dict["Image"]=cover
                        except Exception:
                            data_dict["Image"]=""
                        
                        print(data_dict)
                        requirements_list.append(data_dict)

                        insert_to_csv_part_2(data_dict=data_dict)
                        

                except Exception as e:
                    print(f"Erreur inattendue : {e}")
                    try:
                        data_dict['Title'] = title
                    except Exception:
                        data_dict['Title']=""
                    data_dict['CPU']=""
                    data_dict['GPU']=""
                    data_dict['RAM']=""
                    try:
                        data_dict["Image"]=cover
                    except Exception:
                        data_dict["Image"]=""
                    
                    print(data_dict)
                    requirements_list.append(data_dict)

                    insert_to_csv_part_2(data_dict=data_dict)

                
                # Go back to games list page
                
                driver.execute_script("window.history.go(-1)")
    except Exception as e:
        print(f"Erreur inattendue globale : {e}")
        pass
    finally:
        driver.quit()

def scrap_data(bool_scrap_howlongtobeat:bool=False,bool_scrap_canyourunit:bool=False):
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


if __name__ == "__main__":
    scrap_data()

