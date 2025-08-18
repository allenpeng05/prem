# special version of Selenium Chromedriver to bypass Cloudflare anti-bot
import undetected_chromedriver as uc

# library to parse HTML into searchable tree
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# prevent timeout error
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

standings = []

url = "https://fbref.com/en/comps/9/2023-2024/2023-2024-Premier-League-Stats"

# create browser driver with custom user-agent string to appear as regular user
options = uc.ChromeOptions()
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
)
driver = uc.Chrome(options=options)
years = list(range(2023, 2013, -1))

for year in years:
    driver.get(url)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.stats_table"))
    )
    soup = BeautifulSoup(driver.page_source, "html.parser")
    standings_table = soup.select("table.stats_table")[0]

    # extract the correct season
    season = url.split("/")[6]
    year = season.split("-")[0]

    # get previous season's link
    previous_season = soup.select("a.prev")[0].get("href")
    url = f"https://fbref.com{previous_season}"

    rows = standings_table.find_all("tr")
    for row in rows:
        rank_tag = row.find("th", {"data-stat": "rank"})
        team_link = row.find("a")
        if rank_tag and team_link:
            rank = int(rank_tag.text.strip())
            team = team_link.text.strip()
            standings.append({"season": year, "team": team, "rank": rank})

    time.sleep(random.uniform(3, 6))

standings_df = pd.DataFrame(standings)
filename = f"standings_{min(years)}_to_{max(years)}.csv"
standings_df.to_csv(filename, index=False)
