# -*- coding: utf-8 -*

import json
import urllib
import urllib2

import string

# Global constants
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
VERSION = "1"
PREFIX = "/video/eurosportplayer"

# URLs
CRM_URL = "https://playercrm.ssl.eurosport.com/JsonPlayerCrmApi.svc/"
CRM_LOGIN = CRM_URL + "Login"
CMR_UNLINK = CRM_URL + "Unlink"
IMAGE_HOST_URL = "http://i.eurosportplayer.se/"

#Texts
TEXT_TITLE = u"Eurosport Player"
TEXT_CHANNELS = u"Channels"

get_products = SharedCodeService.eurosportplayer.get_products
find_current_show = SharedCodeService.eurosportplayer.find_current_show

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
    o = ObjectContainer(title1=prevTitle, title2=TEXT_CHANNELS)

    products = get_products()

    for c in products["PlayerObj"]:
        current_show = find_current_show(c)
        if current_show:
            summary = current_show["name"]
        else:
            summary = c["channellivelabel"] + ": " + c["channellivesublabel"],

        url = get_livestream_url(c)
        eo = EpisodeObject(
                title = c["channellabel"],
                summary = summary,
                thumb = IMAGE_HOST_URL + c["vignetteurl"],
                url = url
                )
        o.add(eo)
        Log(url)

    return o

def get_livestream_url(channel):
    return channel["livestreams"][0]["url"]

