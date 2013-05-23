#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import lxml.html
import json

from base import Plugin

#URL to the bus data
URL = "http://www.fahrplaner.de/hafas/stboard.exe/dn?input=1190951&maxJourneys=5&showResultPopup=popup&start=1"

class Bus(Plugin):
    """
    class to parse the bus data of fahrplaner.de webpage
    """
    NAME    = "Bus"
    AUTHOR  = "konrad.rieck@uni-goettingen.de"
    VERSION = (0, 0, 1)
    ENABLED = True

    def __init__(self, ircbot, cache_time=datetime.timedelta(hours=1)):
        Plugin.__init__(self, ircbot, cache_time)

    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)
        
        if msg.startswith("!bus"):
            self.ircbot.switch_personality(nick="busfahrer")

            message = "--- Gleich an der Goldschmidtstrasse ---\n"
            message += self.get_bus()
            
            self.ircbot.privmsg(params[0], message)
            self.ircbot.reset_personality()

    def get_bus(self):
        """
        load bus data from the fahrplaner.de webpage
        """
        #load url and parse it with html parser
        root = lxml.html.parse(URL)

        #get relevant part
        el = root.find(
            "body/div/table"
        )

        tmp = ""
        for tr in el:
            td = tr.getchildren()
            tmp += " %-12s %-15s %s\n " % (
                td[0].text.strip(),
                td[1].text.strip(),
                td[2].text.strip()[:7]
            )
        return tmp.strip().encode("utf-8")

