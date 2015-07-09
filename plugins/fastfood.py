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
URL = "http://www.burgerking.de/neues-aktionen"


class FastFood(Plugin):
    """
    class to parse some fastfood webpages
    """
    NAME     = "Fastfood"
    AUTHOR   = "kellner@cs.uni-goettingen.de"
    VERSION  = (0, 0, 1)
    ENABLED  = True
    HELP     = "!fastfood  display the king of the month"
    CHANNELS = []

    def __init__(
        self, ircbot, cache_time=datetime.timedelta(days=1),
        random_message=[None, None]
    ):
        Plugin.__init__(self, ircbot, cache_time, random_message)


    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)

        if not self.is_in_channel(params[0]):
            #plugin not available in the channel => return
            return

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
            regexpNS = "http://exslt.org/regular-expressions"
            el = root.xpath(
                "//h3[re:test(text(), 'des Monats')]/following-sibling::p",
                namespaces={'re': regexpNS}
            )

            text = "--- King of the Month ---\n%s" % (
                re.sub(r"(\xa0)+", "", el[0].text)
            )
            print repr(el[0].text)


        except Exception, e:
            text = "Sorry, burgerking parser is broken. Cannot get " \
                   "the King of the Month"

        return text.encode("utf-8")


