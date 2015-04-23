from __future__ import print_function, division, with_statement
try:
    import cookiebot
except ImportError:
    cookiebot = None
    import cookie_selenium as cookiebot_bot
    import config_parsing as cookiebot_config
from selenium.webdriver import *
driver = Chrome
config_name = "config.txt"
with open(config_name) as config_file:
    config = (cookiebot or cookiebot_config).parse_file(config_file)["CookieBot"]
(cookiebot or cookiebot_bot).main(driver, config)
