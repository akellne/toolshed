#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from base import Plugin

#random messages
RANDOM_MESSAGES = open('plugins/random_messages.txt').read().splitlines()

class Static(Plugin):
    """
    class for testing the new random message functionality
    """
    NAME     = "Random Messages"
    AUTHOR   = "kellner@cs.uni-goettingen.de"
    VERSION  = (0, 0, 1)
    ENABLED  = True
    HELP     = ""
    CHANNELS = []

    def __init__(
        self, ircbot, cache_time=None,
        random_message=[1 * 60 * 60, 5 * 60 * 60] # between 1 h and 5 h
    ):
        Plugin.__init__(self, ircbot, cache_time, random_message)


    def on_random_message(self):
        for channel in self.ircbot.channels:
            if self.is_in_channel(channel):
                self.ircbot.privmsg(
                    channel, random.choice(RANDOM_MESSAGES)
                )

        self.start_random_message_timer()

