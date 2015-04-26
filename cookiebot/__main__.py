#!/usr/bin/env python3
import cookiebot
from selenium.webdriver import *
driver = Chrome
# What config names to try.
configs = ("config.txt", "config.ini", "config-sample.txt", "config-sample.ini")
def main(save_on_exit=True):
    for n, name in enumerate(configs, start=1):
        try:
            config_file = open(name)
        except IOError as e:
            if n == len(configs):
                raise e.__class__("No Config Was Found!")
        else:
            with config_file:
                config = cookiebot.parse_file(config_file)["CookieBot"]
            cookiebot.CookieBot.start_bot(driver, config, save_on_exit)
            return

if __name__ == '__main__':
    main()
