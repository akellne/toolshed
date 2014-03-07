#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from base import Plugin

#random messages



class Static(Plugin):
    """
    class for sending a bahn durchsage
    """
    NAME     = "Durchsage"
    AUTHOR   = "konrad.rieck@uni-goettingen.de"
    VERSION  = (0, 0, 1)
    ENABLED  = True
    HELP     = ""
    CHANNELS = []

    def __init__(
        self, ircbot, cache_time=None,
        random_message=[4 * 60 * 60, 8 * 60 * 60] # between 4 h and 8 h
    ):
        Plugin.__init__(self, ircbot, cache_time, random_message)
        
    
    def on_init(self):
        #start random message timer on plugin initialization
        self.log.debug("Starting random message timer...") 
        self.start_random_message_timer()


    def get_train(self):
        r = random.random()
        if r < 0.33:
            return "RE %5d" % random.randint(10000,99999)
        elif r < 0.66:
            return "IC %4d" % random.randint(1000,9999)
        else:
            return "ICE %3d" % random.randint(100,999)

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
        return '%d:%.2d' % (random.randint(0,23), random.randint(0,59))

    def get_reason(self):
        reasons = open('plugins/durchsage_g.txt').read().splitlines()
        return random.choice(reasons).strip()

    def durchsage(self):
        (x,y) = self.get_cities()

        r = random.random()
        if r < 0.10:
            text = "Vorsicht an Gleis %d, ein Zug fährt durch!" % random.randint(1,9)
        elif r < 0.20:
            text = "Information zu %s, nach %s über %s, Abfahrt %s, " \
                   "heute in umgekehrter Wagenreihung." % \
                   (self.get_train(), x, y, self.get_time())
        else:
            text = "Information zu %s nach %s über %s, Abfahrt %s, " \
                   "heute circa %d Minuten später. %s." % \
                   (self.get_train(), x, y, self.get_time(), \
                    self.get_delay(), self.get_reason())

        # Make action
        text = "\x01ACTION " + text + "\x01"
        return text


    def on_random_message(self):
        for channel in self.ircbot.channels:
            if self.is_in_channel(channel):
                self.ircbot.privmsg(self.ircbot.channel, self.durchsage())
        self.start_random_message_timer()


    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)

        if not self.is_in_channel(params[0]):
            #plugin not available in the channel => return
            return

        if msg == "!durchsage":
            self.ircbot.privmsg(params[0], self.durchsage())

        if "bahn" in msg and random.random() < 0.5:
            self.ircbot.privmsg(params[0], self.durchsage())
