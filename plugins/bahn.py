#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import datetime
import lxml.html
import json

from base import Plugin


#URL to the mobile webpage of bahn.de
URL = "http://mobile.bahn.de/bin/mobil/query.exe/dox?country=DEU&rt=1&use_realtime_filter=1&searchMode=NORMAL&sotRequest=1"


class Bahn(Plugin):
    """
    class to parse the train connections from bahn mobile
    """
    NAME    = "Bahn"
    AUTHOR  = "kellner@cs.uni-goettingen.de"
    VERSION = (0, 0, 1)
    ENABLED = True
    HELP    = "!bahn+berlin    display next trains to Berlin\n" \
              "!bahn+hannover  display next trains to Hannover"


    def __init__(
        self, ircbot, cache_time=None,
        random_message=[None, None]
    ):
        Plugin.__init__(self, ircbot, cache_time, random_message)


    def on_privmsg(self, msg, *params):
        Plugin.on_privmsg(self, msg, *params)

        if msg.startswith("!bahn"):
            self.ircbot.switch_personality(nick="diebahn")
            if msg == "!bahn+berlin":
                message = self._get_bahn(to_="Berlin")
            elif msg == "!bahn+hannover":
                message = self._get_bahn(to_="Hannover")
            else:
                message = "unknown destination"

            #finally, send the message with the
            self.ircbot.privmsg(params[0], message)

            self.ircbot.reset_personality()


    def _get_bahn(self, to_, from_="Goettingen"):
        """
        get trains from bahn webpage
        """
        try:
            #load url, parse it with html parser and get form
            form = lxml.html.parse(URL).getroot().forms[0]

            #set from and to parameter of the form
            form.fields["REQ0JourneyStopsS0G"] = from_
            form.fields["REQ0JourneyStopsZ0G"] = to_

            #submit the form and get train connections
            root = lxml.html.parse(
                lxml.html.submit_form(form, extra_values={'start': "Suchen"})
            )

            #parse results from returned table
            items = []
            for tr in root.xpath("//table/tr"):
                if tr.find("td[@class='overview timelink']") is not None:
                    ab, an       = tr.xpath("td[@class='overview timelink']/a/text()")
                    vab, van     = tr.xpath("td[@class='overview tprt']//text()")
                    umstg, dauer = tr.xpath("td[@class='overview']//text()")
                    zuege        = tr.xpath("td[@class='overview iphonepfeil']//text()")
                    it = {
                        "ab"             : ab,
                        "an"             : an,
                        "verspaetung_ab" : vab,
                        "verspaetung_an" : van,
                        "umstiege"       : umstg,
                        "dauer"          : dauer,
                        "zuege"          : zuege
                    }
                    items.append(it)

            #prepare message from given connections
            tmp = u"--- Nächste Zugverbindungen: %s - %s ---\n" % (from_, to_)
            for item in items:
                tmp += "ab %s (%s min) an %s (%s min), %sx umsteigen, " \
                       "%s, %s\n" % (
                    item["ab"], item["verspaetung_ab"],
                    item["an"], item["verspaetung_an"],
                    item["umstiege"], item["dauer"],
                    ", ".join(item["zuege"])
                )

        except:
            tmp = "Keine Ahnung. Mein Parser ist kaputt"

            return tmp.strip().encode("utf-8")


