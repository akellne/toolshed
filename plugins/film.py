#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import urllib
import lxml.html
import json

from base import Plugin

#URL to the film data
MAIN_URL = "http://www.kabeleins.de"
URL = "%s/film/filmlexikon//filmtitelsuche/" % MAIN_URL

class Film(Plugin):
    """ class to parse film data """
    NAME     = "Film"
    AUTHOR   = "konrad.rieck@uni-goettingen.de"
    VERSION  = (0, 0, 1)
    ENABLED  = True
    HELP     = "!film  return entry from movie lexicon"
    CHANNELS = []

    def __init__(
        self, ircbot, cache_time=datetime.timedelta(hours=1),
        random_message=[None, None]
    ):
        Plugin.__init__(self, ircbot, cache_time, random_message)

    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)

        if not self.is_in_channel(params[0]):
            #plugin not available in the channel => return
            return

        if msg.startswith("!film"):
            self.ircbot.switch_personality(nick="critic")
            title = msg.split(' ')[1:]
            message = self.get_film(title)
            self.ircbot.privmsg(params[0], message)
            self.ircbot.reset_personality()

    def get_film(self, title):
        """ load results from kabeleins.de """

        try:            
            root = lxml.html.parse(URL + urllib.quote(title))
            link = root.xpath('//a[@class="linkstyle"]')
            
            if len(link) == 0:
                tmp = "Den Film kenne ich nicht!" 
            else:
                root = lxml.html.parse(MAIN_URL + link[-1].get('href'))
                entry = root.xpath('//div[@class="filmlexikon-db-ausgabe"]')[0]
                lines = entry.xpath('string()').split('\n')

                # Get name
                name = entry.getchildren()[0].text
                idx = lines.index('Land, Jahr: ')
                year = lines[idx+1]
                tmp = "--- %s (%s) ---\n" % (name, year)

                # Get description
                idx = lines.index('Filmkritik:')
                tmp += lines[idx+1]
            
        except:
            tmp = "Keine Ahnung. Mein Parser ist kaputt!"
        finally:
            return tmp.strip().encode("utf-8")

