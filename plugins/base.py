import os
import json
import logging
import datetime
import codecs
import random
import threading


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

    ircbot          is the ircbot that can be used by the plugin for the
                    communication with the irc network
    cache_time      should be a datetime.timedelta that specifies from which
                    point in time the cache of the plugin is marked for
                    reloading
    random_message  is an interval in which random messages should be sent
                    the interval unit is seconds so the values must be given
                    as floats.
    """
    NAME     = ""
    AUTHOR   = ""
    VERSION  = (0, 0, 0)
    ENABLED  = False
    HELP     = ""
    CHANNELS = []  #empty list means, active for all channels

    def __init__(
        self, ircbot, cache_time=None, random_message=[None, None]
    ):
        #setup plugin logger
        self.log = logging.getLogger(
            "plugin '%s (%s)':" % (self.NAME, self.get_version())
        )

        self.log.debug("Init with cache_time '%s'" % cache_time)
        self.log.debug(
            "Plugin is activated for channels: %s" % (
                ", ".join(self.CHANNELS)
            )
        )

        #ircbot that is used for information exchange
        self.ircbot = ircbot

        #build cache file name based on plugin name
        self.cache_file     = os.path.join(
            CACHE_DIR, "%s.dat" % self.NAME.lower().replace(" ", "_")
        )

        #if set to None, no caching => otherwise use datetime.timedelta
        self.cache_time = cache_time

        #interval in which random messages should be sent
        self.random_message = random_message

        #random message timer (later used as pointer to the threading.Timer)
        self.timer = None


    def on_init(self):
        """
        called on initialization of the plugin
        """
        self.log.debug("Initializing plugin")


    def on_msg(self, cmd, sender, msg, *params):
        """
        called on arrival of any message
        """

        if cmd == "PRIVMSG":
            self.on_privmsg_ex(sender, msg, *params);


    def on_privmsg_ex(self, sender, msg, *params):
        in_channel = params[0].startswith('#')
        args = tuple(
            [params[0] if in_channel else sender] +list(params[1:])
        );
        self.on_privmsg(msg, *args)


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

        if self.timer:
            #cancel timer and destroy on random message calls
            #to avoid another execution of the timer
            self.log.debug("Canceling random message timer")
            self.timer.cancel()
            self.on_random_message = lambda self: None


    def on_random_message(self):
        """
        called on triggering of a random message
        """
        self.log.debug("random message triggered")


    def start_random_message_timer(self):
        """
        start the random message timer, random choice from
        the given interval
        """
        a, b = self.random_message

        if (not a and not b) or (not a):
            #ignore invalid interval
            return

        if a and not b:
            #set choice to given value
            c = a
        else:
            #choose random time from given interval
            c = random.uniform(a, b)

        if self.timer:
            #cancel current timer, before starting a new timer
            self.log.debug("Canceling running random message timer")
            self.timer.cancel()

        self.log.debug(
            "Starting random timer in %s ms (chosen from interval [%s, %s])" % (
                c, a, b
            )
        )

        #start the timer
        self.timer = threading.Timer(c, self.on_random_message)
        self.timer.start()


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


    def is_in_channel(self, channel):
        """
        returns True, if plugin is in channel
        """
        return (
            (channel in self.CHANNELS) or (self.CHANNELS == [])
        )


    def __str__(self):
        return "%s, %s %s" % (self.NAME, self.AUTHOR, self.get_version())


