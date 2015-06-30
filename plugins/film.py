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
    ENABLED  = False
    HELP     = "!film  return description from filmlexikon"
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
            title = ' '.join(msg.split(' ')[1:])
            message = self.get_film(title)
            self.ircbot.privmsg(params[0], message)

    def get_film(self, title):
        """ load results from kabeleins.de """

        title = title.lower()
        try:            
            root = lxml.html.parse(URL + urllib.quote(title))
            link = root.xpath('//a[@class="linkstyle"]')
            link = filter(lambda x: len(x.xpath('string()')) > 3, link)
            
            if len(link) == 0:
                tmp = "Den Film kenne ich nicht!" 
                return tmp.strip()

            idx = 0
            exact = False
            for (i,l) in enumerate(link):
                x = l.xpath('string()').lower()
                if x.strip() == title.strip():
                    idx = i
                    exact = True

            if not exact and len(link) > 1:
                tmp = "Ich kenne folgende Filme:\n"
                for l in link:
                    tmp += "  %s\n" % l.xpath('string()').encode("utf-8")
            else:
                root = lxml.html.parse(MAIN_URL + link[idx].get('href'))
                entry = root.xpath('//div[@class="filmlexikon-db-ausgabe"]')[0]
                lines = entry.xpath('string()').split('\n')
                lines = map(lambda x: x.strip().encode("utf-8"), lines)

                # Get name
                name = entry.getchildren()[0].text.encode("utf-8")
                idx = lines.index('Land, Jahr:')
                year = lines[idx+1]
                tmp = "--- %s (%s) ---\n" % (name, year)

                # Get description
                idx = lines.index('Filmkritik:') 
                tmp += lines[idx+1].replace('. ', '.\n')
            
        except Exception,e: 
            self.log.debug(str(e))
            tmp = "Keine Ahnung. Mein Parser ist kaputt!"
        finally:
            return tmp.strip()

