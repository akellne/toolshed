#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import asyncore
import datetime
import time
import logging
import random
import signal
import argparse
import ConfigParser

from utils.ircclient import IRCClient, ERR_NICKNAMEINUSE, RPL_MOTD, \
    RPL_ENDOFMOTD
from plugins import get_plugins

#name and version of the bot
NAME    = "ircb"
VERSION = (0, 0, 3)

#config file
CONFIG_FILE = os.path.expanduser('~/.toolshedrc')

#setup logger for the ircbot
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("IRCBot")

#greetings that are randomly chosen
GREETINGS = [
    "Bonjour.", "Salut.", "Hallo.", "Konnichiwa!", "Moin.",
    "Hej!", "¡Hola!", "¡Buenos días!", "Buon giorno!",
    "Hyvää päivää!", "Hoi!", "Goedendag!", "Selam!", "Iyi günler!",
    "Bon dia!", "Moinsen.", "Hallöchen Popöchen"
]

#farewells that are randomly chosen
FAREWELLS = [
    "Au revoir.", "Salut.", "À bientôt.", "À plus tard.",
    "À la prochaine.", "Bonne journée!", "Sayounara!", "Ciao.",
    "¡Hasta luego!", "¡Adiós!", "Arrivederci!", "Alla prossima!",
    "Näkemiin!", "Nähdään pian!", "Eyvallah!", "A reveure!",
    "Tchüssikowski", "Bis Baldrian", "Man siebt sich!", "Tschö mit ö",
    "Pfiat di", "Servus", "Dosvedanja", "Hade", "Horrido", 
    "Wiederschaun, reingehaun!", "Schleich mi", "Bis denne"
]

class IRCBot(IRCClient):
    
    ENABLE_GREETINGS = False
    
    """
    irc bot that can be extended by plugins
    """
    def __init__(
        self, server, port, nick, channels, realname,
        no_message_logging=[]
    ):
        log.debug("Connecting to %s:%s ..." % (server, port))
        IRCClient.__init__(self, server, port, no_message_logging)

        self.nickname              = nick
        self.channels              = channels
        self.trigger_once_commands = []
        self.shutdown_trigger_once = False

        #set nickname, user after MOTD
        self.user(self.nickname, "hostname", "servername", ":" + realname)
        self.nick(self.nickname)

        #get all enabled plugins
        self.plugins   = []
        for plugin in get_plugins():
            if plugin.ENABLED:
                #init enabled plugins
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
        sender = (prefix.split("!")[0].split(":")[-1] if prefix else None);

        #handle incoming messages
        if cmd == RPL_ENDOFMOTD:
            #join all channels after receiving MOTD
            for channel in self.channels:
                channel,_,key = channel.partition(':')
                self.join(channel, key)

                #random greeting
                if IRCBot.ENABLE_GREETINGS:
                    if (random.random() > 0.66):
                        self.privmsg(channel, random.choice(GREETINGS))

                #trigger once commands to itself
                for trigger_cmd in self.trigger_once_commands:
                    self.handle_message(
                        channel, trigger_cmd, "PRIVMSG", channel
                    )

            if self.shutdown_trigger_once:
                #if shutdown_trigger_once flag is set, shutdown the bot
                #after executing the commands
                log.debug(
                    "Shutting down the bot because "\
                    "'shutdown_trigger_once' flag is set."
                )
                self.shutdown()

            #start random message timer for each plugins
            for plugin in self.plugins:
                plugin.start_random_message_timer()


        elif cmd == ERR_NICKNAMEINUSE:
            #nick name in use => add underscore
            self.nickname += "_"
            log.debug(
                "Nickname already in use. Now " \
                "trying '%s'" % self.nickname
            )
            self.nick(self.nickname)

        elif cmd == "PRIVMSG":
            #handle incoming PRIVMSG message
            if tail == "!help":
                #return help for all enabled plugins
                self.switch_personality("lilhelper")
                in_channel = args[0].startswith('#')

                #add help text for overall help of the bot
                def help_text():
                    for plugin in self.plugins:
                        if (
                            plugin.HELP and (not in_channel or plugin.is_in_channel(args[0]))
                        ):
                            #add help text for plugins
                            yield str(plugin.HELP)

                s = '\n'.join(help_text())
                if s:
                    target = (args[0] if in_channel else sender)
                    self.privmsg(target, "--- help---\n%s" % s)

                self.reset_personality()


        #delegate incoming message to plugin
        for plugin in self.plugins:
            #when a message is received delegate it to the plugins
            try:
                if cmd == "PRIVMSG":
                    try:
                        plugin.on_privmsg_ex(sender, tail, *args);

                    except AttributeError:
                        in_channel = args[0].startswith('#')
                        args = tuple([args[0] if in_channel else sender] +list(args[1:]));
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
        if IRCBot.ENABLE_GREETINGS:
            for channel in self.channels:
                if (random.random() > 0.66):
                    self.privmsg(channel, random.choice(FAREWELLS))

        #quit from server
        self.quit()
        sys.exit(0)


    def switch_personality(self, nick):
        #self.part(self.channel, "")
        #self.nick(nick)
        #self.join(self.channel)
        pass

    def reset_personality(self):
        #self.switch_personality(self.nickname)
        pass


    def trigger_once(self, cmds, shutdown_trigger_once=True):
        """
        set trigger once commands which are executed after receiving
        MOTD message
        """
        self.shutdown_trigger_once = shutdown_trigger_once
        self.trigger_once_commands = cmds.split(",")


def get_default_config():
    """
    returns the default configuration
    """
    #get default config from corresponding file
    config = ConfigParser.RawConfigParser()
    if not os.path.exists(CONFIG_FILE):
        #create new config file, if not existing yet
        config.add_section("defaults")
        config.set("defaults", "nick", "toolshed")
        config.set("defaults", "realname", "Stan Marsh")
        config.set("defaults", "channels", "")
        config.set("defaults", "server", "irc.efnet.pl:6667")
        config.set("defaults", "commands", "")
        with open(CONFIG_FILE, "wb") as f:
            config.write(f)
        log.info(
            "Create new config file '%s'. Please set " \
            "your defaults in this file." % CONFIG_FILE
        )
    config.read(CONFIG_FILE)

    return config



def main():
    #read default config
    config = get_default_config()

    # command line arguments and default values
    parser = argparse.ArgumentParser(
        description='Python-based IRC Bot.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--nick', help='nickname of bot',
        default=config.get("defaults", "nick")
    )
    parser.add_argument(
        '--realname', help='realname of bot',
        default=config.get("defaults", "realname")
    )
    parser.add_argument(
        '--channel', help='channel[:key] to join',
        default=config.get("defaults", "channels").split(",")
    )
    parser.add_argument(
        '--server', help='name of irc server',
        default=config.get("defaults", "server").split(":")[0]
    )
    parser.add_argument(
        '--port', help='port of irc server', type=int,
        default=config.get("defaults", "server").split(":")[1]
    )
    parser.add_argument(
        '--commands', help='irc commands separated by , (note: use \!)',
        default=config.get("defaults", "commands")
    )

    #parse command line arguments
    args = parser.parse_args()

    #convert channels to list
    if isinstance(args.channel, str):
        args_channels = args.channel.split(",")
    else:
        args_channels = args.channel
    
    #add missing '#' to channels
    channels = []
    for ch in args_channels:
        if not ch.startswith("#"):
            ch = "#%s" % ch
        channels.append(ch)

    log.debug(
        "Starting '%s' python-based IRC bot V%d.%d.%d" % (
            NAME, VERSION[0], VERSION[1], VERSION[2]
        )
    )
    #create the irc bot
    ircb = IRCBot(
        args.server, args.port, args.nick, channels, args.realname,
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
