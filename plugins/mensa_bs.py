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
URL = "http://www.stw-on.de/braunschweig/essen/menus/mensa-1"


class Mensa(Plugin):
    """
    class to parse the mensa plan
    """
    NAME     = "Mensa Plan (BS)"
    AUTHOR   = "kellner@cs.uni-goettingen.de"
    VERSION  = (0, 0, 1)
    ENABLED  = True
    HELP     = "!mensa   today's dishes in the brunswick mensa-1\n" \
               "!mensa+1 tomorrow's dishes in the brunswick mensa-1"
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

        days = {}
        for day in root.xpath("//table[@class='swbs_speiseplan']"):
            # get weekday and mensa type (Mittags- vs. Abendmensa)
            weekday, mtype = day.find(
                "tr/th[@class='swbs_speiseplan_head']"
            ).text_content().split(u"\u2013")
            
            if mtype.strip() == "Abendmensa":
                # skip Abendmensa
                continue

            #get date
            dt = datetime.datetime.strptime(
                weekday.strip().encode("latin1"), 
                "%A, %d. %B %Y"
            ).strftime("%Y%m%d")
            if dt not in days:
                days[dt] = []

            for row in day.findall("tr")[1:]:
                d = {}
                
                kind_meal = row.find(
                    "td[@class='swbs_speiseplan_kind_meal']"
                ).text_content().strip()

                if kind_meal == "":
                    # skip rows with symbols
                    continue
                d["kind_meal"] = kind_meal

                detail = row.find(
                    "td[@class='swbs_speiseplan_other']"
                ).text_content().strip()
                if detail != "":
                    d["meal_detail"] = detail
                
                d["price_s"] = row.find(
                    "td[@class='swbs_speiseplan_price_s']"
                ).text_content().strip()

                d["price_e"] = row.find(
                    "td[@class='swbs_speiseplan_price_e']"
                ).text_content().strip()
                
                days[dt].append(d)
        return days


    def _get_today(self, today=None):
        if not today:
            today = datetime.datetime.today()
        today = today.strftime("%Y%m%d")

        if today not in self.days:
            #no mensa plan vailable
            return None

        if self.days[today] == []:
            #no information
            return None

        tmp = "--- Der Chef de Cuisine empfiehlt ---\n"
        # save category to prevent duplicate printing
        lastkind = None
        for item in self.days[today]:
            if lastkind!=item["kind_meal"]:
                # \x02 = bold, \x0F = standard
                tmp += "\x02%s\x0F\n" % item["kind_meal"]
            if item["meal_detail"]:
                tmp += "    %s" % item["meal_detail"]
            if item["price_s"]:
                tmp += " (S: %s, M: %s)" % (
                    item["price_s"], item["price_e"]
                )
            tmp += "\n"
            lastkind = item["kind_meal"]

        #hack to add space
        tmp = tmp.replace("undPastabuffet", "und Pastabuffet")

        return tmp.strip().encode("utf-8")


    def _get_tomorrow(self):
        dt = datetime.datetime.today() + datetime.timedelta(days=1)
        return self._get_today(dt)
