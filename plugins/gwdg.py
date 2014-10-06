#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import locale
import datetime
import lxml.html
import json
import email.utils

from base import Plugin


#URL to GWDG breakdowns
URL = "http://www.gwdg.de/index.php?id=1640&type=100"

#do not show messages older than this
OLDEST_NEWS = datetime.datetime.now() - datetime.timedelta(days=2)



class Gwdg(Plugin):
    """
    class to parse the mensa plan
    """
    NAME     = "GWDG"
    AUTHOR   = "kellner@cs.uni-goettingen.de"
    VERSION  = (0, 0, 1)
    ENABLED  = True
    HELP     = "!gwdg   shows the current breakdowns of GWDG"
    CHANNELS = []

    def __init__(
        self, ircbot, cache_time=datetime.timedelta(days=0),
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

        if msg == "!gwdg":
            self.ircbot.switch_personality("murphy")

            #get data from cache
            reload_data, self.breakdowns = self.load_cache()
            if reload_data:
                #reload the data, if too old
                self.breakdowns = self._get_breakdowns()
                self.save_cache(data=self.breakdowns)

            self.breakdowns = self._get_breakdowns()
            if len(self.breakdowns) > 0:
                message = "--- GWDG-Breakdowns ---\n"
                for b in self.breakdowns:
                    message += "%s  %s\n" % (
                        str(b["pubdate"]), b["title"]
                    )

            else:
                message = "Unbelievable, but there were no " \
                          "breakdowns at GWDG recently!"


            #finally, send the message with the
            self.ircbot.privmsg(params[0], message.strip().encode("utf-8"))

            self.ircbot.reset_personality()


    def _get_breakdowns(self):
        """
        returns breakdowns from GWDG in given timewindow
        """
        #load url and parse it with html parser
        root = lxml.html.parse(URL)

        #get items
        items = []
        for x in root.findall("//item"):
            pubdate = datetime.datetime.fromtimestamp(
                email.utils.mktime_tz(
                    email.utils.parsedate_tz(
                        x.find("pubdate").text[:-6]
                    )
                )
            )
            if pubdate >= OLDEST_NEWS:
                item = {
                    "title"   : x.find("title").text,
                    "pubdate" : str(pubdate),
                    "content" : x.find("description").getnext().text_content(),
                }
                items.append(item)

        return sorted(items, key=lambda x: x["pubdate"], reverse=True)



