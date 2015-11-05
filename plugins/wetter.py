#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import lxml.html
import json

from base import Plugin

#URL to the weather data
URL = "http://mobile.wetter.com/wetter_aktuell/wettervorhersage/3_tagesvorhersage/?id=DE0003197"


class Wetter(Plugin):
    """
    class to parse the weather of wetter.com mobile webpage
    """
    NAME     = "Wetter"
    AUTHOR   = "kellner@cs.uni-goettingen.de"
    VERSION  = (0, 0, 2)
    ENABLED  = True
    HELP     = "!wetter  current weather forecast\n" \
               "!wetter+1  weather forecast for tomorrow\n" \
               "!wetter+2  weather forecast for the day after tomorrow"
    CHANNELS = []

    def __init__(
        self, ircbot, cache_time=datetime.timedelta(hours=1),
        random_message=[None, None]
    ):
        Plugin.__init__(self, ircbot, cache_time, random_message)


    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)

        if not self.is_in_channel(params[0]):
            #plugin not available in the channel => return
            return

        if msg.startswith("!wetter"):
            #get data from cache

            self.ircbot.switch_personality(nick="kachelmann")

            reload_data, self.days = self.load_cache()
            if reload_data:
                #reload the data, if too old
                self.days = self._get_weather()
                self.save_cache(data=self.days)

            if msg == "!wetter" or msg == "!wetter_heute":
                message = "--- Wetter heute in Göttingen: ---\n"
                message += self._get_today()

            elif msg == "!wetter+1" or msg == "!wetter_morgen":
                message = "--- Wetter morgen in Göttingen: ---\n"
                message += self._get_tomorrow()

            elif msg == "!wetter+2" or msg == "!wetter_uebermorgen":
                message = "--- Wetter übermorgen in Göttingen: ---\n"
                message += self._get_tomorrow()

            #finally, send the message with the
            self.ircbot.privmsg(params[0], message)

            self.ircbot.reset_personality()


    def _get_weather(self):
        """
        load weather from the mobile version of the wetter.com webpage
        """
        #load url and parse it with html parser
        root = lxml.html.parse(URL)

        #get weather panels
        days = {}
        for panel in root.xpath("//div[contains(@class, 'panelContainer weather')]"):
            # get day
            day = panel.xpath(
                "div/div/div[contains(@style, 'color: #365383;')]"
            )[0].text_content().strip()[-10:]
            #get date
            dt = datetime.datetime.strptime(
                day, "%d.%m.%Y"
            ).strftime("%Y%m%d")

            tods = {}
            for col in panel.findall("div/div[@class='small-3 columns']"):
                rows = col.findall("div[@class='row']")

                # get time of day (morgens, mittags etc.)
                tod = rows[0].text_content().lower().strip()

                # prepare day item
                tods[tod] = {}
                tods[tod]["degree"] = rows[2].text_content().strip()
                tods[tod]["status"] = rows[3].text_content().strip()
                tods[tod]["rainprob"] = rows[5].text_content().strip()
                tmp = rows[6].text_content().strip().split("\n")
                tods[tod]["wind"] = "%s %s" % (tmp[0].strip(), tmp[1].strip())
                
            days[dt] = tods

        return days


    def _get_today(self, today=None):
        if not today:
            today = datetime.datetime.today()
        today = today.strftime("%Y%m%d")

        if today not in self.days:
            return "There is no weather forecast for today :-("

        if self.days[today] == {}:
            #no information
            return None

        tmp = ""
        for item in ("morgens", "mittags", "abends", "nachts"):
            if item not in self.days[today]:
                continue

            tmp += "%s:\n  %s, %s (%s), %s\n" % (
                item,
                self.days[today][item]["degree"],
                self.days[today][item]["status"],
                self.days[today][item]["rainprob"],
                self.days[today][item]["wind"]
            )

        return tmp.strip().encode("utf-8")


    def _get_tomorrow(self):
        dt = datetime.datetime.today() + datetime.timedelta(days=1)
        return self._get_today(dt)


    def _get_day_after_tomorrow(self):
        dt = datetime.datetime.today() + datetime.timedelta(days=1)
        return self._get_today(dt)


