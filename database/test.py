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
from database import connect_to_database
import wget
import os
import sqlite3

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path=ROOT_DIR+"/_data"

def scrap_howlongtobbeat():

    print(f"\n>>> Scrapping games data from HowLongToBeat.com ...")

    games_list=[]
    game_page=1 # Initialisation of this variable
    max_games_per_page=30 # Maximum number of games per page to scrap for example. Default 30
    max_pages=15 # Maximum number of games list pages. Default 3600

    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options)
    #driver.get('https://howlongtobeat.com/?q=') # Uncomment to scrapp all games
    driver.get('https://howlongtobeat.com/?q=a') # Scrapping only games starting with 'a' for exemple

    wait = WebDriverWait(driver, 10)

    # Accepting cookies
    try:
        popup_button = wait.until(EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler')))
        popup_button.click()
        wait.until(EC.invisibility_of_element_located((By.ID, 'onetrust-accept-btn-handler')))
    except NoSuchElementException:
        pass

    try:
        page_items = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'back_darkish.GameCard_search_list__IuMbi')))
    except TimeoutException:
        page_items = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'back_darkish GameCard_search_list__IuMbi')))

    if len(page_items) >=max_games_per_page:
        iter_games=max_games_per_page
    else:
        iter_games= len(page_items)

    try:
        number_of_pages=wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="__next"]/div/main/div/div/div[6]/div/button[2]')))
        driver.execute_script("arguments[0].scrollIntoView();", number_of_pages)
        number_of_pages = int(number_of_pages.text.strip())
        print(f"Number of pages : {number_of_pages}")

    except NoSuchElementException:
        raise Exception

    if number_of_pages >=max_pages:
        iter_pages=max_pages
    else:
        iter_pages= number_of_pages

    for p in range(iter_pages):
        print("Page number: ",game_page)
        print("Number of games in this page: ",len(page_items))
        for k in range(iter_games):

            try:
                wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="search-results-header"]/ul')))
            except Exception:
                raise Exception

            xpath=f'//*[@id="search-results-header"]/ul/li[{k+1}]/div/div[2]/h3/a'

            # Waiting for the page to load
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

            page_item=driver.find_element(By.XPATH, xpath)

            # Clicking on game page
            try:
                driver.execute_script("arguments[0].scrollIntoView();", page_item)
                wait.until(EC.element_to_be_clickable(page_item))

                # Scrapping game title
                title = page_item.text.strip()
                driver.execute_script("arguments[0].click();", page_item)

            except Exception as e:
                print(f"Erreur lors du clic : {e}")
                continue

            # Scrapping data :
            try:
                games_data={}
                games_data["Title"]=title
                # print(title)
                # Waiting for the page to load
                wait = WebDriverWait(driver, 10)

                # Scrapping main story game time
                try:                                                      
                    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/main/div[2]/div/div[2]/div[1]/ul/li[1]')))
                    main_story_time_element = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div/div[2]/div[1]/ul/li[1]')
                    # print("Main Story found")                            
                except TimeoutException:
                    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/main/div[2]/div/div[2]/div[1]/ul/div/li[1]')))
                    main_story_time_element = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div/div[2]/div[1]/ul/div/li[1]')
                    # print("Main Story found")
                
                driver.execute_script("arguments[0].scrollIntoView();", main_story_time_element)
                table=main_story_time_element.text.strip()
                mainstory = table.partition("Main Story")[2].strip()
                try:
                    mainstory = mainstory.partition("Hours")[0].strip()
                except Exception:
                    mainstory = table.partition("Main Story")[2].strip()
                games_data["Main Story (Hours)"]=mainstory
                # print("Main Story scrapped")


                # Scrapping plateform
                plateform_element = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div/div[2]/div[2]/div[4]')
                driver.execute_script("arguments[0].scrollIntoView();", plateform_element)
                table=plateform_element.text.strip()
                plateform = table.partition("Platforms:")[2].strip()
                games_data["Platforms"]=plateform
                # print("Platforms scrapped")

                # Scrapping genres
                genres_element = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div/div[2]/div[2]/div[5]')
                driver.execute_script("arguments[0].scrollIntoView();", genres_element)
                table=genres_element.text.strip()
                genres = table.partition("Genres:")[2].strip()
                games_data["Genres"]=genres
                # print("Genres scrapped")

                print(games_data)
                games_list.append(games_data)

                wait = WebDriverWait(driver, 10)
                
            except NoSuchElementException:
                pass

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

        except NoSuchElementException:
            raise Exception
        
    driver.quit()

    df_games = pd.DataFrame(games_list)
    df_games.reset_index(inplace=True,drop=True)
    try:
        df_games["Main Story (Hours)"] = df_games["Main Story (Hours)"].str.extract('(\d+)').astype(int)
    except Exception:
        pass
    
    df_games.to_csv(f"{path}/games_temp.csv",index=False)

    print(f"\nGames data file successfuly created !")
    return df_games


def get_tables_sqlite(path=path+"/WebScrapping.db"):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # Exécutez la requête pour récupérer les tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Affichez les noms des tables
    for table in tables:
        print(table[0])

    conn.close()

get_tables_sqlite()