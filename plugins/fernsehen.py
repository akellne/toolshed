#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import lxml.html
import json

from base import Plugin

#URL to the tvmovie data
URL = "http://mobil.tvmovie.de/page%d.rbml"

class Fernsehen(Plugin):
    """ class to parse fernsehen data """
    NAME    = "Fernsehen"
    AUTHOR  = "konrad.rieck@uni-goettingen.de"
    VERSION = (0, 0, 1)
    ENABLED = True
    HELP    = "!fernsehen  current tv shows\n" \
              "!fernsehen+gleich  following tv shows\n"
              "!fernsehen+20:15  tv shows at 20:15\n" \
              "!fernsehen+22:00  tv shows at 22:00\n" \
              "!fernsehen+tipp  today's best tv shows\n" \
              "!fernsehen+filme  today's best movies" \


    def __init__(self, ircbot, cache_time=datetime.timedelta(hours=1)):
        Plugin.__init__(self, ircbot, cache_time)

    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)

        if msg.startswith("!fernsehen"):
            self.ircbot.switch_personality(nick="glotze")

            if msg == "!fernsehen+gleich":
                message = self.get_fernsehen(6)
            elif msg == "!fernsehen+20:15":
                message = self.get_fernsehen(1)
            elif msg == "!fernsehen+22:00":
                message = self.get_fernsehen(2)
            elif msg == "!fernsehen+tipp":
                message = self.get_fernsehen(5)
            elif msg == "!fernsehen+filme":
                message = self.get_fernsehen(4)
            else:
                message = self.get_fernsehen(3)

            self.ircbot.privmsg(params[0], message)
            self.ircbot.reset_personality()

    def get_fernsehen(self, page):
        """ load results from tvmovie.de """

        try:
            tmp = ""
            root = lxml.html.parse(URL % page)
            el = root.xpath('//a[@class="piped-active"]')[0]
            tmp += "--- Fernsehen: %s ---\n" % el.xpath('string()').strip()

            for headline in root.xpath('//div[@class="headline"]'):
                prg = headline.xpath('string()').strip()
                if len(prg) > 45: prg = prg[:45] + "..."
                tmp += "  %s\n" % prg
        except:
            tmp = "Keine Ahnung. Mein Parser ist kaputt"
        finally:
            return tmp.strip().encode('utf-8')
