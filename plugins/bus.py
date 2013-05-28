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
    """ class to parse bus data from fahrplaner.de """
    NAME    = "Bus"
    AUTHOR  = "konrad.rieck@uni-goettingen.de"
    VERSION = (0, 0, 1)
    ENABLED = True
    HELP    = "!bus  current timetable for the bus stop at " \
              "Goldschmidtstraße"

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
        """ load departures from the fahrplaner.de """

        try:
            root = lxml.html.parse(URL)
            el = root.find(
                "body/div/table"
            )

            tmp = ""
            for tr in el:
                td = tr.getchildren()
                tmp += " %-12s %-20s  %s\n " % (
                    td[0].text.strip(),
                    td[1].text.strip()[:20],
                    td[2].text.strip()[:7]
                )
        except:
            tmp = "Keine Ahnung. Mein Parser ist kaputt!"
        finally:
            return tmp.strip().encode("utf-8")

