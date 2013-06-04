#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import locale
import datetime
import lxml.html
import json

from base import Plugin


class Analyse(Plugin):
    """
    class to analyse the current irc
    """
    NAME    = "Analyse"
    AUTHOR  = "kellner@cs.uni-goettingen.de"
    VERSION = (0, 0, 1)
    ENABLED = True
    HELP    = "!analyse  shows the analyse of the irc"

    def __init__(
        self, ircbot, cache_time=datetime.timedelta(days=1),
        random_message=[None, None]
    ):
        Plugin.__init__(self, ircbot, cache_time, random_message)

        #dict to store counts
        self.count = {
            "positive" : 0,
            "negative" : 0,
            "neutral"  : 0,
            "total"    : 0,
        }

        #dict with positive and negative words that are matched
        self.words = {
            "positive" : [],
            "negative" : []
        }
        self._load_words()


    def _load_words(self):
        #load positive words
        try:
            with file("plugins/positive.txt", "r") as f:
                for line in f.readlines():
                    if line.strip() != "" and not line.startswith("#"):
                        self.words["positive"].append(line.strip())
        except IOError, e:
            self.log.error(e)

        #load negative words
        try:
            with file("plugins/negative.txt", "r") as f:
                for line in f.readlines():
                    if line.strip() != "" and not line.startswith("#"):
                        self.words["negative"].append(line.strip())
        except IOError, e:
            self.log.error(e)
        print self.words

    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)

        #remove some characters
        for s in (".", ",", "!"):
            msg = msg.replace(s, "")

        words = msg.lower().split(" ")
        for w in words:
            self.count["total"] += 1
            if w in self.words["positive"]:
                self.count["positive"] += 1
            elif w in self.words["negative"]:
                self.count["negative"] += 1
            else:
                self.count["neutral"] += 1

        if msg == "!analyse":
            self.ircbot.switch_personality("yogeshwar")

            #get data from cache
            #reload_data, self.days = self.load_cache()
            #if reload_data:
                #reload the data, if too old
            #    self.days = self._get_dishes()
            #    self.save_cache(data=self.days)

            message =  "--- sentiment analysis ---\n"
            message += "%2.2f %% positive  %2.2f %% negative  "\
                       "%2.2f %% unknown\n" % (
                            self.count["positive"] / float(self.count["total"]) * 100,
                            self.count["negative"] / float(self.count["total"]) * 100,
                            self.count["neutral"] / float(self.count["total"]) * 100
                       )

            #finally, send the message with the
            self.ircbot.privmsg(params[0], message)

            self.ircbot.reset_personality()


#a = Analyse(None)
#for
