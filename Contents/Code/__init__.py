# -*- coding: utf-8 -*

import json
import urllib
import urllib2
import re
import datetime

# Global constants
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
VERSION = "1"
PREFIX = "/video/eurosportplayer"

# URLs
CRM_URL = "https://playercrm.ssl.eurosport.com/JsonPlayerCrmApi.svc/"
CRM_LOGIN = CRM_URL + "Login"
CMR_UNLINK = CRM_URL + "Unlink"
IMAGE_HOST_URL = "http://i.eurosportplayer.se/"

VIDEO_URL = "http://videoshop.ext.eurosport.com/JsonProductService.svc/"
VIDEO_PRODUCTS = VIDEO_URL + "GetAllProductsByDeviceMobile"

#Texts
TEXT_TITLE = u"Eurosport Player"
TEXT_CHANNELS = u"Channels"

date_regex = re.compile("Date\(([0-9]*?)\+([0-9]*?)\)")

user_ref = None
login_data = {"email":"", "password":"", "udid":"8932743294"}
context = {"v":"1",
        "s":"1",
        "d":4,
        "b":"Plex",
        "ma":"MrsnugglyBottom",
        "p":"1",
        "mn":"Snugglyman",
        "mi":VERSION,
        "osn":"Android",
        "osv":"4.3",
        "ap":18,
        "tt":"pad",
        "di":"dimension:=1920x1128,density=300.00x300.00,scale=1.00x1.00",
        "l:":"7",
        "g":"SE"
        }

ep_login = SharedCodeService.eurosportplayer.ep_login

# Initializer called by the framework
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def Start():
    pass

# Menu builder methods
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@handler(PREFIX, TEXT_TITLE)
def MainMenu():

    menu = ObjectContainer(title1=TEXT_TITLE)
    menu.add((DirectoryObject(key=Callback(ListChannels, prevTitle = TEXT_TITLE), title=TEXT_CHANNELS)))
    menu.add(PrefsObject(title="Preferences"))

    Log("Version: %s" % VERSION)

    return menu

def ListChannels(prevTitle):
    if not user_ref:
        do_login2()

    o = ObjectContainer(title1=prevTitle, title2=TEXT_CHANNELS)
    dvs = {"userid": user_ref["Id"],
            "hkey": user_ref["Hkey"],
            "languageid": 7,
            "isbroadcasted" : 1,
            "isfullaccess" : 0
            }
    encoded = urllib.urlencode({"data": json.dumps(dvs), "context" : json.dumps(context)})
    channelsUrl = VIDEO_PRODUCTS + "?" + encoded
    products = JSON.ObjectFromURL(channelsUrl)

    for c in products["PlayerObj"]:
        current_show = find_current_show(c)
        if current_show:
            summary = current_show["name"]
        else:
            summary = c["channellivelabel"] + ": " + c["channellivesublabel"],

        eo = EpisodeObject(
                title = c["channellabel"],
                summary = summary,
                thumb = IMAGE_HOST_URL + c["vignetteurl"],
                url = get_livestream_url(c)
                )
        o.add(eo)

    return o

def get_livestream_url(channel):
    return channel["livestreams"][0]["url"]

def find_current_show(channel):
    now = datetime.datetime.now()

    if channel["tvschedules"]:
        for s in channel["tvschedules"]:
            endtime = convert_date(s["enddate"]["datetime"])
            starttime = convert_date(s["startdate"]["datetime"])
            if now < endtime and now >= starttime:
                return s
    elif channel["tvscheduleliveevents"]:
        for s in channel["tvscheduleliveevents"]:
            endtime = convert_date(s["enddate"]["datetime"])
            starttime = convert_date(s["startdate"]["datetime"])
            if now < endtime and now >= starttime:
                return s
    return None

def do_login2():
    global user_ref
    user_ref = ep_login()

def convert_date(dateString):
    r = date_regex.search(dateString)
    (time, offset) = r.groups()
    time = int(time)
    time = time / 1000
    return datetime.datetime.fromtimestamp(time)
