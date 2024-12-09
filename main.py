import os

from selenium import webdriver

from shorts_songs_crawler import ShortsSongsCrawler

options = webdriver.FirefoxOptions()
options.set_preference("browser.download.folderList", 2)
options.set_preference(
    "browser.download.dir", "/home/filipe/Pesquisas/short-videos/dataset"
)
options.set_preference(
    "browser.helperApps.neverAsk.saveToDisk", "application/pdf,text/csv"
)
options.set_preference("pdfjs.disabled", True)

driver = webdriver.Firefox(options=options)

crawler = ShortsSongsCrawler("20231106")  # Max previous collect day
crawler.run_shorts_music_collect("20241106", [])  # Today
