#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import datetime
import lxml.html
import json
import collections

from base import Plugin

#URL to the uniliga spielplan page
URL = "http://uni-liga-goettingen.deinsportplatz.de/liga/spielplan.page?id=495"


class UniLiga(Plugin):
    """
    class to parse the uniliga
    """
    NAME     = "Uni Liga"
    AUTHOR   = "kellner@cs.uni-goettingen.de"
    VERSION  = (0, 0, 1)
    ENABLED  = True
    HELP     = "!uniliga  display the current stoppelhopser results "
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

        if msg == "!uniliga":
            #get data from cache

            self.ircbot.switch_personality(nick="derTitan")

            reload_data, message = self.load_cache()
            if reload_data:
                #reload the data, if too old
                message = self._get_uniliga_results()
                self.save_cache(data=message)
            else:
                message = message.encode("utf-8")

            #finally, send the message with the
            self.ircbot.privmsg(params[0], message)

            self.ircbot.reset_personality()


    def _get_uniliga_results(self):
        """
        load the uniliga results from the webpage
        """
        #load url and parse it with html parser
        root = lxml.html.parse(URL)

        matches = collections.OrderedDict([])
        for td in root.xpath(
            "//table[@class='match_list toggle_color_table']//tr/td"
        ):
            if td.attrib.get("colspan") == "7":
                match_day = td.text_content().strip()[0]
                matches[match_day] = []
                i = 0
            else:
                i+= 1

            if i % 7 == 1:
                match = {}
                match["date"] = td.text_content().strip()
            elif i % 7 == 2:
                match["time"] = td.text_content().strip()
            elif i % 7 == 3:
                match["teamA"] = td.text_content().strip()
            elif i % 7 == 5:
                match["teamB"] = td.text_content().strip()
            elif i % 7 == 6:
                match["result"] = td.text_content().strip()
                matches[match_day].append(match)

        tmp = "--- Uni-Liga powered by Stoppelhopser  ---\n"
        for k, v in matches.items():
            tmp += "%s. Spieltag:\n" % k
            for x in v:
                tmp += "   %s %s   %s - %s   %s\n" % (
                    x["date"], x["time"], x["teamA"], x["teamB"],
                    x["result"]
                )

        return tmp.encode("utf-8")

