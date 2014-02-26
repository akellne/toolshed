#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import locale
import datetime
import lxml.html
import json

from base import Plugin

#URL to the mensa plan
URL = "http://www.studentenwerk-goettingen.de/speiseplan.html?&no_cache=1&day=7&push=0&selectmensa=Nordmensa"


class Mensa(Plugin):
    """
    class to parse the mensa plan
    """
    NAME     = "Mensa Plan"
    AUTHOR   = "kellner@cs.uni-goettingen.de"
    VERSION  = (0, 0, 2)
    ENABLED  = True
    HELP     = "!mensa   today's dishes in the nord mensa\n" \
               "!mensa+1 tomorrow's dishes in the nord mensa"
    CHANNELS = []

    def __init__(
        self, ircbot, cache_time=datetime.timedelta(days=1),
        random_message=[None, None]
    ):
        Plugin.__init__(self, ircbot, cache_time, random_message)

        #set locale to German (required for parsing the German date)
        try:
            locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
        except Exception, e:
            print "de_DE.UTF-8 needs to be generated so that the " \
                  "date can be parsed correctly! (use 'dpkg-" \
                  "reconfigure locales' to generate the " \
                  "corresponding locales)"
            sys.exit(1)


    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)

        if not self.is_in_channel(params[0]):
            #plugin not available in the channel => return
            return

        if msg in ("!mensa", "!mensa+1"):
            self.ircbot.switch_personality("souschef")

            #get data from cache
            reload_data, self.days = self.load_cache()
            if reload_data:
                #reload the data, if too old
                self.days = self._get_dishes()
                self.save_cache(data=self.days)
            
            if msg == "!mensa":
                message = self._get_today()
                if message:
                    message = message.replace("DAY", "heute")
                else:        
                    message = "Die Küche hat heute bereits geschlossen."
            elif msg == "!mensa+1":
                message = self._get_tomorrow()
                if message:
                    message = message.replace("DAY", "morgen")
                else:
                    message = "Die Küche hat morgen geschlossen."

            #finally, send the message with the
            self.ircbot.privmsg(params[0], message)

            self.ircbot.reset_personality()


    def _get_dishes(self):
        """
        get dishes from mensa webpage
        """
        #load url and parse it with html parser
        root = lxml.html.parse(URL)

        #get relevant part of the webpage with the dishes
        el = root.find("//div[@id='speise-main']")

        #get the different days
        days = {}
        for x in el.findall("div[@class='speise-tblhead']"):
            #get date
            dt = datetime.datetime.strptime(
                x.text.encode("latin1"), 
                "%A, %d. %B %Y"
            ).strftime("%Y%m%d")

            if dt not in days:
                days[dt] = []
            for dish in  x.getnext().findall("tr"):
                err = dish.find("td[@class='ext_sits_speiseplan_err']")

                #get all dishes of the day
                dish_type = dish.find(
                    "td[@class='ext_sits_speiseplan_links']"
                )
                if dish_type is not None:
                    dish_type = dish_type.text_content()

                dish_desc = dish.find(
                    "td[@class='ext_sits_speiseplan_rechts']"
                )
                if dish_desc is not None:
                    details = dish_desc.find(
                        "span[@class='ext_sits_essen']"
                    )
                    if details is not None:
                        el = details.find("strong")
                        if el is not None:
                            starter   = details.text.strip()
                            main_dish = el.text
                            if main_dish:
                                side_dish = el.tail.strip()
                            else:
                                main_dish = el.tail.strip()
                                side_dish = ""

                            item = {
                                "type"      : dish_type,
                                "starter"   : starter,
                                "main_dish" : main_dish,
                                "side_dish" : side_dish,
                            }
                            days[dt].append(item)

        return days


    def _get_today(self, today=None):
        if not today:
            today = datetime.datetime.today()
        today = today.strftime("%Y%m%d")

        if today not in self.days:
            #no mensa plan vailable
            return None

        print today, self.days[today]

        if self.days[today] == []:
            #no information
            return None

        tmp = "--- Der Chef de Cuisine empfiehlt DAY ---\n"
        for item in self.days[today]:
            tmp += "%s\n" % item["type"]
            if item["starter"]:
                tmp += "    %s\n" % item["starter"]
            tmp += "    %s\n" % item["main_dish"]
            if item["side_dish"]:
                tmp += "    %s\n" % item["side_dish"]

        return tmp.strip().encode("utf-8")


    def _get_tomorrow(self):
        dt = datetime.datetime.today() + datetime.timedelta(days=1)
        return self._get_today(dt)

