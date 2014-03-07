#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import locale
import datetime
import lxml.html
import json

from base import Plugin


#URL to the lectures
URL = "http://univz.uni-goettingen.de/veranstaltungsmonitor/public/?piznr=2412"


class Lectures(Plugin):
    """
    class to parse the lectures
    """
    NAME     = "Lectures"
    AUTHOR   = "kellner@cs.uni-goettingen.de"
    VERSION  = (0, 0, 1)
    ENABLED  = True
    HELP     = "!lectures   show today's lectures at IfI\n"
    CHANNELS = []

    def __init__(
        self, ircbot, cache_time=datetime.timedelta(minutes=5),
        random_message=[None, None]
    ):
        Plugin.__init__(self, ircbot, cache_time, random_message)

        #set locale to German (required for parsing the German date)
        try:
            locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
        except Exception, e:
            print "de_DE.UTF-8 needs to be generated so that the " \
                  "date can be parsed correctly! (use 'dpkg-" \
                  "reconfigure locales' to generate the " \
                  "corresponding locales)"
            sys.exit(1)


    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)

        if not self.is_in_channel(params[0]):
            #plugin not available in the channel => return
            return

        if msg in ("!lectures"):
            self.ircbot.switch_personality("infod")

            #get data from cache
            reload_data, self.lectures = self.load_cache()
            if reload_data:
                #reload the data, if too old
                self.lectures = self._get_lectures()
                self.save_cache(data=self.lectures)

            message = ""
            for lecture in self.lectures:
                message += "%s - %s" % (
                    lecture["time"], lecture["title"],
                )
                if lecture["lecturer"]:
                    message += " (%s)" % lecture["lecturer"]
                message += ", room %s\n" % lecture["room"]

            #finally, send the message with the
            self.ircbot.privmsg(params[0], message.strip().encode("utf-8"))

            self.ircbot.reset_personality()


    def _get_lectures(self):
        """
        get lectures from webpage
        """
        #load url and parse it with html parser
        root = lxml.html.parse(URL)

        #get the lectures
        lectures = []
        for x in root.findall("//div[@id='id_content']/table/tr"):
            if x.get("bgcolor") != "#c56529":
                #if not heading => get item
                items = x.findall("td[@class='lecture_started']")
                if items:                
                    lecturer = None
                
                    if (len(items) >= 1) and (items[1].find("span") != None):
                        lecturer = items[1].find("span").text.strip()
                    lectures.append({
                        "time"     : items[0].text.strip(),
                        "title"    : items[1].text.strip(),
                        "lecturer" : lecturer,
                        "no"       : items[2].text.strip(),
                        "room"     : items[3].text.strip(),
                    })

        return lectures


