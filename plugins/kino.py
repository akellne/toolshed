#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import lxml.html
import json

from base import Plugin

#URL to the kino data 
URL = "http://www.kino.de/kinoprogramm/goettingen"

class Kino(Plugin):
    """ class to parse kino data """
    NAME    = "Kino"
    AUTHOR  = "konrad.rieck@uni-goettingen.de"
    VERSION = (0, 0, 1)
    ENABLED = True

    def __init__(self, ircbot, cache_time=datetime.timedelta(hours=1)):
        Plugin.__init__(self, ircbot, cache_time)

    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)
        
        if msg.startswith("!kino"):
            self.ircbot.switch_personality(nick="popcorn")
            message = self.get_kino()
            self.ircbot.privmsg(params[0], message)
            self.ircbot.reset_personality()

    def get_kino(self):
        """ load results from kino.de """
        try:
            root = lxml.html.parse(URL)
            tmp = "--- Heute im Kino ---\n"

            ul = root.xpath('//ul[@class="cinema-city-list"]')[0]
            for li in ul.getchildren():  
                name = li.find('div/div/a').xpath('string()')
                tmp += "%s\n" % name.strip()
                
                schedule = {}    
                for mo in li.xpath('ul/li'):
                    title = mo.xpath('div[@class="movie-title"]')[0]
                    title = title.xpath('string()').strip()
                
                    show = []    
                    showtimes = mo.xpath('div[@class="movie-showtimes"]')[0]
                    for st in showtimes.xpath('*/p'):
                        st = st.xpath('string()')
                        if st[0].isdigit():
                            show.append(st.strip())
                            
                    if title not in schedule:
                        schedule[title] = []
                    schedule[title].extend(show)

                for title in sorted(schedule.keys()):
                    times = ' '.join(sorted(schedule[title]))
                    if len(title) > 22: title = title[:22] + "..."
                    tmp += "  %-25s  %s\n" % (title[:25], times)
        except:
            tmp = "Keine Ahnung. Mein Parser ist kaputt!"
        finally:    
            return tmp.strip().encode("utf-8")            

