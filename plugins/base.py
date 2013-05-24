import os
import sys
import json
import logging
import datetime
import codecs


#setup logger for plugins
logging.basicConfig(level=logging.DEBUG)

CACHE_DIR = "./cache"
if not os.path.exists(CACHE_DIR):
    #create chache dir if it is not existing yet
    logging.debug("Creating cache dir '%s'" % CACHE_DIR)
    os.mkdir(CACHE_DIR)


class Plugin(object):
    """
    parent class for all plugins
    """
    NAME    = ""
    AUTHOR  = ""
    VERSION = (0, 0, 0)
    ENABLED = False

    def __init__(self, ircbot, cache_time=None):
        #setup plugin logger
        self.log = logging.getLogger(
            "plugin '%s (%s)':" % (self.NAME, self.get_version())
        )

        self.log.debug("Init with cache_time '%s'" % cache_time)

        #ircbot that is used for information exchange
        self.ircbot = ircbot

        #build cache file name based on plugin name
        self.cache_file     = os.path.join(
            CACHE_DIR, "%s.dat" % self.NAME.lower().replace(" ", "_")
        )

        #if set to None, no caching => otherwise use datetime.timedelta
        self.cache_time = cache_time


    def on_init(self):
        """
        called on initialisation of the plugin
        """
        self.log.debug("Initializing plugin")


    def on_privmsg(self, msg, *params):
        """
        called on arrival of a privmsg
        """
        if len(params) > 1:
            params = ", ".join(*params)
        self.log.debug(
            "privmsg '%s' %s" % (
                msg, params
            )
        )


    def on_quit(self):
        """
        called on quitting of the plugin
        """
        self.log.debug("Quitting plugin")


    def get_version(self):
        """
        returns the version of the plugin
        """
        return "V%d.%d.%d" % (
            self.VERSION[0], self.VERSION[1], self.VERSION[2]
        )


    def load_cache(self):
        """
        load cached data of the plugin
        => returns True and None for data, if new data
           for the plugin should be loaded instead of
           the outdated data from the cache
        """
        reload_data = True
        data        = None

        if self.cache_time and os.path.exists(self.cache_file):
            #cache time is set and cache file does exist
            try:
                #get last modification time
                mtime = datetime.datetime.fromtimestamp(
                    os.path.getmtime(self.cache_file)
                )

                if (datetime.datetime.now() - mtime) < self.cache_time:
                    #cache time is not expired => load cached data
                    self.log.debug("Loading data from cache")
                    reload_data = False
                    with codecs.open(self.cache_file, "r", "utf-8") as f:
                        data = json.load(f)
                else:
                    self.log.debug(
                        "Data in cache is too old => recommend to " \
                        "reload the data."
                    )

            except ValueError:
                self.log.exception("Error laoding data from cache")
        else:
            self.log.debug(
                "cachetime: '%s' is None or file '%s' does not " \
                "exist" % (self.cache_time, self.cache_file)
            )

        return (reload_data, data)


    def save_cache(self, data):
        """
        save given data to the cache
        """
        self.log.debug("Storing data to cache: %s" % str(data))
        with codecs.open(self.cache_file, "w", "utf-8" ) as f:
            f.write(json.dumps(data))




