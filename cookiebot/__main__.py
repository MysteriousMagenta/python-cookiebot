#!/usr/bin/env python3
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
# If somebody forgets to rename it.
fallback_config = "config-sample.txt"
def main():
    try:
        config_file = open(config_name)
    except FileNotFoundError:
        config_file = open(fallback_config)

    config = (cookiebot or cookiebot_config).parse_file(config_file)["CookieBot"]
    config_file.close()

    (cookiebot or cookiebot_bot).main(driver, config)

if __name__ == '__main__':
    main()
