import src
from selenium.webdriver import *
driver = Chrome
location = "savefile.txt"
path = ""
if path:
    src.main(driver, location, path)
else:
    src.main(driver, location)