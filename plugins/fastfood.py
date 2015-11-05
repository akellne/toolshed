#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import datetime
import lxml.html
import json
import requests

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
            #load feed first, since not working with lxml directly
            r = requests.get(URL)

            #load url and parse it with html parser
            root = lxml.html.fromstring(r.text.encode("utf-8"))

            #get relevant part
            #"//img[contains(@src,'kdm')]")
            kdm = "could not find king of the month"
            for cols in root.xpath("//div[@class='col-md-4']"):
                if "kdm" in cols.find("img").attrib["src"]:
                    # king of the month picture
                    kdm = cols.find("div/p").text_content()
                    break

            text = "--- King of the Month ---\n%s" % ( kdm)

        except Exception, e:
            print e
            text = "Sorry, burgerking parser is broken. Cannot get " \
                   "the King of the Month"

        return text.encode("utf-8")

