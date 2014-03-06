ReadMe
======
This is a small python based irc bot that just handles some very basic irc commands. However, it can be extended by plugins stored in the plugins/ directory. Each plugin must be derived from the Plugin class that provides some basic plugin functionality.


notes
-----
    * this program is at an early stage of development so use it at your 
      own risk!
    * for security reasons the bot plugins should not allow arbitrary user
      input, i.e. only direct mapping of pre-defined parameter to results
      should be used
    * the default configuration is read from ~/.toolshedrc, which is used
      in case of no arguments given on start


