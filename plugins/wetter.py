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
    NAME    = "Wetter"
    AUTHOR  = "kellner@cs.uni-goettingen.de"
    VERSION = (0, 0, 1)
    ENABLED = True
    HELP    = "!wetter  current weather forecast\n" \
              "!wetter+1  weather forecast for tomorrow\n" \
              "!wetter+2  weather forecast for the day after tomorrow"

    def __init__(self, ircbot, cache_time=datetime.timedelta(hours=1)):
        Plugin.__init__(self, ircbot, cache_time)


    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)

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

        #get relevant part
        el = root.find(
            "body/div[@id='container']/div[@id='main']/div[@id='content']"
        )

        days = {}
        for x in el.xpath(
            "div[@class='vorschau_wrapper ' or @class='vorschau_wrapper']"
        ):
            #print lxml.html.tostring(x)

            day = x.find("div[@class='day weekend']").text_content()[-10:]
            #get date
            dt = datetime.datetime.strptime(
                day, "%d.%m.%Y"
            ).strftime("%Y%m%d")

            #for each day get different time of days
            tods = {}
            for tod in ("morgens", "mittags", "abends", "nachts"):
                tods[tod] = {}

                #degree
                el = x.find("div[@class='%s']" % tod).find(
                    "div[@class='degree']"
                )
                tods[tod]["degree"] = el.text_content()

                #status
                el = el.getnext()
                tods[tod]["status"] = el.text_content()

                #skip gefuehlt wie => rain probability
                el = el.getnext().getnext()
                tods[tod]["rainprob"] = el.text_content()

                #wind
                el = el.getnext()
                tods[tod]["wind"] = el.text_content()

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
        for item in self.days[today]:
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

