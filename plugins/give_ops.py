#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

from base import Plugin



class GiveOps(Plugin):
    """ class to give ops to joining users"""
    NAME     = "GiveOps"
    AUTHOR   = "chwress"
    VERSION  = (0, 0, 1)
    ENABLED  = False
    HELP     = ""
    CHANNELS = []

    def __init__(
        self, ircbot, cache_time=datetime.timedelta(hours=1),
        random_message=[None, None]
    ):
        Plugin.__init__(self, ircbot, cache_time, random_message)

        self.__nickname = None


    def on_msg(self, cmd, sender, msg, *params):
        Plugin.on_msg(self, cmd, sender, msg, *params)

        if cmd == 'PRIVMSG' and msg == "\x01VERSION\x01":
            try:
                self.__nickname = params[0]
            except: pass

        if cmd == 'JOIN':
            self.on_join(sender, msg, *params)


    def on_join(self, sender, channel, *params):
        nick = self.__nickname;
        if nick and sender != nick:
            self.ircbot.channel_mode(channel, "+o", sender)
            self.ircbot.privmsg(channel, "Hi %s!" % sender)

