#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import lxml.html
import json

from base import Plugin

#URL to the bundesliga data
URL = "http://fussballdaten.sport.de/"

class Bundesliga(Plugin):
    """ class to parse bundesliga data """
    NAME    = "Bundesliga"
    AUTHOR  = "konrad.rieck@uni-goettingen.de"
    VERSION = (0, 0, 1)
    ENABLED = True
    HELP    = "!bundesliga  current results of the Bundesliga"

    def __init__(self, ircbot, cache_time=datetime.timedelta(hours=1)):
        Plugin.__init__(self, ircbot, cache_time)

    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)

        if msg.startswith("!bundesliga"):
            self.ircbot.switch_personality(nick="loddar")
            message = self.get_bundesliga()
            self.ircbot.privmsg(params[0], message)
            self.ircbot.reset_personality()

    def get_bundesliga(self):
        """ load results from sport.de """

        try:
            root = lxml.html.parse(URL)
            el = root.xpath('//table[@class="Spiele"]')[0]

            tmp = "--- %s ---\n" % el.get('summary').strip()
            for tr in el.getchildren()[1:]:
                td = tr.getchildren()
                tmp += "  %s  %s : %s  %s\n" % (
                    td[0].xpath("string()")[3:-11],
                    td[1].xpath("string()"),
                    td[3].xpath("string()"),
                    td[4].xpath("string()")[:-7]
                )
        except:
            tmp = "Keine Ahnung. Mein Parser ist kaputt!"
        finally:
            return tmp.strip().encode("utf-8")
