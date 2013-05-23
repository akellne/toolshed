#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import asyncore
import datetime
import time
import logging
import random
import signal
import argparse

from utils.ircclient import IRCClient
from plugins import get_plugins

# command line arguments and default values
parser = argparse.ArgumentParser(description='Python-based IRC Bot.', 
         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--nick', help='nickname of bot', 
                    default='toolshed')
parser.add_argument('--realname', help='realname of bot',
                    default='Stan Marsh')
parser.add_argument('--channel', help='channel to join',
                    default='#mlsec')
parser.add_argument('--server', help='name of irc server',
                    default='irc.servercentral.net')
parser.add_argument('--port', help='port of irc server',
                    type=int, default=6667)

args = parser.parse_args()

#name and version of the bot
NAME = "ircb"
VERSION = (0, 0, 2)

#setup logger for the ircbot
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("IRCBot")

#greetings that are randomly chosen
GREETINGS = [
    "Bonjour.", "Salut."
]

#farewells that are randomly chosen
FAREWELLS = [
    "Au revoir.", "Salut.", "À bientôt.", "À plus tard.",
    "À la prochaine.", "Bonne journée!"
]


class IRCBot(IRCClient):
    """
    irc bot that can be extended by plugins
    """
    def __init__(self, server, port, nick, channel):
        IRCClient.__init__(self, server, port)
        
        self.nickname = nick
        self.channel  = channel
        
        #get all enabled plugins
        self.plugins = []
        for plugin in get_plugins():
            if plugin.ENABLED:
                log.debug("Adding enabled plugin '%s'..." % plugin)
                self.plugins.append(plugin(self))
                self.plugins[-1].on_init()
            else:
                log.debug("Skipping disabled plugin '%s'..." % plugin)
        
        #set nickname, user and join the channel
        self.nick(self.nickname)
        self.user(self.nickname, "hostname", "servername", ":" + args.realname)
        self.join(self.channel)
        
        #random greeting
        self.privmsg(self.channel, random.choice(GREETINGS))


    def handle_message(self, prefix, tail, cmd, *args):
        """
        handle incoming irc messages
        """
        IRCClient.handle_message(self, prefix, tail, cmd, *args)

        for plugin in self.plugins:
            #when a message is received delegate it to the plugins
            try:
                if cmd == "PRIVMSG":
                    plugin.on_privmsg(tail, *args)
                    
            except Exception, e:
                log.exception("Could not handle message: %s" % e)


    def shutdown(self):
        """
        shutdown the bot, i.e. send farewell message, 
        quit the connection the irc server and exit the bot
        """
        for plugin in self.plugins:
            #delegate shutdown to the plugins
            try:
                plugin.on_quit()
            except Exception, e:
                log.exception("Could not handle message: %s" % e)

        #send farewell message
        self.privmsg(self.channel, random.choice(FAREWELLS))

        #quit from server
        self.quit()
        sys.exit(0)
        
    def switch_personality(self, nick):
        self.part(self.channel, "")
        time.sleep(1)
        self.nick(nick)
        time.sleep(1)
        self.join(self.channel)
        
    def reset_personality(self):
        self.switch_personality(self.nickname)

def main():
    log.debug(
        "Starting '%s' python-based IRC bot V%d.%d.%d" % (
            NAME, VERSION[0], VERSION[1], VERSION[2]
        )
    )
    #create the irc bot
    ircb = IRCBot(args.server, args.port, args.nick, args.channel)
    
    #add signal handler that is called on killing the process
    #=> shutdown the bot nicely
    signal.signal(signal.SIGTERM, lambda signal, frame: ircb.shutdown())
    
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        ircb.shutdown()


if __name__ == "__main__":
    main()
