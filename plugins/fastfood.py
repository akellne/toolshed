#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import datetime
import lxml.html
import json

from base import Plugin

#URL to burgerking
URL = "http://www.burgerking.de"


class FastFood(Plugin):
    """
    class to parse some fastfood webpages
    """
    NAME    = "Fastfood"
    AUTHOR  = "kellner@cs.uni-goettingen.de"
    VERSION = (0, 0, 1)
    ENABLED = True
    HELP    = "!fastfood  display the king of the month"

    def __init__(
        self, ircbot, cache_time=datetime.timedelta(days=1),
        random_message=[None, None]
    ):
        Plugin.__init__(self, ircbot, cache_time, random_message)


    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)

        if msg == "!fastfood":
            #get data from cache
            self.ircbot.switch_personality(nick="bkismyway")

            reload_data, message = self.load_cache()
            if reload_data:
                #reload the data, if too old
                message = self._get_king_of_the_month()
                self.save_cache(data=message)
            else:
                message = message.encode("utf-8")

            #finally, send the message with the
            self.ircbot.privmsg(params[0], message)

            self.ircbot.reset_personality()


    def _get_king_of_the_month(self):
        """
        load king of the month from burgerking webpage
        """
        try:
            #load url and parse it with html parser
            root = lxml.html.parse(URL)

            #get relevant part
            el = root.xpath(
                "//h2[text()='King des Monats']/following-sibling::div[@class='info']/p"
            )

            res = re.compile("Der (.*?) -" ).search(el[0].text)
            if res:
                text = "--- King of the Month: '%s' ---\n%s" % (
                    res.group(1),  el[0].text
                )
            else:
                text = "--- King of the Month ---\n%s" % el[0].text

        except:
            text = "Sorry, burgerking parser is broken. Cannot get " \
                   "the King of the Month"

        return text.encode("utf-8")


