#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import datetime
import lxml.html
import json
import random
import urllib2

from base import Plugin



class YouTube(Plugin):
    """
    class to parse youtube feeds
    """
    NAME    = "Youtube"
    AUTHOR  = "kellner@cs.uni-goettingen.de"
    VERSION = (0, 0, 1)
    ENABLED = True
    HELP    = "!yt  get random youtube link"

    def __init__(
        self, ircbot, cache_time=datetime.timedelta(days=1),
        random_message=[None, None]
    ):
        Plugin.__init__(self, ircbot, cache_time, random_message)

        #load all urls from cache
        reload_data, self.urls = self.load_cache()
        if self.urls is None:
            self.urls = []


    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)

        if msg == "!yt":
            self.ircbot.switch_personality(nick="ytroulet")
            self.ircbot.privmsg(
                params[0],
                random.choice(self.urls).encode("utf-8")
            )
            self.ircbot.reset_personality()

        else:
            res = re.compile(r".*(youtube\.com/.*v=[^&]*)").search(msg)
            if res:
                #create https url
                url = "http://www.%s" % res.group(1)

                if url not in self.urls:
                    #store url, if not existing yet
                    self.urls.append(url)
                    self.save_cache(data=self.urls)

                #get info from youtube url
                info = self._get_information(self.urls[-1])
                if info["comments"]:
                    self.ircbot.privmsg(
                        params[0],
                        random.choice(info["comments"])[:255].encode(
                            "ascii", "ignore"
                        )
                    )


    def _get_information(self, url):
        """
        get information about youtube url
        """
        try:
            #load url and parse it with html parser
            #hack via urllib2 to set timeout
            html = urllib2.urlopen(url, timeout=60)
            root =  lxml.html.fromstring(html.read())

            #get relevant part
            comments = root.xpath(
                "//div[@class='comment-text']/p/text()"
            )

        except IOError, e:
            print "====>", e
            comments = None

        return {
            "comments" : comments
        }

