#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from base import Plugin


#random messages
RANDOM_MESSAGES = [
    "That's just the way it is!",
    "Oh, Elvis seems to be around.",
    "Life is great!"
]


class Static(Plugin):
    """
    class for testing the new random message functionality
    """
    NAME    = "Random Messages"
    AUTHOR  = "kellner@cs.uni-goettingen.de"
    VERSION = (0, 0, 1)
    ENABLED = True
    HELP    = ""

    def __init__(
        self, ircbot, cache_time=None, 
        random_message=[600, 3600] #between 10 min and 60 min
    ):
        Plugin.__init__(self, ircbot, cache_time, random_message)

    
    def on_random_message(self):
        self.ircbot.privmsg(self.ircbot.channel, random.choice(RANDOM_MESSAGES))
        self.start_random_message_timer()

