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

from utils.ircclient import IRCClient, ERR_NICKNAMEINUSE, RPL_MOTD, \
    RPL_ENDOFMOTD
from plugins import get_plugins

#name and version of the bot
NAME = "ircb"
VERSION = (0, 0, 2)

#setup logger for the ircbot
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("IRCBot")

#greetings that are randomly chosen
GREETINGS = [
    "Bonjour.", "Salut.", "Hallo.", "Konnichiwa!", "Moin.",
    "Hej!", "¡Hola!", "¡Buenos días!", "Buon giorno!",
    "Hyvää päivää!", "Hoi!", "Goedendag!", "Selam!", "Iyi günler!",
    "Bon dia!"
]

#farewells that are randomly chosen
FAREWELLS = [
    "Au revoir.", "Salut.", "Ã€ bientÃ´t.", "Ã€ plus tard.",
    "Ã€ la prochaine.", "Bonne journÃ©e!", "Sayounara!", "Ciao.",
    "¡Hasta luego!", "¡Adiós!", "Arrivederci!", "Alla prossima!",
    "Näkemiin!", "Nähdään pian!", "Eyvallah!", "A reveure!"
]

class IRCBot(IRCClient):
    """
    irc bot that can be extended by plugins
    """
    def __init__(
        self, server, port, nick, channel, realname,
        no_message_logging=[]
    ):
        log.debug("Connecting to %s:%s ..." % (server, port))
        IRCClient.__init__(self, server, port, no_message_logging)

        self.nickname              = nick
        self.channel               = channel
        self.trigger_once_commands = []
        self.shutdown_trigger_once = False

        #set nickname, user after MOTD
        self.user(self.nickname, "hostname", "servername", ":" + realname)
        self.nick(self.nickname)

        #get all enabled plugins
        self.plugins = []
        for plugin in get_plugins():
            if plugin.ENABLED:
                log.debug("Adding enabled plugin '%s'..." % plugin)
                self.plugins.append(plugin(self))
                self.plugins[-1].on_init()
            else:
                log.debug("Skipping disabled plugin '%s'..." % plugin)


    def handle_message(self, prefix, tail, cmd, *args):
        """
        handle incoming irc messages
        """
        IRCClient.handle_message(self, prefix, tail, cmd, *args)

        #handle incoming messages
        if cmd == RPL_ENDOFMOTD:
            #join the channel after receiving MOTD
            self.join(self.channel)
            #random greeting
            self.privmsg(self.channel, random.choice(GREETINGS))

            #trigger once commands to itself
            for trigger_cmd in self.trigger_once_commands:
                print "FOO", trigger_cmd
                self.handle_message(prefix, trigger_cmd, "PRIVMSG", self.channel)

            if self.shutdown_trigger_once:
                #if shutdown_trigger_once flag is set, shutdown the bot
                #after executing the commands
                log.debug(
                    "Shutting down the bot because "\
                    "'shutdown_trigger_once' flag is set."
                )
                self.shutdown()

        elif cmd == ERR_NICKNAMEINUSE:
            #nick name in use => add underscore
            self.nickname += "_"
            log.debug(
                "Nickname already in use. Now " \
                "trying '%s'" % self.nickname
            )
            self.nick(self.nickname)


        #delegate incoming message to plugin
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
        #self.part(self.channel, "")
        self.nick(nick)
        #self.join(self.channel)


    def reset_personality(self):
        self.switch_personality(self.nickname)


    def trigger_once(self, cmds, shutdown_trigger_once=True):
        """
        set trigger once commands which are executed after receiving
        MOTD message
        """
        self.shutdown_trigger_once = shutdown_trigger_once
        self.trigger_once_commands = cmds.split(",")


def main():
    # command line arguments and default values
    parser = argparse.ArgumentParser(
        description='Python-based IRC Bot.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--nick', help='nickname of bot', default='toolshed'
    )
    parser.add_argument(
        '--realname', help='realname of bot', default='Stan Marsh'
    )
    parser.add_argument(
        '--channel', help='channel to join', default='#mlsec'
    )
    parser.add_argument(
        '--server', help='name of irc server',
        default='irc.servercentral.net'
    )
    parser.add_argument(
        '--port', help='port of irc server',
        type=int, default=6667
    )
    parser.add_argument(
        '--commands', help='irc commands separated by ,',
        default=""
    )

    #parse command line arguments
    args = parser.parse_args()
    if not args.channel.startswith("#"):
        args.channel = "#" + args.channel

    log.debug(
        "Starting '%s' python-based IRC bot V%d.%d.%d" % (
            NAME, VERSION[0], VERSION[1], VERSION[2]
        )
    )
    #create the irc bot
    ircb = IRCBot(
        args.server, args.port, args.nick, args.channel, args.realname,
        no_message_logging=[RPL_MOTD]
    )

    #add signal handler that is called on killing the process
    #=> shutdown the bot nicely
    signal.signal(signal.SIGTERM, lambda signal, frame: ircb.shutdown())

    if args.commands:
        print args.commands
        ircb.trigger_once(args.commands)

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        ircb.shutdown()


if __name__ == "__main__":
    main()
