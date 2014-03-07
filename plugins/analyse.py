#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
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
    NAME     = "Analyse"
    AUTHOR   = "kellner@cs.uni-goettingen.de"
    VERSION  = (0, 0, 1)
    ENABLED  = True
    HELP     = "!analyse  shows the average of the irc analyse\n" 
    CHANNELS = []

    def __init__(
        self, ircbot, cache_time=datetime.timedelta(days=1),
        random_message=[None, None]
    ):
        Plugin.__init__(self, ircbot, cache_time, random_message)

        #get data from cache
        reload_data, self.count = self.load_cache()
        if not self.count:
            #not cached yet, reset counts
            self.count = {}

        #dict with positive and negative words that are matched
        self.words = {}

        #load wordlists
        self._load_words()


    def _load_words(self):
        #load positive and negative words with scores
        try:
            for t in ("positive", "negative"):
                self.words[t] = {}
                with file("plugins/%s.txt" % t, "r") as f:
                    for line in f.readlines():
                        if line.strip() == "" or line.startswith("#"):
                            #skip comments and empty lines
                            continue

                        res = re.compile(
                            "^(.*?)\|(.*?)\s+(.*?)\s+(.*?)$"
                        ).search(line.strip())
                        if res:
                            for word in (
                                res.group(4).split(",") + [res.group(1)]
                            ):
                                #store same score for word and its variations
                                self.words[t][word.lower()] = float(3)
        except IOError, e:
            self.log.error(e)


    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)

        if not self.is_in_channel(params[0]):
            #plugin not available in the channel => return
            return

        if msg.startswith("!analyse"):
            #react to command

            self.ircbot.switch_personality("yogeshwar")

            message =  "--- sentiment analysis ---\n"
            total = {
                "positive" : 0.0,
                "positive_score" : 0.0,
                "negative" : 0.0,
                "negative_score" : 0.0,
                "neutral" : 0.0,
            }
            for k in sorted(self.count.keys()):
                dt = datetime.datetime.strptime(k, "%Y%m%d")
                total["positive"] += (
                    self.count[k]["positive"] / 
                    float(self.count[k]["total"]) * 100
                ) / len(self.count.keys())
                total["positive_score"] += self.count[k]["positive_score"]
                total["negative"] += (
                    self.count[k]["negative"] / 
                    float(self.count[k]["total"]) * 100
                ) / len(self.count.keys())
                total["negative_score"] += self.count[k]["negative_score"]
                total["neutral"] += (
                    self.count[k]["neutral"] / 
                    float(self.count[k]["total"]) * 100
                ) / len(self.count.keys())
                
            from_ = datetime.datetime.strptime(self.count.keys()[0], "%Y%m%d")
            to_   = datetime.datetime.strptime(self.count.keys()[-1], "%Y%m%d")
            message = "--- sentiment analysis from %s to %s ---\n" \
                      "positive: %2.2f%% [score: %2.2f]\n" \
                      "negative:  %2.2f%% [score: %2.2f]\n" \
                      "neutral:  %2.2f%% (unknown)\n" % (
                          from_.strftime("%d/%m/%Y"),
                          to_.strftime("%d/%m/%Y"),
                          total["positive"], total["positive_score"],
                          total["negative"], total["negative_score"],
                          total["neutral"]
                      )

            #finally, send the message with the
            self.ircbot.privmsg(params[0], message)

            self.ircbot.reset_personality()

        else:
            #not a command => analyse message

            #get current date and use it as key for storing counts
            dt = datetime.datetime.now().strftime("%Y%m%d")
            if dt not in self.count:
                self.count[dt] = {
                    "positive"       : 0,
                    "negative"       : 0,
                    "positive_score" : 0.0,
                    "negative_score" : 0.0,
                    "neutral"        : 0,
                    "total"          : 0,
                }


            #remove some characters
            for s in (".", ",", "!"):
                msg = msg.replace(s, "")

            #split message by spaces
            words = msg.lower().split(" ")
            for w in words:
                #increase counts depending on word type
                self.count[dt]["total"] += 1
                if w in self.words["positive"]:
                    self.count[dt]["positive"] += 1
                    self.count[dt]["positive_score"] += self.words["positive"][w]
                elif w in self.words["negative"]:
                    self.count[dt]["negative"] += 1
                    self.count[dt]["negative_score"] += self.words["negative"][w]
                else:
                    self.count[dt]["neutral"] += 1


    def on_quit(self):
        Plugin.on_quit(self)

        #save all results in the cache
        self.save_cache(data=self.count)


