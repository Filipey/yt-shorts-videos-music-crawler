import os

from selenium import webdriver

from shorts_songs_crawler import ShortsSongsCrawler

options = webdriver.FirefoxOptions()
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.dir", os.getenv("DOWNLOAD_PATH", "../dataset"))
options.set_preference(
    "browser.helperApps.neverAsk.saveToDisk", "application/pdf,text/csv"
)
options.set_preference("pdfjs.disabled", True)

driver = webdriver.Firefox(options=options)

crawler = ShortsSongsCrawler(driver, True)
crawler.run_shorts_music_collect()
