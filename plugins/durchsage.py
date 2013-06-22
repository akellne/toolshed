#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from base import Plugin

#random messages



class Static(Plugin):
    """
    class for sending a bahn durchsage
    """
    NAME    = "Durchsage"
    AUTHOR  = "konrad.rieck@uni-goettingen.de"
    VERSION = (0, 0, 1)
    ENABLED = True
    HELP    = ""

    def __init__(
        self, ircbot, cache_time=None, 
        random_message=[3 * 60 * 60, 9 * 60 * 60] # between 3 h and 9 h
    ):
        Plugin.__init__(self, ircbot, cache_time, random_message)

    def get_train(self):
        r = random.random()
        if r < 0.33:
            return "RE %5d" % random.randint(10000,100000)
        elif r < 0.66:
            return "IC %4d" % random.randint(1000,10000)
        else:
            return "ICE %3d" % random.randint(100,1000)

    def get_delay(self):
        mins = [5, 10, 15, 20, 30, 40, 45, 60, 90, 120]
        return random.choice(mins)

    def get_cities(self):
        cities = open('plugins/durchsage_s.txt').read().splitlines()
        y = x = random.choice(cities).strip()
        while y == x:
            y = random.choice(cities).strip()
        return (x,y)

    def get_time(self):
        return '%d:%.2d' % (random.randint(0,24), random.randint(0,60))

    def get_reason(self):
        reasons = open('plugins/durchsage_g.txt').read().splitlines()
        return random.choice(reasons).strip()
    
    def durchsage(self):
        (x,y) = self.get_cities()
        text = "Information zu %s nach %s über %s, Abfahrt %s, " \
               "heute circa %d Minuten später. %s." % \
               (self.get_train(), x, y, self.get_time(), \
                self.get_delay(), self.get_reason())
        return text

    def on_random_message(self):
        self.ircbot.privmsg(self.ircbot.channel, durchsage())
        self.start_random_message_timer()

    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)

        if msg == "!durchsage":
            self.ircbot.privmsg(params[0], self.durchsage())
            
        if "bahn" in msg and random.random() < 0.5:
            self.ircbot.privmsg(params[0], self.durchsage())
