#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from base import Plugin


#static messages
STATIC_MESSAGES = {
    "!exit" : [
        "I cannot find a door!",
        "is this the last exit to Brooklyn!"
        "I cannot - I am locked up on this server!",
    ],
    "!shutdown" : [
        "no.",
    ],
    "!reboot" : [
        "no.",
        "ok ... eh, wait who do you think you are?"
    ],
    "!die" : [
        "no, I am too young to die.",
        "why should I?"
    ],
    "!kill" : [
        "hey, I am not a contract killer!",
        "so how much do you pay?",
        "be serious nobody is getting killed here!"
    ],
    "!;)" : [
        "the world is elefantastic!",
    ],
    "!currywurst" : [
        "Ruhrpott Carpaccio",
        "Truckerfrühstück",
        "Prenzelbergplatte",
        "Mantateller",
        "Gelsenkirchner Geschnetzeltes",
        "Kreuzberger Filet",
    ],
}


class Static(Plugin):
    """
    class for some static answering of questions
    => on triggering a known command a random message is generated
    """
    NAME     = "Static Messages"
    AUTHOR   = "kellner@cs.uni-goettingen.de"
    VERSION  = (0, 0, 1)
    ENABLED  = True
    HELP     = ""
    CHANNELS = []

    def __init__(
        self, ircbot, cache_time=None, random_message=[None, None]
    ):
        Plugin.__init__(self, ircbot, cache_time, random_message)


    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)

        if not self.is_in_channel(params[0]):
            #plugin not available in the channel => return
            return

        if msg in STATIC_MESSAGES:
            #finally, send the message with the
            self.ircbot.privmsg(
                params[0], random.choice(STATIC_MESSAGES[msg])
            )


