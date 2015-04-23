#!/usr/bin/env python3
from __future__ import print_function, division, with_statement
import time
import re
from datetime import datetime
from math import ceil
from urllib.error import URLError
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

html_entities = re.compile("%[0-9a-fA-F][0-9a-fA-F]")


def unescape_html(thing):
    new_string = thing
    for i in set(html_entities.findall(new_string)):
        value = int(i.replace("%", "", 1), 16)
        ascii_char = chr(value)
        new_string = new_string.replace(("%" if not i.startswith("%") else "") + i, ascii_char)
    return new_string


class CookieException(Exception):
    pass


class CookieBot(object):
    chip_amount = None

    def __init__(self, driver_type, config):
        """
        Initializes a CookieBot instance
        Arguments:
            driver_type: What driver to use, e.g Chrome/ or PhantomJS
            save_to: Where to load/save the savefile.

        """
        if config["binary_path"]:
            self.browser = driver_type(config["binary_path"])
        else:
            self.browser = driver_type()

        self.location = config["savefile_path"]
        self.running = True
        self.save_string = None
        self.config = config
        self.golden_dt = None
        self.bought = 0
        self.start()

    def start(self):
        """
        Loads up everything needed for the CookieBot
        There's no need to call this, since it's called in __init__
        """
        self.browser.maximize_window()
        self.browser.get(self.config["url"])
        # For some reason even if I waited for bigCookie it would still crash.
        WebDriverWait(self.browser, 60).until(
            expected_conditions.title_contains(
                "cookies"
            )
        )
        if CookieBot.chip_amount is None:
            CookieBot.chip_amount = self.browser.execute_script("return Game.HowManyCookiesReset(1)")
        self.load_save_file()
        self.minimal()

    def run(self):
        """
        Runs the CookieBot.
        The self.running variable can also be edited by another thread to stop.
        """
        iterations = 0
        while self.running:
            self.click_golden()
            self.close_notifications()
            money = self.get_cookies()
            mps = self.get_cookies_per_second()
            self.echo("[+] Have {} cookies and {} cookies per second, heavenly chips so far: {}".format(
                money,
                mps,
                self.get_chips()
                )
            )
            best_building = self.get_best_building()
            best_upgrade = self.get_best_upgrade()
            things = filter(lambda x: x is not None, [best_building, best_upgrade])
            optimal = min(things, key=lambda x: x["ratio"])
            if optimal is not None:
                self.echo("[+] Buying {} with price {}".format(optimal["name"], optimal["price"]))
                if optimal["price"] > money:
                    difference = optimal["price"] - money
                    self.echo("[-] Missing {} money!".format(difference))
                    if self.config["click_missing"]:
                        for _ in range(int(ceil(difference))):
                            self.click_golden()
                            self.click_cookie()
                            if self.get_cookies() >= optimal["price"]:
                                break
                self.browser.execute_script(optimal["buy"])
            else:
                self.click_cookie(5)
            self.reset()  # Don't worry, it's auto-handled.
            iterations += 1
            if iterations >= self.config["save_every"]:
                self.echo("[+] Saved!")
                self.save_string = self.get_save_string()
                iterations = 0
            time.sleep(self.config["sleep_amount"])


    def click_cookie(self, amount=1):
        """
        Clicks the Big Cookie, giving you one cookie for each press.
        Arguments:
            amount: How many times to press
        """
        for i in range(amount):
            self.browser.execute_script("Game.ClickCookie()")

    def click_golden(self, chain=False):
        """
        Clicks a Golden Cookie if it's there.
        """
        if self.golden_dt is not None and time.time() - self.golden_dt < .1:
            self.echo("[-] Pressing Too Quick!")
            return
        cache = self.get_golden()
        money = self.get_cookies()
        self.browser.execute_script("Game.goldenCookie.click()")

        if self.get_golden() > cache:
            effect = self.browser.execute_script("return Game.goldenCookie.last").lower()
            new = self.get_cookies()
            diff = max(new, money) - min(new, money)
            self.echo("[+] Pressed a Golden Cookie with effect {} and difference in money {}!".format(effect, diff))
            self.golden_dt = time.time()
            if "chain" in effect:
                time.sleep(.1)
                if not chain:
                    self.echo("[+] Starting chain!")
                self.click_golden(True)


    def quit(self):
        """
        Writes the save file and quits the browser.
        """
        # I know this method is mostly useless.
        # But I'll add more to it once I do have more to add to it.
        self.write_save_file()
        try:
            self.browser.quit()
        except URLError:
            # This sometimes happens.
            # I don't know why yet.
            pass

    def close_notifications(self):
        """
        Closes all the notifications/etc on screen.
        """
        self.browser.execute_script("Game.CloseNotes()")

    def get_cookies(self, full=False):
        """
        Gets how much "money" you have.
        """
        raw_cookies = self.browser.execute_script("return Game.cookies")
        if full:
            return raw_cookies
        else:
            return round(raw_cookies, 2)

    def get_cookies_per_second(self, full=False):
        """
        Gets how much cookies per second you have.
        """
        raw_cookiesps = self.browser.execute_script("return Game.cookiesPs")
        if full:
            return raw_cookiesps
        else:
            return round(raw_cookiesps, 2)

    def get_golden(self, local=True):
        """
        Gets how many golden cookies you've clicked
        Can either be "in this session" or "all time"
        Arguments:
            local: If to get this session's or all time's
        """
        golden_script = "return Game.goldenClicksLocal" if local else "return Game.goldenClicks"
        return self.browser.execute_script(golden_script)

    def get_buildings(self):
        """
        Gets all the buildings, and returns back an useful dict.
        Can be easily expanded.
        """
        buildings = []
        for i in range(11):
            script_ = "return Game.ObjectsById[{}]".format(i)
            info = self.browser.execute_script(script_)
            name = info["name"]
            price = info["price"]
            mps = self.browser.execute_script(script_ + ".cps()")
            buy = script_ + ".buy(1)"
            # Is there a better way to calculate "value"? (the ratio)
            i_dict = {
                "name": name,
                "price": price,
                "mps": mps,
                "ratio": (price - self.get_cookies()) / (self.get_cookies_per_second() or 1),
                "buy": buy
            }
            buildings.append(i_dict)
        return buildings

    def get_upgrades(self):
        """
        Gets the upgrades, in the same manner as the buildings.
        """
        upgrades = []
        available = self.browser.execute_script("return Game.UpgradesInStore")
        # Only get 10 upgrades at a time.
        for i in range(len(available)):
            script_ = "return Game.UpgradesInStore[{}]".format(i)
            info = self.browser.execute_script(script_)
            name = info["name"]
            if name.lower() in self.config["excluded_upgrades"]:
                continue
            price = self.browser.execute_script(script_ + ".getPrice()")
            buy = script_ + ".buy(1)"
            i_dict = {
                "name": name,
                "price": price,
                "ratio": (price - self.get_cookies()) / (self.get_cookies_per_second() or 1),
                "buy": buy
            }

            upgrades.append(i_dict)
        return upgrades

    def get_best_building(self):
        options = self.get_buildings()
        if options:
            return min(options, key=lambda x: x["ratio"])

    def get_best_upgrade(self):
        options = self.get_upgrades()
        if options:
            return min(options, key=lambda x: x["ratio"])

    # noinspection PyTypeChecker
    def get_chips(self):
        if CookieBot.chip_amount is not None:
            chips = self.get_cookies() / CookieBot.chip_amount
            return chips
        return 0

    def reset_viable(self):
        if CookieBot.chip_amount is not None:
            return self.get_chips() >= self.config["reset_every"]
        return False

    def reset(self, override=False):
        if override or self.reset_viable():
            self.echo("[+] Resetting!")
            self.browser.execute_script("Game.Reset()")
            self.browser.find_element_by_id("promptOption0").click()

    # Helper methods for saving and loading.
    def get_save_string(self):
        """
        Gets the save-string needed to restore the save.
        """
        self.browser.execute_script("Game.ExportSave()")
        save_zone = self.browser.find_element_by_id("textareaPrompt")
        save_string = save_zone.text
        self.browser.execute_script("Game.ClosePrompt()")
        return save_string

    def load_save_file(self):
        """
        Loads the savefile easily.
        """
        self.browser.execute_script("Game.ImportSave()")
        try:
            with open(self.location) as save_file:
                self.browser.find_element_by_id("textareaPrompt").send_keys(save_file.read())
        except FileNotFoundError:
            self.echo("[-] No savefile!")
        self.browser.find_element_by_id("promptOption0").click()

    def write_save_file(self):
        """
        Saves the save-string to the given location.
        """
        if self.save_string is not None:
            with open(self.location, "w") as save_file:
                save_file.write(self.save_string)

    def minimal(self):
        self.browser.execute_script("for (var k in Game.prefs) Game.prefs[k] = 0; Game.prefs[\"format\"] = 1")
        self.browser.execute_script(
            "Game.ToggleFancy();BeautifyAll();Game.RefreshStore();Game.upgradesToRebuild=1;")

    def echo(self, *args, **kwargs):
        if self.config["verbose"]:
            extra = []
            if self.config["timestamp"]:
                today = datetime.today()
                if "time" in self.config["timestamp"]:
                    extra.append("[{}]".format(today.strftime("%H:%M:%S")))
                if "date" in self.config["timestamp"]:
                    extra.append("[{}]".format(today.strftime("%Y-%m-%d")))
            print(*tuple(extra) + args, **kwargs)


def main(driver_type, conf):
    bot = CookieBot(driver_type, conf)
    try:
        bot.run()
    except KeyboardInterrupt:
        bot.echo("[-] Quitting...")
    finally:
        bot.quit()

