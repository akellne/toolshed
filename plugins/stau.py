#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import datetime
import lxml.html
import json

from base import Plugin

#URL to the traffic jam data
URL = "http://www.verkehrsinformation.de/?tmp=search&road=%&region=9"

#routes to consider
ROUTES = ["A2", "A7"]


class Stau(Plugin):
    """
    class to parse the traffic jam notifications
    """
    NAME     = "Stau"
    AUTHOR   = "kellner@cs.uni-goettingen.de"
    VERSION  = (0, 0, 1)
    ENABLED  = False
    HELP     = "!stau  display the current traffic jams "\
               "(routes: %s)" % ", ".join(ROUTES)
    CHANNELS = []

    def __init__(
        self, ircbot, cache_time=datetime.timedelta(minutes=5),
        random_message=[None, None]
    ):
        Plugin.__init__(self, ircbot, cache_time, random_message)


    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)

        if not self.is_in_channel(params[0]):
            #plugin not available in the channel => return
            return

        if msg == "!stau":
            #get data from cache

            self.ircbot.switch_personality(nick="goodcop")

            reload_data, message = self.load_cache()
            if reload_data:
                #reload the data, if too old
                message = self._get_traffic_jam()
                self.save_cache(data=message)
            else:
                message = message.encode("utf-8")

            #finally, send the message with the
            self.ircbot.privmsg(params[0], message)

            self.ircbot.reset_personality()


    def _get_traffic_jam(self):
        """
        load weather from the mobile version of the wetter.com webpage
        """
        #load url and parse it with html parser
        root = lxml.html.parse(URL)

        routes = {}
        for td in root.xpath(
            "//tr/td[@colspan='2']/font"
        ):
            text = td.text_content().strip()

            #try to find the route in the text
            res = re.compile("^(\w\d+.*?)\s").search(text)
            if res:
                if res.group(1) in ROUTES:
                    #got route from regex
                    route = res.group(1)

                    #if considered route => add it to the list
                    if route not in routes:
                        routes[route] = []
                    routes[route].append(text)

        tmp = "--- Verkehrsnachrichten ---\n"
        for route, items in routes.items():
            tmp += "Achtung auf der %s!\n" % route
            for item in items:
                tmp += "* %s\n" % item
        tmp += "Trotzdem eine gute Fahrt!"

        return tmp.encode("utf-8")


