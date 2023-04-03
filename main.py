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
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
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
    try:
        while True:
            if driver.title == "Error | Transfermarkt" or driver.find_element(By.TAG_NAME,
                                                                              "h1").text == "503 Service Unavailable":
                reload(driver)
            else:
                break
    except:
        driver.save_screenshot("{}.jpeg".format(str(time.time())))

def close_popup(driver: webdriver.Firefox):
    wait = WebDriverWait(driver, 60)
    iframe = wait.until(EC.presence_of_element_located((By.ID, "sp_message_iframe_764226")))
    driver.switch_to.frame(iframe)
    sp_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sp_choice_type_11")))
    sp_button.click()
    time.sleep(5)
    driver.switch_to.default_content()

def get_player(driver: webdriver.Firefox, player_id: str, profile_url: str):
    date_of_birth = ""
    place_of_birth = ""
    height = ""
    citizenship = ""
    foot = ""
    agent = ""
    current_club = ""
    outfitter = ""
    main_position = ""
    other_position1 = ""
    other_position2 = ""
    current_international = ""

    full_name = driver.find_element(By.CLASS_NAME, "data-header__headline-wrapper").text
    if full_name.find("#") != -1:
        full_name = full_name[full_name.find(" ") + 1:]

    info_table_spans = driver.find_element(By.CLASS_NAME, "info-table").find_elements(By.TAG_NAME, "span")
    for i, span in enumerate(info_table_spans):
        if span.text == "Date of birth:":
            date_of_birth = info_table_spans[i + 1].text
        elif span.text == "Place of birth:":
            place_of_birth = info_table_spans[i + 1].text
        elif span.text == "Height:":
            height = info_table_spans[i + 1].text
        elif span.text == "Citizenship:":
            citizenship = info_table_spans[i + 1].find_element(By.TAG_NAME, "img").get_attribute("title")
        elif span.text == "Foot:":
            foot = info_table_spans[i + 1].text
        elif span.text == "Player agent:":
            agent = info_table_spans[i + 1].text
        elif span.text == "Current club:":
            current_club = info_table_spans[i + 1].text
        elif span.text == "Outfitter:":
            outfitter = info_table_spans[i + 1].text

    try:
        position_box = driver.find_elements(By.CLASS_NAME, "detail-position__position")
        main_position = position_box[0].text
    except:
        return -1

    try:
        other_position1 = position_box[2].text
        other_position2 = position_box[3].text
        current_international = \
            driver.find_element(By.CLASS_NAME, "data-header__details").find_elements(By.CLASS_NAME,
                                                                                     "data-header__items")[
                2].find_element(By.TAG_NAME, "a").text
    except:
        pass

    return Player(player_id=player_id, full_name=full_name, date_of_birth=date_of_birth, place_of_birth=place_of_birth,
                  height=height,
                  citizenship=citizenship, foot=foot, agent=agent, current_club=current_club, outfitter=outfitter,
                  main_position=main_position, other_position1=other_position1, other_position2=other_position2,
                  current_international=current_international, transfermarket=profile_url)


def get_stats(driver: webdriver.Firefox, player_id: str, profile_url: str):
    wait = WebDriverWait(driver, 50)
    stats = []
    stats_url = profile_url.replace("profil", "leistungsdatendetails")
    driver.get(stats_url)

    error_handler(driver)

    time.sleep(1)

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "tm-tab")))
        driver.find_elements(By.CLASS_NAME, "tm-tab")[1].click()
    except:
        return -1

    error_handler(driver)

    try:
        stats_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "items")))
        table_rows = stats_table.find_element(By.TAG_NAME, "tbody").find_elements(By.CSS_SELECTOR,
                                                                                  "[class*=odd], [class*=even]")

        for stat_row in table_rows:
            columns = stat_row.find_elements(By.TAG_NAME, "td")
            player_stats = Stats(player_id=player_id, season=columns[0].text,
                                 competition=columns[2].find_element(By.TAG_NAME, "a").text,
                                 club=columns[3].find_element(By.TAG_NAME, "a").get_attribute("title"),
                                 squad=columns[4].text,
                                 appearances=columns[5].find_element(By.TAG_NAME, "a").text,
                                 point_per_game=columns[6].text,
                                 goals=columns[7].text, assists=columns[8].text, own_goals=columns[9].text,
                                 substitutions_on=columns[10].text, substitutions_off=columns[11].text,
                                 yellow=columns[12].text,
                                 second_yellow=columns[13].text, red=columns[14].text,
                                 penalty_goals=columns[15].text,
                                 minutes_per_goal=columns[16].text, minutes=columns[17].text)
            stats.append(player_stats)
        return stats
    except:
        return -1


def get_goals(driver: webdriver.Firefox, player_id, profile_url):
    wait = WebDriverWait(driver, 80)
    goals = []
    goals_url = profile_url.replace("profil", "alletore")
    driver.get(goals_url)

    error_handler(driver)

    time.sleep(1)

    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "tm-tab")))
        driver.find_elements(By.CLASS_NAME, "tm-tab")[1].click()
    except:
        return -1

    error_handler(driver)

    wait.until(EC.title_contains("All goals (Detailed view) | Transfermarkt"))

    try:
        goals_table_rows = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "responsive-table"))).find_element(
            By.TAG_NAME,
            "tbody").find_elements(
            By.TAG_NAME, "tr")

        for goal_row in goals_table_rows:
            cls = goal_row.get_attribute("style")
            if cls == "":
                goal_columns = goal_row.find_elements(By.TAG_NAME, "td")

                goal_assist = ""
                try:
                    goal_assist = goal_columns[-1].find_element(By.TAG_NAME, "a").text
                except:
                    pass

                if len(goal_columns) > 5:

                    player_goal = Goal(player_id=player_id,
                                       competition=goal_columns[1].find_element(By.TAG_NAME, "a").text,
                                       matchday=goal_columns[2].find_element(By.TAG_NAME, "a").text,
                                       date=goal_columns[3].text,
                                       venue=goal_columns[4].text,
                                       club=goal_columns[5].find_element(By.TAG_NAME, "a").get_attribute("title"),
                                       against=goal_columns[-7].find_element(By.TAG_NAME, "a").text,
                                       result=goal_columns[-6].find_element(By.TAG_NAME, "span").text,
                                       position=goal_columns[-5].find_element(By.TAG_NAME, "a").get_attribute("title"),
                                       minute=goal_columns[-4].text, at_score=goal_columns[12].text,
                                       type_of_goal=goal_columns[-2].text,
                                       assist=goal_assist)
                elif len(goal_columns) == 5:
                    player_goal.minute = goal_columns[1].text
                    player_goal.at_score = goal_columns[2].text
                    player_goal.type_of_goal = goal_columns[3].text
                    player_goal.assist = goal_assist
                goals.append(player_goal)
        return goals
    except:
        return -1


def get_injury_history(driver: webdriver.Firefox, player_id, profile_url):
    wait = WebDriverWait(driver, 30)
    injuries = []
    injury_history_url = profile_url.replace("profil", "verletzungen")
    driver.get(injury_history_url)

    error_handler(driver)

    time.sleep(1)

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "tm-tab")))
        driver.find_elements(By.CLASS_NAME, "tm-tab")[1].click()
    except:
        return -1

    error_handler(driver)

    wait.until(EC.title_contains("Injury history (Detailed view) | Transfermarkt"))

    while (True):
        try:
            injury_table_rows = driver.find_element(By.CLASS_NAME, "items").find_element(By.TAG_NAME,
                                                                                         "tbody").find_elements(
                By.TAG_NAME, "tr")

            for injury_row in injury_table_rows:
                injury_columns = injury_row.find_elements(By.TAG_NAME, "td")

                injury = Injury(player_id=player_id, season=injury_columns[0].text, injury=injury_columns[1].text,
                                start_date=injury_columns[2].text, end_date=injury_columns[3].text,
                                days=injury_columns[4].text, games_missed=injury_columns[5].text)

                injuries.append(injury)

            table_next_page(driver)
        except:
            break
    return injuries


def get_suspensions(driver: webdriver.Firefox, player_id, profile_url):
    wait = WebDriverWait(driver, 30)
    suspensions = []
    suspensions_url = profile_url.replace("profil", "ausfaelle")
    driver.get(suspensions_url)

    error_handler(driver)

    while (True):
        try:
            suspensions_table_rows = driver.find_element(By.CLASS_NAME, "items").find_element(By.TAG_NAME,
                                                                                              "tbody").find_elements(
                By.TAG_NAME, "tr")

            for suspension_row in suspensions_table_rows:
                suspension_columns = suspension_row.find_elements(By.TAG_NAME, "td")

                competition = ""
                try:
                    competition = suspension_columns[2].find_element(By.TAG_NAME,
                                                                     "img").get_attribute("title")
                except:
                    pass
                suspension = Suspension(player_id=player_id, season=suspension_columns[0].text,
                                        suspension=suspension_columns[1].text,
                                        competition=competition,
                                        start_date=suspension_columns[3].text, end_date=suspension_columns[4].text,
                                        days=suspension_columns[5].text, games_missed=suspension_columns[6].text, )

                suspensions.append(suspension)

            table_next_page(driver)
        except:
            break

    return suspensions


def get_market_values(driver: webdriver.Firefox, player_id, profile_url):
    wait = WebDriverWait(driver, 60)
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


def get_transfers(driver: webdriver.Firefox, player_id, profile_url):
    wait = WebDriverWait(driver, 40)
    transfers = []
    transfers_url = profile_url.replace("profil", "transfers")
    driver.get(transfers_url)

    error_handler(driver)

    try:
        transfers_table_cells = driver.find_element(By.CLASS_NAME,
                                                    "viewport-tracking").find_elements(
            By.CSS_SELECTOR,
            "div[class*=tm-player-transfer-history-grid]:not([class*=tm-player-transfer-history-grid--heading])")
        for i in range(7, len(transfers_table_cells) - 4, 7):
            transfers.append(Transfer(player_id=player_id, season=transfers_table_cells[i].text,
                                      date=transfers_table_cells[i + 1].text, left=transfers_table_cells[i + 2].text,
                                      joined=transfers_table_cells[i + 3].text,
                                      market_value=transfers_table_cells[i + 4].text,
                                      fee=transfers_table_cells[i + 5].text))
        return transfers
    except:
        return -1


def get_national_team_carrers(driver: webdriver.Firefox, player_id, profile_url):
    wait = WebDriverWait(driver, 30)
    national_team_carrers = []
    national_carrer_url = profile_url.replace("profil", "nationalmannschaft")
    driver.get(national_carrer_url)

    error_handler(driver)

    try:
        national_carrer_table_rows = driver.find_element(By.XPATH,
                                                         "/html/body/div[2]/main/div[3]/div[1]/div[1]/table").find_element(
            By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

        for i in range(1, len(national_carrer_table_rows), 2):
            columns = national_carrer_table_rows[i].find_elements(By.TAG_NAME, "td")

            coach = ""
            try:
                coach = columns[6].find_element(By.TAG_NAME, "a").text
            except:
                pass

            debut = ""
            try:
                debut = columns[3].find_element(By.TAG_NAME, "a").text
            except:
                debut = columns[3].text

            national_team_carrers.append(
                NationalTeamCareer(player_id=player_id, national_team=columns[2].find_element(By.TAG_NAME, "a").text,
                                   debut=debut,
                                   matches=columns[4].find_element(By.TAG_NAME, "a").text,
                                   goals=columns[5].find_element(By.TAG_NAME, "a").text,
                                   coach=coach, age_at_debut=columns[7].text))
        return national_team_carrers
    except:
        return -1

def get_achievements(driver: webdriver.Firefox, player_id, profile_url):
    wait = WebDriverWait(driver, 30)
    achievements = []
    achievements_url = profile_url.replace("profil", "erfolge")
    driver.get(achievements_url)
    try:
        boxes = driver.find_elements(By.CLASS_NAME, "large-6")
        for box in boxes:
            header = box.find_element(By.CLASS_NAME, "content-box-headline").text
            achievement_name = header[(header.find(" ") + 1):]
            awards = box.find_element(By.CLASS_NAME, "auflistung").find_element(By.TAG_NAME, "tbody").find_elements(
                By.TAG_NAME, "tr")
            for award in awards:
                achievements.append(Achievement(player_id=player_id, achievement=achievement_name,
                                                season=award.find_element(By.TAG_NAME, "td").text))
        return achievements
    except:
        return -1

def get_squad_numbers(driver: webdriver.Firefox, player_id, profile_url):
    wait = WebDriverWait(driver, 30)
    squad_numbers = []
    squad_numbers_url = profile_url.replace("profil", "rueckennummern")
    driver.get(squad_numbers_url)
    try:
        rows = driver.find_element(By.CLASS_NAME, "items").find_element(By.TAG_NAME, "tbody").find_elements(
            By.TAG_NAME,
            "tr")
        for row in rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            squad_numbers.append(SquadNumber(player_id=player_id, season=columns[0].text,
                                             club=columns[2].find_element(By.TAG_NAME, "a").text
                                             , number=columns[3].text))
        return squad_numbers
    except:
        return -1


def objects_to_dataframe(objects_list, name):
    # Get the attribute names of the first object in the list
    column_names = [attr for attr in dir(objects_list[0]) if
                    not callable(getattr(objects_list[0], attr)) and not attr.startswith("__")]

    # Create a list of DataFrames for each object in the list
    dfs = [pd.DataFrame([[getattr(obj, attr) for attr in column_names]], columns=column_names) for obj in objects_list]

    # Concatenate the list of DataFrames into one DataFrame
    df = pd.concat(dfs, ignore_index=True)

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
    all_players = []
    all_goals = []
    all_stats = []
    all_injuries = []
    all_suspensions = []
    # all_market_values = []
    all_transfers = []
    all_national_team_carrers = []
    all_achievements = []
    all_squad_numbers = []

    # firefox_options = Options()
    # firefox_options.headless = True
    # firefox_options.binary_location = "C:\Program Files\Mozilla Firefox/firefox.exe"
    #
    # firefox_profile = webdriver.FirefoxProfile()
    # firefox_profile.set_preference("permissions.default.image", 2)

    # driver = webdriver.Firefox(options=firefox_options, firefox_profile=firefox_profile)

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://www.transfermarkt.com/")

    close_popup(driver)

    links = links[800:900]

    for profile_url in links:
        player_id = uuid.uuid4()
        driver.get(profile_url)

        # GENERAL INFORMATION
        player = get_player(driver, player_id, profile_url)
        if player == -1:
            continue
        else:
            all_players.append(player)

        # GET STATS
        stats = get_stats(driver, player_id, profile_url)
        if stats == -1:
            print("Exception on stats of {}".format(player.full_name))
        else:
            all_stats = all_stats + stats

        # GET ALL GOALS
        if not player.main_position == "Goalkeeper":
            goals = get_goals(driver, player_id, profile_url)
            if goals == -1:
                print("Exception on goals of {}".format(player.full_name))
            else:
                all_goals = all_goals + goals
        else:
            pass


        # GET ALL INJURY HISTORY
        injuries = get_injury_history(driver, player_id, profile_url)
        if injuries == -1:
            print("Exception on injuries of {}".format(player.full_name))
        else:
            all_injuries = all_injuries + injuries

        # SUSPENSIONS
        suspensions = get_suspensions(driver, player_id, profile_url)
        if suspensions == -1:
            print("Exception on suspensions of {}".format(player.full_name))
        else:
            all_suspensions = all_suspensions + suspensions


        # MARKET VALUE
        # market_values = get_market_values(driver, player_id, profile_url)
        # if market_values == -1:
        #     print("Exception on market_values of {}".format(player.full_name))
        # else:
        #     all_market_values = all_market_values + market_values

        # TRANSFERS
        transfers = get_transfers(driver, player_id, profile_url)
        if transfers == -1:
            print("Exception on transfers of {}".format(player.full_name))
        else:
            all_transfers = all_transfers + transfers


        # NATIONAL TEAM CARRER
        national_team_carrers = get_national_team_carrers(driver, player_id, profile_url)
        if national_team_carrers == -1:
            print("Exception on national_team_carrers of {}".format(player.full_name))
        else:
            all_national_team_carrers = all_national_team_carrers + national_team_carrers


        # ACHIEVEMENTS
        achievements = get_achievements(driver, player_id, profile_url)
        if achievements == -1:
            print("Exception on achievements of {}".format(player.full_name))
        else:
            all_achievements = all_achievements + achievements


        # SQUAD NUMBERS
        squad_numbers = get_squad_numbers(driver, player_id, profile_url)
        if squad_numbers == -1:
            print("Exception on squad numbers of {}".format(player.full_name))
        else:
            all_squad_numbers = all_squad_numbers + squad_numbers

        print(index,":" ,len(all_players)/len(links)*100, "%")

    objects_to_dataframe(all_players, "Players" + str(index))
    objects_to_dataframe(all_goals, "Goals" + str(index))
    objects_to_dataframe(all_stats, "AllStats" + str(index))
    objects_to_dataframe(all_injuries, "Injuries" + str(index))
    objects_to_dataframe(all_suspensions, "Suspensions" + str(index))
    # objects_to_dataframe(all_market_values, "MarketValues" + str(index))
    objects_to_dataframe(all_transfers, "Transfers" + str(index))
    objects_to_dataframe(all_national_team_carrers, "NationalTeamCarrer" + str(index))
    objects_to_dataframe(all_achievements, "Achievements" + str(index))
    objects_to_dataframe(all_squad_numbers, "SquadNumbers" + str(index))

    driver.close()


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
