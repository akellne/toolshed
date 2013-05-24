#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asynchat
import asyncore
import socket
import logging
import time

#
# check: https://tools.ietf.org/html/rfc1459
#

#setup logger
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("ircb")

#delay that is used between messages to avoid flooding
MESSAGE_DELAY = 1.0

#numeric message code constants
RPL_WELCOME           = "001"
RPL_YOURHOST          = "002"
RPL_CREATED           = "003"
RPL_MYINFO            = "004"
RPL_BOUNCE            = "005"
RPL_USERHOST          = "302"
RPL_ISON              = "303"
RPL_AWAY              = "301"
RPL_UNAWAY            = "305"
RPL_NOWAWAY           = "306"
RPL_WHOISUSER         = "311"
RPL_WHOISSERVER       = "312"
RPL_WHOISOPERATOR     = "313"
RPL_WHOISIDLE         = "317"
RPL_ENDOFWHOIS        = "318"
RPL_WHOISCHANNELS     = "319"
RPL_WHOWASUSER        = "314"
RPL_ENDOFWHOWAS       = "369"
RPL_LISTSTART         = "321"
RPL_LIST              = "322"
RPL_LISTEND           = "323"
RPL_UNIQOPIS          = "325"
RPL_CHANNELMODEIS     = "324"
RPL_NOTOPIC           = "331"
RPL_TOPIC             = "332"
RPL_INVITING          = "341"
RPL_SUMMONING         = "342"
RPL_INVITELIST        = "346"
RPL_ENDOFINVITELIST   = "347"
RPL_EXCEPTLIST        = "348"
RPL_ENDOFEXCEPTLIST   = "349"
RPL_VERSION           = "351"
RPL_WHOREPLY          = "352"
RPL_ENDOFWHO          = "315"
RPL_NAMREPLY          = "353"
RPL_ENDOFNAMES        = "366"
RPL_LINKS             = "364"
RPL_ENDOFLINKS        = "365"
RPL_BANLIST           = "367"
RPL_ENDOFBANLIST      = "368"
RPL_INFO              = "371"
RPL_ENDOFINFO         = "374"
RPL_MOTDSTART         = "375"
RPL_MOTD              = "372"
RPL_ENDOFMOTD         = "376"
RPL_YOUREOPER         = "381"
RPL_REHASHING         = "382"
RPL_YOURESERVICE      = "383"
RPL_TIME              = "391"
RPL_USERSSTART        = "392"
RPL_USERS             = "393"
RPL_ENDOFUSERS        = "394"
RPL_NOUSERS           = "395"
RPL_TRACELINK         = "200"
RPL_TRACECONNECTING   = "201"
RPL_TRACEHANDSHAKE    = "202"
RPL_TRACEUNKNOWN      = "203"
RPL_TRACEOPERATOR     = "204"
RPL_TRACEUSER         = "205"
RPL_TRACESERVER       = "206"
RPL_TRACESERVICE      = "207"
RPL_TRACENEWTYPE      = "208"
RPL_TRACECLASS        = "209"
RPL_TRACERECONNECT    = "210"
RPL_TRACELOG          = "261"
RPL_TRACEEND          = "262"
RPL_STATSLINKINFO     = "211"
RPL_STATSCOMMANDS     = "212"
RPL_ENDOFSTATS        = "219"
RPL_STATSUPTIME       = "242"
RPL_STATSOLINE        = "243"
RPL_UMODEIS           = "221"
RPL_SERVLIST          = "234"
RPL_SERVLISTEND       = "235"
RPL_LUSERCLIENT       = "251"
RPL_LUSEROP           = "252"
RPL_LUSERUNKNOWN      = "253"
RPL_LUSERCHANNELS     = "254"
RPL_LUSERME           = "255"
RPL_ADMINME           = "256"
RPL_ADMINLOC1         = "257"
RPL_ADMINLOC2         = "258"
RPL_ADMINEMAIL        = "259"
RPL_TRYAGAIN          = "263"
ERR_NOSUCHNICK        = "401"
ERR_NOSUCHSERVER      = "402"
ERR_NOSUCHCHANNEL     = "403"
ERR_CANNOTSENDTOCHAN  = "404"
ERR_TOOMANYCHANNELS   = "405"
ERR_WASNOSUCHNICK     = "406"
ERR_TOOMANYTARGETS    = "407"
ERR_NOSUCHSERVICE     = "408"
ERR_NOORIGIN          = "409"
ERR_NORECIPIENT       = "411"
ERR_NOTEXTTOSEND      = "412"
ERR_NOTOPLEVEL        = "413"
ERR_WILDTOPLEVEL      = "414"
ERR_BADMASK           = "415"
ERR_UNKNOWNCOMMAND    = "421"
ERR_NOMOTD            = "422"
ERR_NOADMININFO       = "423"
ERR_FILEERROR         = "424"
ERR_NONICKNAMEGIVEN   = "431"
ERR_ERRONEUSNICKNAME  = "432"
ERR_NICKNAMEINUSE     = "433"
ERR_NICKCOLLISION     = "436"
ERR_UNAVAILRESOURCE   = "437"
ERR_USERNOTINCHANNEL  = "441"
ERR_NOTONCHANNEL      = "442"
ERR_USERONCHANNEL     = "443"
ERR_NOLOGIN           = "444"
ERR_SUMMONDISABLED    = "445"
ERR_USERSDISABLED     = "446"
ERR_NOTREGISTERED     = "451"
ERR_NEEDMOREPARAMS    = "461"
ERR_ALREADYREGISTRED  = "462"
ERR_NOPERMFORHOST     = "463"
ERR_PASSWDMISMATCH    = "464"
ERR_YOUREBANNEDCREEP  = "465"
ERR_YOUWILLBEBANNED   = "466"
ERR_KEYSET            = "467"
ERR_CHANNELISFULL     = "471"
ERR_UNKNOWNMODE       = "472"
ERR_INVITEONLYCHAN    = "473"
ERR_BANNEDFROMCHAN    = "474"
ERR_BADCHANNELKEY     = "475"
ERR_BADCHANMASK       = "476"
ERR_NOCHANMODES       = "477"
ERR_BANLISTFULL       = "478"
ERR_NOPRIVILEGES      = "481"
ERR_CHANOPRIVSNEEDED  = "482"
ERR_CANTKILLSERVER    = "483"
ERR_RESTRICTED        = "484"
ERR_UNIQOPPRIVSNEEDED = "485"
ERR_NOOPERHOST        = "491"
ERR_UMODEUNKNOWNFLAG  = "501"
ERR_USERSDONTMATCH    = "502"



code_explanations = {
    RPL_WELCOME         : "Welcome to the Internet Relay Network " \
                          "<nick>!<user>@<host>",
    RPL_YOURHOST        : "Your host is <servername>, running version <ver>",
    RPL_CREATED         : "This server was created <date>",
    RPL_MYINFO          : "<servername> <version> <available user modes> " \
                          "<available channel modes>",
    RPL_BOUNCE          : "Try server <server name>, port <port number>",
    RPL_USERHOST        : ":*1<reply> *( " " <reply> )",
    RPL_ISON            : ":*1<nick> *( " " <nick> )",
    RPL_AWAY            : "<nick> :<away message>",
    RPL_UNAWAY          : ":You are no longer marked as being away",
    RPL_NOWAWAY         : ":You have been marked as being away",
    RPL_WHOISUSER       : "<nick> <user> <host> * :<real name>",
    RPL_WHOISSERVER     : "<nick> <server> :<server info>",
    RPL_WHOISOPERATOR   : "<nick> :is an IRC operator",
    RPL_WHOISIDLE       : "<nick> <integer> :seconds idle",
    RPL_ENDOFWHOIS      : "<nick> :End of WHOIS list",
    RPL_WHOISCHANNELS   : '<nick> :*( ( "@" / "+" ) <channel> " " )',
    RPL_WHOWASUSER      : "<nick> <user> <host> * :<real name>",
    RPL_ENDOFWHOWAS     : "<nick> :End of WHOWAS",
    RPL_LIST            : "<channel> <# visible> :<topic>",
    RPL_LISTEND         : ":End of LIST",
    RPL_UNIQOPIS        : "<channel> <nickname>",
    RPL_CHANNELMODEIS   : "<channel> <mode> <mode params>",
    RPL_NOTOPIC         : "<channel> :No topic is set",
    RPL_TOPIC           : "<channel> :<topic>",
    RPL_INVITING        : "<channel> <nick>",
    RPL_SUMMONING       : "<user> :Summoning user to IRC",
    RPL_INVITELIST      : "<channel> <invitemask>",
    RPL_ENDOFINVITELIST : "<channel> :End of channel invite list",
    RPL_EXCEPTLIST      : "<channel> <exceptionmask>",
    RPL_ENDOFEXCEPTLIST : "<channel> :End of channel exception list",
    RPL_VERSION         : "<version>.<debuglevel> <server> :<comments>",
    RPL_WHOREPLY        : '<channel> <user> <host> <server> <nick>' \
                          '( "H" / "G" > ["*"] [ ( "@" / "+" ) ]' \
                          ':<hopcount> <real name>',
    RPL_ENDOFWHO        : "<name> :End of WHO list",
    RPL_NAMREPLY        : '( "=" / "*" / "@" ) <channel>' \
                          ':[ "@" / "+" ] <nick> *( " " [ "@" / "+" ] <nick> )',
    RPL_ENDOFNAMES      : "<channel> :End of NAMES list",
    RPL_LINKS           : "<mask> <server> :<hopcount> <server info>",
    RPL_ENDOFLINKS      : "<mask> :End of LINKS list",
    RPL_BANLIST         : "<channel> <banmask>",
    RPL_ENDOFBANLIST    : "<channel> :End of channel ban list",
    RPL_INFO            : ":<string>",
    RPL_ENDOFINFO       : ":End of INFO list",
    RPL_MOTDSTART       : ":- <server> Message of the day - ",
    RPL_MOTD            : ":- <text>",
    RPL_ENDOFMOTD       : ":End of MOTD command",
    RPL_YOUREOPER       : ":You are now an IRC operator",
    RPL_REHASHING       : "<config file> :Rehashing",
    RPL_YOURESERVICE    : "You are service <servicename>",
    RPL_TIME            : "<server> :<string showing server's local time>",
    RPL_USERSSTART      : ":UserID   Terminal  Host",
    RPL_USERS           : ":<username<> <ttyline> <hostname>",
    RPL_ENDOFUSERS      : ":End of users",
    RPL_NOUSERS         : ":Nobody logged in",
    RPL_TRACELINK       : "Link <version & debug level> <destination>" \
                          "<next server> V<protocol version>" \
                          "<link uptime in seconds> <backstream sendq>" \
                          "<upstream sendq>",
    RPL_TRACECONNECTING : "Try. <class> <server>",
    RPL_TRACEHANDSHAKE  : "H.S. <class> <server>",
    RPL_TRACEUNKNOWN    : "???? <class> [<client IP address in dot form>]",
    RPL_TRACEOPERATOR   : "Oper <class> <nick>",
    RPL_TRACEUSER       : "User <class> <nick>",
    RPL_TRACESERVER     : "Serv <class> <int>S <int>C <server>" \
                          "<nick!user|*!*>@<host|server> V<protocol version>",
    RPL_TRACESERVICE    : "Service <class> <name> <type> <active type>",
    RPL_TRACENEWTYPE    : "<newtype> 0 <client name>",
    RPL_TRACECLASS      : "Class <class> <count>",
    RPL_TRACELOG        : "File <logfile> <debug level>",
    RPL_TRACEEND        : "<server name> <version & debug level> :End of TRACE",
    RPL_STATSLINKINFO   : "<linkname> <sendq> <sent messages>" \
                          "<sent Kbytes> <received messages>" \
                          "<received Kbytes> <time open>",
    RPL_STATSCOMMANDS   : "<command> <count> <byte count> <remote count>",
    RPL_ENDOFSTATS      : "<stats letter> :End of STATS report",
    RPL_STATSUPTIME     : ":Server Up %d days %d:%02d:%02d",
    RPL_STATSOLINE      : "O <hostmask> * <name>",
    RPL_UMODEIS         : "<user mode string>",
    RPL_SERVLIST        : "<name> <server> <mask> <type> <hopcount> <info>",
    RPL_SERVLISTEND     : "<mask> <type> :End of service listing",
    RPL_LUSERCLIENT     : ":There are <integer> users and <integer>" \
                          "services on <integer> servers",
    RPL_LUSEROP         : "<integer> :operator(s) online",
    RPL_LUSERUNKNOWN    : "<integer> :unknown connection(s)",
    RPL_LUSERCHANNELS   : "<integer> :channels formed",
    RPL_LUSERME         : ":I have <integer> clients and <integer> servers",
    RPL_ADMINME         : "<server> :Administrative info",
    RPL_ADMINLOC1       : ":<admin info>",
    RPL_ADMINLOC2       : ":<admin info>",
    RPL_ADMINEMAIL      : ":<admin info>",
    RPL_TRYAGAIN        : "<command> :Please wait a while and try again.",
    ERR_NOSUCHNICK      : "<nickname> :No such nick/channel",
    ERR_NOSUCHSERVER    : "<server name> :No such server",
    ERR_NOSUCHCHANNEL   : "<channel name> :No such channel",
    ERR_CANNOTSENDTOCHAN: "<channel name> :Cannot send to channel",
    ERR_TOOMANYCHANNELS : "<channel name> :You have joined too many channels",
    ERR_WASNOSUCHNICK   : "<nickname> :There was no such nickname",
    ERR_TOOMANYTARGETS  : "<target> :<error code> recipients. <abort message>",
    ERR_NOSUCHSERVICE   : "<service name> :No such service",
    ERR_NOORIGIN        : ":No origin specified",
    ERR_NORECIPIENT     : ":No recipient given (<command>)",
    ERR_NOTEXTTOSEND    : ":No text to send",
    ERR_NOTOPLEVEL      : "<mask> :No toplevel domain specified",
    ERR_WILDTOPLEVEL    : "<mask> :Wildcard in toplevel domain",
    ERR_BADMASK         : "<mask> :Bad Server/host mask",
    ERR_UNKNOWNCOMMAND  : "<command> :Unknown command",
    ERR_NOMOTD          : ":MOTD File is missing",
    ERR_NOADMININFO     : "<server> :No administrative info available",
    ERR_FILEERROR       : ":File error doing <file op> on <file>",
    ERR_NONICKNAMEGIVEN : ":No nickname given",
    ERR_ERRONEUSNICKNAME: "<nick> :Erroneous nickname",
    ERR_NICKNAMEINUSE   : "<nick> :Nickname is already in use",
    ERR_NICKCOLLISION   : "<nick> :Nickname collision KILL from <user>@<host>",
    ERR_UNAVAILRESOURCE : "<nick/channel> :Nick/channel is temporarily unavailable",
    ERR_USERNOTINCHANNEL: "<nick> <channel> :They aren't on that channel",
    ERR_NOTONCHANNEL    : "<channel> :You're not on that channel",
    ERR_USERONCHANNEL   : "<user> <channel> :is already on channel",
    ERR_NOLOGIN         : "<user> :User not logged in",
    ERR_SUMMONDISABLED  : ":SUMMON has been disabled",
    ERR_USERSDISABLED   : ":USERS has been disabled",
    ERR_NOTREGISTERED   : ":You have not registered",
    ERR_NEEDMOREPARAMS  : "<command> :Not enough parameters",
    ERR_ALREADYREGISTRED: ":Unauthorized command (already registered)",
    ERR_NOPERMFORHOST   : ":Your host isn't among the privileged",
    ERR_PASSWDMISMATCH  : ":Password incorrect",
    ERR_YOUREBANNEDCREEP: ":You are banned from this server",
    ERR_YOUWILLBEBANNED : ":You will be banned from this server",
    ERR_KEYSET          : "<channel> :Channel key already set",
    ERR_CHANNELISFULL   : "<channel> :Cannot join channel (+l)",
    ERR_UNKNOWNMODE     : "<char> :is unknown mode char to me for <channel>",
    ERR_INVITEONLYCHAN  : "<channel> :Cannot join channel (+i)",
    ERR_BANNEDFROMCHAN  : "<channel> :Cannot join channel (+b)",
    ERR_BADCHANNELKEY   : "<channel> :Cannot join channel (+k)",
    ERR_BADCHANMASK     : "<channel> :Bad Channel Mask",
    ERR_NOCHANMODES     : "<channel> :Channel doesn't support modes",
    ERR_BANLISTFULL     : "<channel> <char> :Channel list is full",
    ERR_NOPRIVILEGES    : ":Permission Denied- You're not an IRC operator",
    ERR_CHANOPRIVSNEEDED: "<channel> :You're not channel operator",
    ERR_CANTKILLSERVER  : ":You can't kill a server!",
    ERR_RESTRICTED      : ":Your connection is restricted!",
    ERR_UNIQOPPRIVSNEEDED:":You're not the original channel operator",
    ERR_NOOPERHOST      : ":No O-lines for your host",
    ERR_UMODEUNKNOWNFLAG: ":Unknown MODE flag",
    ERR_USERSDONTMATCH  : ":Cannot change mode for other users",
}


class IRCClient(asynchat.async_chat):
    """
    IRC client class
    """
    def __init__(self, server, port):
        self.received_data = []

        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((server, port))

        self.set_terminator("\r\n")


    def collect_incoming_data(self, data):
        #append incoming data to buffer
        self.received_data.append(data)


    def found_terminator(self):
        msg = ''.join(self.received_data)

        #get prefix
        if msg.startswith(":"):
            prefix,_, msg = msg.partition(" ")
        else:
            prefix = None

        #get tail (the message)
        msg, _, tail = msg.partition(" :")

        #get command and parameters
        params = msg.split(" ")
        cmd = params.pop(0)

        #handle the message
        self.handle_message(prefix, tail, cmd, *params)

        #reset buffer for incoming data
        self.received_data = []


    def handle_message(self, prefix, tail, cmd, *args):
        """
        handle incoming irc messages
        => override this to add reaction to messages
        """
        log.debug(
            "<<< prefix: %s  tail: %s  cmd: %s  params: %s" % (
                prefix, tail, cmd, ", ".join(args)
            )
        )

        if cmd == "PING":
            #answer ping with pong
            self.pong(tail)


    def send_data(self, data):
        log.debug(">>> %s" % data)
        self.push("%s%s" % (data, self.get_terminator()))

    def passw(self, password):
        self.send_data("PASS %s" % password)

    def nick(self, nickname):
        self.send_data("NICK %s" % nickname)

    def user(self, username, hostname, servername, realname):
        self.send_data("USER %s %s %s %s" % (username, hostname, servername, realname))

    def quit(self, message=""):
        self.send_data("QUIT %s" % message)

    def join(self, channel):
        self.send_data("JOIN %s" % channel)

    def part(self, channel):
        self.send_data("PART %s" % channel)


    def part(self, channel, topic):
        self.send_data("PART %s :%s" % (channel, topic))

    def names(self, channel):
        self.send_data("NAMES %s" % channel)

    def list(self, channel=""):
        self.send_data("LIST %s" % channel)

    def privmsg(self, receiver, message):
        for msg in message.split("\n"):
            self.send_data("PRIVMSG %s :%s" % (receiver, msg))
            time.sleep(MESSAGE_DELAY)


    def who(self, name):
        self.send_data("WHO %s" % name)

    def whois(self, server, nickmask):
        self.send_data("WHOIS %s %s" % (server, nickmask))

    def pong(self, daemon=""):
        self.send_data("PONG %s" % daemon)

    def away(self, message=""):
        self.send_data("AWAY %s" % message)

