#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import urllib2
import re
import json

from base import Plugin

#URL to fixtures
URL = "http://worldcup.sfg.io/matches/today"

#URL to groups
URL2 = "http://worldcup.sfg.io/group_results"

#dateformat used
DTFORMAT="%Y-%m-%dT%H:%M:%S"

#hours that needs to be shifted for correct times of ics files
TIME_SHIFT = datetime.timedelta(hours=5)


class WM(Plugin):
    """
    class to parse the json of worldcup.sfg.io
    """
    NAME     = "WM 2014"
    AUTHOR   = "kellner@cs.uni-goettingen.de"
    VERSION  = (0, 0, 1)
    ENABLED  = False
    HELP     = "!wm  shows the current WM fixtures\n" \
               "!wm+<group> shows the table of the WM group"
    CHANNELS = []

    def __init__(
        self, ircbot, cache_time=datetime.timedelta(minutes=1),
        random_message=[None, None]
    ):
        Plugin.__init__(self, ircbot, cache_time, random_message)


    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)

        if not self.is_in_channel(params[0]):
            #plugin not available in the channel => return
            return

        if msg.startswith("!wm"):
            #self.ircbot.switch_personality(nick="KMH")

            #NO CACHING

            if msg == "!wm":
                message = "--- WM 2014 today ---\n"
                message += self._get_fixtures()

            elif msg in (
                "!wm+A", "!wm+B", "!wm+C", "!wm+D", "!wm+E", "!wm+F",
                "!wm+G", "!wm+H",
            ):
                message = "--- WM 2014 - Group %s ---\n" % msg[-1]
                message += self._get_groups(msg[-1])

            #finally, send the message with the
            self.ircbot.privmsg(params[0], message)

            #self.ircbot.reset_personality()


    def _get_groups(self, group):
        f      = urllib2.urlopen(URL2)
        teams = json.loads(f.read())

        tmp = "Country  GP   W D L  GF GA  GD PTS\n"
        for team in teams:
            group_no = ord(group) - 64
            if team["group_id"] == group_no:
                tmp += "%s      %d    %d %d %d   %d  %d  %2d  %d\n" % (
                    team["fifa_code"],
                    team["wins"] + team["draws"] + team["losses"],
                    team["wins"],
                    team["draws"],
                    team["losses"],
                    team["goals_for"],
                    team["goals_against"],
                    team["goals_for"] - team["goals_against"],
                    team["wins"] * 3 + team["draws"]
                )

        return tmp.decode("latin-1").encode("utf-8")



    def _get_fixtures(self):
        """
        parse the WM fixtures
        """
        #load url and parse it with simple regex
        f   = urllib2.urlopen(URL)
        fixtures = json.loads(f.read())

        tmp = ""
        for fixture in sorted(fixtures, key=lambda item: item["datetime"]):
            dt = datetime.datetime.strptime(
                fixture["datetime"][:19], DTFORMAT
            ) + TIME_SHIFT

            tmp += "%s - %s" % (
                fixture["home_team"]["code"].ljust(3),
                fixture["away_team"]["code"].ljust(3),
            )
            if fixture["status"] != "future":
                tmp += "   %2d : %2d" % (
                    fixture["home_team"]["goals"],
                    fixture["away_team"]["goals"],
                )
            else:
                tmp += "      :   "

            tmp += "  at %s" % fixture["location"]

            if fixture["status"] == "future":
                tmp += "  %sh" % dt.strftime("%H:%M")
            else:
                tmp += "  [%s]" % fixture["status"]

            tmp += "\n"

        return tmp.decode("latin-1").encode("utf-8")


if __name__ == "__main__":
    wm = WM(None)
    wm._get_groups("A")
