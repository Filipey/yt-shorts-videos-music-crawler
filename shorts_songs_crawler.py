import logging
from time import sleep

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.wpewebkit.webdriver import WebDriver

from logger import Logger


class ShortsSongsCrawler:
    countries: list = []
    current_country: None | str = None
    current_country_weeks: list = []
    current_country_week: str
    driver: WebDriver
    logger: logging.Logger
    dataset_path: str = "../dataset"
    YT_CHARTS_URL = "https://charts.youtube.com/charts/TopShortsSongs/global/weekly"
    is_collecting_shorts_songs: bool

    def __init__(self, driver: WebDriver, is_collecting_shorts_songs) -> None:
        self.countries = []
        self.current_country = None
        self.current_country_weeks = []
        self.driver = driver
        self.logger = Logger.get_logger(__name__)
        self.is_collecting_shorts_songs = is_collecting_shorts_songs

    def start(self):
        self.driver.get(self.YT_CHARTS_URL)

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

        self.countries = [country.text for country in countries_buttons]
        self.countries = self.countries[:-6]
        self.logger.info(f"It will be collected {len(self.countries)} countries data.")
        self.current_country = self.countries[0]

    def set_current_week(self):
        current_week = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "chart-range-string"))
        )
        self.current_country_week = current_week.text

    def __click_weeks_button(self):
        change_week_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//span[contains(text(), '{self.current_country_week}')]")
            )
        )
        change_week_button.click()
        weeks_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//paper-item[contains(@role, 'option')]")
            )
        )

        change_week_button.click()
        return weeks_button

    def get_all_weeks(self):
        weeks_button = self.__click_weeks_button()
        self.current_country_weeks = [button.text for button in weeks_button]
        self.logger.info(
            f"Current country has {len(self.current_country_weeks)} weeks."
        )

    def download_chart(self):
        download_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "download-button"))
        )
        download_button.click()

    def change_week(self):
        self.__click_weeks_button()

        next_week_index = (
            self.current_country_weeks.index(self.current_country_week) + 1
        )

        next_week = self.current_country_weeks[next_week_index]

        next_week_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//paper-item[text(), {next_week}]")
            )
        )
        next_week_button.click()

    def change_country(self):
        current_country_index = self.countries.index(self.current_country)
        next_country = self.countries[current_country_index + 1]

        countries_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "location-point-icon"))
        )
        countries_button.click()

        next_country_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//paper-item[contains(text(), '{next_country}')]")
            )
        )
        next_country_button.click()
        self.current_country = next_country

    def run_shorts_music_collect(self):
        self.start()
        self.collect_countries()
        self.set_current_week()
        self.get_all_weeks()

        for week_index, week in enumerate(self.current_country_weeks):
            if week_index == len(self.current_country_weeks):
                self.logger.info(
                    f"Collect of {country} finished. Changing to the next country"
                )
                break
            self.logger.info(f"Collecting Week {week}")
            for country_index, country in enumerate(self.countries):
                if country_index == len(self.countries):
                    self.logger.info(f"Collect completed. Check the 'dataset' folder!")
                    break

                self.logger.info(f"------ Currently collecting '{country}.' ------")
                self.download_chart()
                self.change_country()
