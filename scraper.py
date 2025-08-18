# special version of Selenium Chromedriver to bypass Cloudflare anti-bot
import undetected_chromedriver as uc

# library to parse HTML into searchable tree
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from io import StringIO

# prevent timeout error
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# change this to scrape years dynamically and load in
# format: years = [2024, 2023] corresponds to 2024-2025 season and 2023-2024 season
years = [2022, 2021]
all_matches = []
# this should be the URL for the season of years[0]
standings_url = "https://fbref.com/en/comps/9/2022-2023/2022-2023-Premier-League-Stats"

# create browser driver with custom user-agent string to appear as regular user
options = uc.ChromeOptions()
options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
)
driver = uc.Chrome(options=options)

# for each season:
for year in years:
    # open Prem Leage data page in browser
    driver.get(standings_url)

    # wait at least 30 seconds until the page has a table with class stats_table
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.stats_table"))
    )

    # give HTML source to BS to parse, first HTML table is the Prem one
    soup = BeautifulSoup(driver.page_source, "html.parser")
    standings_table = soup.select("table.stats_table")[0]

    # extract + build all href links, only for squads in the Prem
    links = [l.get("href") for l in standings_table.find_all("a")]
    links = [l for l in links if l and "/squads/" in l]
    team_urls = [f"https://fbref.com{l}" for l in links]

    # extract + build link for previous season, update url to prev season
    previous_season = soup.select("a.prev")[0].get("href")
    standings_url = f"https://fbref.com{previous_season}"

    # extract clean team name from each URL
    for team_url in team_urls:
        team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")

        # load each team page
        driver.get(team_url)

        # prevent timeout, wait until Scores and Fixtures table is visible
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, "//table[contains(., 'Scores & Fixtures')]")
            )
        )

        # read match schedule table into pd dataframe
        matches = pd.read_html(StringIO(driver.page_source), match="Scores & Fixtures")[
            0
        ]

        # extract link to the shooting stats page
        soup = BeautifulSoup(driver.page_source, "html.parser")
        links = [l.get("href") for l in soup.find_all("a")]
        links = [l for l in links if l and "all_comps/shooting/" in l]
        shooting_url = "https://fbref.com" + links[0]
        driver.execute_script("window.location.href = arguments[0];", shooting_url)

        # prevent timeout, wait until Shooting table is visible
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, "//table[contains(., 'Shooting')]")
            )
        )

        # read shooting table into pandas, remove multi-level header for indexing
        shooting = pd.read_html(StringIO(driver.page_source), match="Shooting")[0]
        shooting.columns = shooting.columns.droplevel()

        # FROM match JOIN shooting(info) ON match.date = shooting.date
        # some teams missing shooting data, skip if N/A
        try:
            team_data = matches.merge(
                shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date"
            )
        except ValueError:
            continue

        # filter non-Prem games(ex: cup matches, etc)
        team_data = team_data[team_data["Comp"] == "Premier League"]

        # add season and team name columns
        team_data["Season"] = year
        team_data["Team"] = team_name

        # add team dataframe to all_matches list
        all_matches.append(team_data)

        # avoid IP bans with randomized delay
        time.sleep(random.uniform(3, 6))

driver.quit()

# data processing + save to CSV
match_df = pd.concat(all_matches)
match_df.columns = [c.lower() for c in match_df.columns]
filename = f"matches{min(years)%100}{max(years)%100}.csv"
match_df.to_csv(filename)
