#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import urllib2
import re
import json

from base import Plugin

#URL to the ifi news ics file
URL = "http://filepool.informatik.uni-goettingen.de/gcms/ifi/news/ifi_cal.php"

#dateformat used in ics files (date with and without time)
ICS_UTC="%Y%m%dT%H%M%SZ"
ICS_DATE="%Y%m%d"

#hours that needs to be shifted for correct times of ics files
TIME_SHIFT = datetime.timedelta(hours=2)


class IfINews(Plugin):
    """
    class to parse the ics calendar of the IfI webpage
    """
    NAME     = "IfI News"
    AUTHOR   = "kellner@cs.uni-goettingen.de"
    VERSION  = (0, 0, 1)
    ENABLED  = True
    HELP     = "!ifi  shows the cureent ifi news"
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

        if msg == "!ifi":
            self.ircbot.switch_personality(nick="chiefsec")

            #get data from cache
            reload_data, self.data = self.load_cache()
            if reload_data:
                #reload the data, if too old
                self.data = self._get_news()
                self.save_cache(data=self.data)
            else:
                self.data = self.data.encode("utf-8")

            message = "--- IfI News: ---\n"
            message += self.data

            #finally, send the message with the
            self.ircbot.privmsg(params[0], message)

            self.ircbot.reset_personality()


    def _get_news(self):
        """
        load ifi news from ifi webpage's ics file
        """
        #load url and parse it with simple regex
        f   = urllib2.urlopen(URL)
        ics = f.read()

        #parse ics data
        li = []
        for res in re.compile(
            r'BEGIN:VEVENT(.*?)END:VEVENT', re.I|re.S
        ).findall(ics):
            #parse every calendar item found
            item = {}
            for line in res.split("\n"):
                if line.strip():
                    #replace stuff for all day events that use another format
                    for x in ("DTSTART", "DTEND"):
                        line = line.replace(
                            "%s;VALUE=DATE" % x,
                            "%s" % x 
                        )

                    k, _, v = line.partition(":")
                    if k in ("SUMMARY", "DTSTART", "DTEND"):
                        if k == "SUMMARY":
                            item[k.lower()] = v.strip()
                        else:
                            try:
                                #try to parse date and time
                                item[k.lower()] = datetime.datetime.strptime(
                                    v.strip(), ICS_UTC
                                ) + TIME_SHIFT
                                item["onlydate"] = False
                            except Exception:
                                try:
                                    #try to parse only date
                                    item[k.lower()] = datetime.datetime.strptime(
                                        v.strip(), ICS_DATE
                                    )
                                    item["onlydate"] = True
                                except Exception:
                                    pass

            li.append(item)

        #build message
        tmp = ""
        for item in sorted(li, key=lambda item: item["dtstart"]):
            if item["dtstart"] >= datetime.datetime.today():
                if not item["onlydate"]:
                    tmp += "%sh to %sh:  %s\n" % (
                        item["dtstart"].strftime("%a %d. %b %Y, %H:%M"),
                        item["dtend"].strftime("%H:%M"),
                        item["summary"].replace("\\", "")
                    )
                else:
                    tmp += "%sh %s\n" % (
                        item["dtstart"].strftime("%a %d. %b %Y"),
                        item["summary"].replace("\\", "")
                    )

        return tmp.decode("latin-1").encode("utf-8")

