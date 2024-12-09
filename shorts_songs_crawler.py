import logging
import os
import re
from datetime import datetime, timedelta
from time import sleep

import pycountry
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.wpewebkit.webdriver import WebDriver

from logger import Logger


class ShortsSongsCrawler:
    countries: list = []
    current_country: None | str = None
    weeks: list = []
    current_week: str
    driver: WebDriver
    logger: logging.Logger
    dataset_path: str = "/home/filipe/Pesquisas/short-videos/dataset"
    YT_CHARTS_URL = "https://charts.youtube.com/charts/TopShortsSongs/global/daily"
    is_collecting_shorts_songs: bool = True
    max_previous_day_str: str

    def __init__(self, max_previous_day_str: str) -> None:
        self.countries = []
        self.current_country = None
        self.weeks = []
        self.logger = Logger.get_logger(__name__)
        self.max_previous_day_str = max_previous_day_str

    def setup(self, download_dir: str):
        options = webdriver.FirefoxOptions()
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", download_dir)
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk", "application/pdf,text/csv"
        )
        options.set_preference("pdfjs.disabled", True)
        self.driver = webdriver.Firefox(options=options)

    def start(self):
        self.setup(self.dataset_path)
        self.driver.get(f"{self.YT_CHARTS_URL}")

    def collect_countries(self):
        location_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "location-point-icon"))
        )
        location_button.click()
        countries_buttons = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    "//paper-item[contains(@class, 'style-scope ytmc-dropdown-v2') and not(contains(@style, 'none'))]",
                )
            )
        )

        elements = [country.text for country in countries_buttons]
        self.countries = [c for c in elements if not re.search(r"\d", c)]
        self.countries = self.countries[:-5]
        self.logger.info(f"The countries in context are: {self.countries}.")
        self.logger.info(f"It will be collected {len(self.countries)} countries data.")
        self.current_country = self.countries[0]
        self.set_current_week()

    def create_countries_folders(self):
        for folder_name in self.countries:
            folder_path = os.path.join(self.dataset_path, folder_name)

            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Folder created: {folder_path}")
            else:
                print(f"Folder already exists: {folder_path}")

    def set_current_week(self):
        current_week = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "chart-range-string"))
        )
        self.current_week = current_week.text

    def click_nth_paper_button(self, n):
        try:
            paper_buttons = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//paper-button"))
            )
            if n < 1 or n > len(paper_buttons):
                raise IndexError(
                    f"The index {n} is out of bounds. There is only {len(paper_buttons)} 'paper-button'(s) in page."
                )
            paper_buttons[n - 1].click()
        except Exception as e:
            print(f"Error on click nth 'paper-button': {e}")

    def __click_weeks_button(self):
        self.click_nth_paper_button(3)
        weeks_buttons = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//paper-item[contains(@role, 'option')]")
            )
        )
        return weeks_buttons

    def get_all_weeks(self):
        weeks_button = self.__click_weeks_button()
        elements = [button.text for button in weeks_button]

        week_regex = r"^[A-Za-z]{3} \d{1,2} - [A-Za-z]{3} \d{1,2}, \d{4}$|^[A-Za-z]{3} \d{1,2}, \d{4} - [A-Za-z]{3} \d{1,2}, \d{4}$"
        self.weeks = [item for item in elements if re.match(week_regex, item)]
        self.logger.info(f"Current country has {len(self.weeks)} weeks.")

    def download_chart(self):
        download_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "download-button"))
        )
        download_button.click()
        sleep(5)

    def change_week(self):
        self.__click_weeks_button()

        next_week_index = self.weeks.index(self.current_week) + 1

        next_week = self.weeks[next_week_index]
        self.current_week = next_week

        next_week_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//paper-item[contains(text(), '{next_week}')]")
            )
        )

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//paper-item[contains(text(), '{next_week}')]")
            )
        )

        actions = ActionChains(self.driver)
        actions.move_to_element(next_week_button).click().perform()

    def change_country(self):
        current_country_index = self.countries.index(self.current_country)
        next_country = self.countries[current_country_index + 1]

        countries_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "location-point-icon"))
        )
        countries_button.click()

        next_country_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//paper-item[@aria-label='{next_country}']")
            )
        )

        if current_country_index + 1 <= 4:
            self.driver.execute_script(
                "arguments[0].scrollIntoView(true);", next_country_button
            )

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//paper-item[@aria-label='{next_country}']")
            )
        )

        actions = ActionChains(self.driver)
        actions.move_to_element(next_country_button).click().perform()
        self.current_country = next_country

    def reset_to_first_country(self):
        countries_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "location-point-icon"))
        )
        countries_button.click()

        first_country_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//paper-item[@aria-label='{self.countries[0]}']")
            )
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView(true);", first_country_button
        )

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//paper-item[@aria-label='{self.countries[0]}']")
            )
        )

        actions = ActionChains(self.driver)
        actions.move_to_element(first_country_button).click().perform()
        self.current_country = self.countries[0]
        sleep(5)

    def run_shorts_music_collect(self, initial_date: str, exclude_countries: list):
        self.start()
        self.collect_countries()
        self.create_countries_folders()
        selected_countries = [
            country for country in self.countries if country not in exclude_countries
        ]

        for country in selected_countries:
            if country == "South Korea":
                country_code = "kr"
            else:
                country_code = (
                    pycountry.countries.get(name=country).alpha_2.lower()
                    if country != "Global"
                    else "global"
                )

            self.logger.info(f"Current collecting {country} data.")
            current_date = datetime.strptime(initial_date, "%Y%m%d")
            end_date = datetime.strptime(self.max_previous_day_str, "%Y%m%d")
            self.driver.get(
                f"https://charts.youtube.com/charts/TopShortsSongs/{country_code}/daily/{initial_date}"
            )
            sleep(5)
            while current_date >= end_date:
                self.logger.info(
                    f"Collecting charts for day {current_date.strftime("%Y%m%d")}"
                )
                self.download_chart()
                current_date -= timedelta(days=1)
                current_date_str = current_date.strftime("%Y%m%d")
                self.driver.get(
                    f"https://charts.youtube.com/charts/TopShortsSongs/{country_code}/daily/{current_date_str}"
                )
                sleep(5)
