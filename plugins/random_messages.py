#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from base import Plugin


#random messages
RANDOM_MESSAGES = [
    "That's just the way it is!",
    "Oh, Elvis seems to be around.",
    "Life is great!",
    "I sense a disturbance in the Force.",
    "Houston, we have a problem.",
    "I feel the need... the need for speed.",
    "May the force be with you.",
    "I've got a feeling we're not in Kansas anymore.",
    "Go ahead, make my day.",
    "Gentlemen, you can't fight in here! This is the War Room!",
    "I'm king of the world!",
    "Who you gonna call?",
    "But why is the rum gone?",
    "That's the most ridiculous thing I've ever heard.",
    "Looks like I picked the wrong week to quit drinking...",
    "If I only had a brain...",
    "There's no place like home.",
    "Round up the usual suspects.",
    "You can't handle the truth!",
    "Why so serious?",
    "It's alive!",
    "Don't criticize what you can't understand.",
    "Get up, stand up, Stand up for your rights.",
    "Get up, stand up, Don't give up the fight.",
    "Humour. It is a difficult concept.",
    "Who's been holding up the damn elevator?",
    "Logic is the beginning of wisdom; not the end.",
    "Shields up! Rrrrred alert!",
    "I hate prototypes."
    "Hello? Pizza delivery for uh... I.C. Wiener?",
    "Hooray!",
    "Neat!",
    "I'm not insane, my creator had me tested!",
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

