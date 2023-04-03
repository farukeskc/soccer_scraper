from selenium import webdriver
import uuid
import time
import csv
import pandas as pd
from src.player_name_url import PlayerNameUrl
from src.player import Player
from src.stat import Stats
from src.goal import Goal
from src.national_team_career import NationalTeamCareer
from src.injury import Injury
from src.market_value import MarketValue
from src.suspensions import Suspension
from src.transfer import Transfer
from src.achievement import Achievement
from src.squad_number import SquadNumber
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import threading


def reload(driver: webdriver.Firefox):
    driver.refresh()

def table_next_page(driver):
    next_page_button = driver.find_element(By.CLASS_NAME, "tm-pagination__list-item--icon-next-page")
    next_page_button.click()
    time.sleep(0.5)
    while (True):
        try:
            driver.find_element(By.CLASS_NAME, "grid-view-loading")
        except:
            break

def error_handler(driver):
    while True:
        if driver.title == "Error | Transfermarkt" or driver.find_element(By.TAG_NAME, "h1").text == "503 Service Unavailable":
            reload(driver)
        else:
            break

def close_popup(driver: webdriver.Firefox):
    wait = WebDriverWait(driver, 60)
    iframe = wait.until(EC.presence_of_element_located((By.ID, "sp_message_iframe_764226")))
    driver.switch_to.frame(iframe)
    sp_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sp_choice_type_11")))
    sp_button.click()
    time.sleep(5)
    driver.switch_to.default_content()

def get_market_values(driver: webdriver.Firefox, player_id, profile_url):
    wait = WebDriverWait(driver, 30)
    market_values = []
    market_value_url = profile_url.replace("profil", "marktwertverlauf")
    driver.get(market_value_url)

    error_handler(driver)

    try:
        chart = driver.find_element(By.ID, "subnavigation")
        chart.location_once_scrolled_into_view
        time.sleep(2)
        # driver.execute_script("arguments[0].scrollIntoView();", chart)

        market_values_on_chart = driver.find_element(By.CLASS_NAME, "highcharts-markers").find_elements(By.TAG_NAME,
                                                                                                        "image")
        actions = ActionChains(driver)

        for point_on_chart in market_values_on_chart:
            actions.move_to_element(point_on_chart).perform()
            time.sleep(0.05)
            hover_menu_items = driver.find_elements(By.CLASS_NAME, "highcharts-tooltip")[1].find_element(By.TAG_NAME,
                                                                                                         "span").find_elements(
                By.TAG_NAME, "b")
            market_value = MarketValue(player_id=player_id, date=hover_menu_items[0].text,
                                       value=hover_menu_items[1].text, club=hover_menu_items[2].text,
                                       age=hover_menu_items[3].text)
            market_values.append(market_value)
        return market_values
    except:
        return -1



def objects_to_dataframe(objects_list, name):
    # Get the attribute names of the first object in the list
    column_names = [attr for attr in dir(objects_list[0]) if
                    not callable(getattr(objects_list[0], attr)) and not attr.startswith("__")]

    # Create an empty DataFrame with the column names
    df = pd.DataFrame(columns=column_names)

    # Add rows to the DataFrame for each object in the list
    for obj in objects_list:
        row_data = [getattr(obj, attr) for attr in column_names]
        df = df.append(pd.Series(row_data, index=column_names), ignore_index=True)

    df.to_csv("outputs/{}.csv".format(name), index=False)

def split_list(lst, n):
    """
    Split the given list into n parts.

    Args:
        lst (list): The list to split.
        n (int): The number of parts to split the list into.

    Returns:
        list: A list of n sublists.
    """
    # Calculate the length of each sublist
    size = len(lst) // n

    # Determine any remainder elements
    remainder = len(lst) % n

    # Initialize the output list
    result = []

    # Initialize the starting and ending indices
    start = 0
    end = size

    # Iterate over the number of parts
    for i in range(n):
        # If there are remainder elements, add one to this sublist
        if i < remainder:
            end += 1

        # Add the current sublist to the output list
        result.append(lst[start:end])

        # Update the starting and ending indices for the next sublist
        start = end
        end += size

    return result

def hello(links: list, index:int):
    all_market_values = []


    firefox_options = Options()
    # firefox_options.headless = True
    firefox_options.binary_location = "C:\Program Files\Firefox Developer Edition/firefox.exe"

    firefox_profile = webdriver.FirefoxProfile()
    # firefox_profile.set_preference("permissions.default.image", 2)

    driver = webdriver.Firefox(options=firefox_options, firefox_profile=firefox_profile)
    driver.get("https://www.transfermarkt.com/")

    close_popup(driver)

    for profile_url in links:
        player_id = uuid.uuid4()

        # MARKET VALUE
        market_values = get_market_values(driver, player_id, profile_url)
        if market_values == -1:
            print("Exception on market_values of {}".format(player.full_name))
        else:
            all_market_values = all_market_values + market_values


        print(index,":" ,len(all_players)/len(links), "%")

    objects_to_dataframe(all_market_values, "MarketValues" + str(index))



def run_threads():
    num_threads = int(input("Enter the number of threads to create: "))
    links = pd.read_csv("outputs/PlayerNameUrl.csv")['url'].values.tolist()
    splitted_links = split_list(links, num_threads)

    # Create threads for each browser
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=hello, args=(splitted_links[i], i,))
        threads.append(thread)

    # Start the threads
    for thread in threads:
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # for i in range(num_threads):
    #     threading.Thread(target=openBrowser(i)).start()
    #
    # while True:
    #     check = True
    #     for key in browserOpenningThreads.keys():
    #         if browserOpenningThreads[key].is_alive():
    #             check = False
    #     if check:
    #         print("All browsers opened")
    #         break
    #
    # for i in range(num_threads):
    #     threading.Thread(target=hello(drivers[i], splitted_links[i], i)).start()


run_threads()



# GET LINKS

# def text_to_price(value: str):
#     return int(float(value[1:value.find("m")]) * 1000000)
#
#
# def get_links(driver: webdriver.Firefox):
#     value = 200000000
#     data = []
#     while value > 5000000:
#         driver.get("https://www.transfermarkt.com/detailsuche/spielerdetail/suche")
#         max_market_value_input = driver.find_element(By.ID, "Detailsuche_maxMarktwert")
#         max_market_value_input.clear()
#         max_market_value_input.send_keys(value)
#         driver.find_element(By.XPATH, "/html/body/div[2]/main/form[2]/div[5]/div[1]/div/div[2]/input").click()
#
#         a = wait.until_not(EC.presence_of_element_located((By.CLASS_NAME, "icon_logo")))
#
#         while True:
#             if driver.title == "Error | Transfermarkt":
#                 reload(driver)
#             else:
#                 break
#
#         while True:
#             player_rows = driver.find_element(By.CLASS_NAME, "items").find_element(By.TAG_NAME, "tbody").find_elements(
#                 By.CSS_SELECTOR,
#                 "[class*=odd], [class*=even]")
#
#             for row in player_rows:
#                 columns = row.find_elements(By.TAG_NAME, "td")
#                 new_player_row = PlayerNameUrl(
#                     name=columns[1].find_element(By.CLASS_NAME, "hauptlink").find_element(By.TAG_NAME, "a").text,
#                     url=columns[1].find_element(By.CLASS_NAME, "hauptlink").find_element(By.TAG_NAME,
#                                                                                          "a").get_attribute("href"),
#                     market_value=text_to_price(columns[-1].text))
#                 if new_player_row not in data:
#                     data.append(new_player_row)
#
#             try:
#                 next_page_button = driver.find_element(By.CLASS_NAME, "tm-pagination__list-item--icon-next-page")
#                 next_page_button.click()
#                 time.sleep(0.5)
#                 while (True):
#                     try:
#                         driver.find_element(By.CLASS_NAME, "grid-view-loading")
#                     except:
#                         break
#             except:
#                 break
#
#         value = text_to_price(columns[-1].text)
#
#     return data
#
#
# def get_links_for_small_market_values(driver: webdriver.Firefox):
#     data = []
#     for value in range(5000000, 500000, -500000):
#         for position in ["Exclude position", "Goalkeeper", "Defence", "Midfield", "Attack"]:
#             for i in range(3):
#                 driver.get("https://www.transfermarkt.com/detailsuche/spielerdetail/suche")
#
#                 position_field = driver.find_element(By.XPATH,
#                                                      "/html/body/div[2]/main/form[2]/div[5]/div[1]/div/div[1]/div/div/div[1]/div[2]/div/ul/li/input")
#
#                 position_field.clear()
#                 position_field.send_keys(position)
#                 time.sleep(0.1)
#                 position_field.send_keys(Keys.RETURN)
#
#                 driver.find_element(By.ID, "Detailsuche_fuss_id_" + str(i)).click()
#
#                 min_market_value_input = driver.find_element(By.ID, "Detailsuche_minMarktwert")
#                 min_market_value_input.clear()
#                 min_market_value_input.send_keys(value)
#
#                 max_market_value_input = driver.find_element(By.ID, "Detailsuche_maxMarktwert")
#                 max_market_value_input.clear()
#                 max_market_value_input.send_keys(value)
#                 driver.find_element(By.XPATH, "/html/body/div[2]/main/form[2]/div[5]/div[1]/div/div[2]/input").click()
#
#                 a = wait.until_not(EC.presence_of_element_located((By.CLASS_NAME, "icon_logo")))
#
#                 while True:
#                     if driver.title == "Error | Transfermarkt":
#                         reload(driver)
#                     else:
#                         break
#
#                 while True:
#                     try:
#                         player_rows = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "items"))).find_element(
#                             By.TAG_NAME,
#                             "tbody").find_elements(
#                             By.CSS_SELECTOR,
#                             "[class*=odd], [class*=even]")
#                     except:
#                         break
#
#                     for row in player_rows:
#                         columns = row.find_elements(By.TAG_NAME, "td")
#                         new_player_row = PlayerNameUrl(
#                             name=columns[1].find_element(By.CLASS_NAME, "hauptlink").find_element(By.TAG_NAME,
#                                                                                                   "a").text,
#                             url=columns[1].find_element(By.CLASS_NAME, "hauptlink").find_element(By.TAG_NAME,
#                                                                                                  "a").get_attribute(
#                                 "href"),
#                             market_value=text_to_price(columns[-1].text))
#                         if new_player_row not in data:
#                             data.append(new_player_row)
#
#                     try:
#                         next_page_button = driver.find_element(By.CLASS_NAME,
#                                                                "tm-pagination__list-item--icon-next-page")
#                         next_page_button.click()
#                         time.sleep(0.5)
#                         while (True):
#                             try:
#                                 driver.find_element(By.CLASS_NAME, "grid-view-loading")
#                             except:
#                                 break
#                     except:
#                         break
#     return data
