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
    VERSION  = (0, 0, 2)
    ENABLED  = True
    HELP     = "!uniliga       display the last stoppelhopser results and table\n" \
               "!uniliga+table display the current stoppelhopser table\n" \
               "!uniliga+last  display the last stoppelhopser results\n" \
               "!uniliga+next  display upcoming stoppelhopser match\n" \
               "!uniliga+all   display all stoppelhopser matches"
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

        if msg.startswith("!uniliga"):
            #get data from cache

            self.ircbot.switch_personality(nick="derTitan")

            #load data from cache
            reload_data, data = self.load_cache()
            if data:
                self.matches = data["matches"]
                self.table   = data["table"]
            if reload_data:
                #reload the data, if too old
                self._get_uniliga_results()
                self.save_cache(
                    data={
                        "matches" : self.matches, "table" : self.table
                    }
                )

            #get last and next day
            last_day, next_day = self._get_last_day()

            #build message depending on given parameter
            message = "--- Uni-Liga powered by Stoppelhopser  ---\n\n"
            if msg == "!uniliga":
                message  += "%s\n%s" % (
                    self._match_day(last_day),
                    self._get_table()
                )

            elif msg == "!uniliga+last":
                if last_day is not None:
                    message += self._match_day(last_day)
                else:
                    message += "There is no last day!"

            elif msg == "!uniliga+next":
                if next_day is not None:
                    message += self._match_day(next_day)
                else:
                    message += "There is no next day!"

            elif msg == "!uniliga+table":
                message += self._get_table()

            elif msg == "!uniliga+all":
                for match_day in self.matches.keys():
                    message += "%s\n" % self._match_day(match_day)

            #finally, send the message with the
            self.ircbot.privmsg(params[0], message)

            self.ircbot.reset_personality()


    def _get_uniliga_results(self):
        """
        load the uniliga results from the webpage
        """
        #load url and parse it with html parser
        root = lxml.html.parse(URL)

        #get results from html
        self.matches = collections.OrderedDict([])
        for td in root.xpath(
            "//table[@class='match_list toggle_color_table']//tr/td"
        ):
            if td.attrib.get("colspan") == "7":
                match_day = td.text_content().strip()[0]
                self.matches[match_day] = []
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
                self.matches[match_day].append(match)

        #get table from html
        self.table = []
        i = 0
        for td in root.xpath(
            "//table[@class='league_table_short']//tr/td"
        ):
            if i == 0:
                entry = {}
                entry["place"] = td.text_content().strip()
            elif i == 2:
                entry["team"] = td.text_content().strip()
            elif i == 3:
                entry["games"] = td.text_content().strip()
            elif i == 4:
                entry["diff"] = td.text_content().strip()
            elif i == 5:
                entry["points"] = td.text_content().strip()
                self.table.append(entry)
                i = -1

            i += 1


    def _parse_dt(self, match):
        """
        parse datetime of a match
        """
        return datetime.datetime.strptime(
            "%s%s %s" % (
                match["date"][-6:],
                datetime.datetime.now().year,
                match["time"]
            ),
            "%d.%m.%Y %H:%M"
        )


    def _get_last_day(self):
        """
        returns a tuple (last day, next day) based no current
        date and existing matches
        """
        last_day = None
        next_day = None
        for k, matches in self.matches.items():
            #parse time of first match on match day
            dt = self._parse_dt(matches[0])
            if (datetime.datetime.now() < dt) and next_day is None:
                next_day = int(k)
                break
        if next_day > 1:
            last_day = next_day - 1
        return (str(last_day), str(next_day))


    def _match_day(self, k):
        """
        returns the match day as string
        """
        tmp  = "%s. Spieltag:\n" % k
        tmp += "-------------\n"
        for x in self.matches[k]:
            tmp += "%s %s   %s - %s   %s\n" % (
                x["date"], x["time"], x["teamA"].ljust(20),
                x["teamB"].ljust(20), x["result"]
            )

        return tmp.encode("utf-8")


    def _get_table(self):
        """
        returns the current table
        """
        tmp  = "    Team                   Sp. Diff. Pkt.\n"
        tmp += "------------------------------------------\n"
        for entry in self.table:
            tmp += "%s  %s    %s   %3d   %s\n" % (
                entry["place"], entry["team"].ljust(20), entry["games"],
                int(entry["diff"]), entry["points"]
            )

        return tmp.encode("utf-8")

