import src
from selenium.webdriver import *
driver = Chrome
config_name = "config.txt"
with open(config_name) as config_file:
    config = src.parse_file(config_file)
src.main(driver, config)