#
# Imports
#
import os
import sys
import urllib
import HTMLParser

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
from BeautifulSoup import SoupStrainer
from BeautifulSoup import BeautifulSoup
from HTTPCommunicator import HTTPCommunicator



#
# Constants
# 
__settings__ = xbmcaddon.Addon()
__language__ = __settings__.getLocalizedString
rootDir = __settings__.getAddonInfo('path')
if rootDir[-1] == ';':
    rootDir = rootDir[0:-1]
rootDir = xbmc.translatePath(rootDir)


#
# Main class
#
class Main:
    #
    # Init
    #
    def __init__(self):
        # Constants
        self.DEBUG = False
        self.IMAGES_PATH = xbmc.translatePath(os.path.join(rootDir, 'resources', 'images'))

        # Parse parameters...
        params = dict(part.split('=') for part in sys.argv[2][1:].split('&'))
        self.show_url = urllib.unquote_plus(params.get("event-url"))
        self.current_page = int(params.get("page", "1"))

        print "event-url: %s" % self.show_url

        #
        # Get the videos...
        #
        self.get_videos()

    #
    # Get videos...
    #
    def get_videos(self):
        #
        # Init
        #
        sysaddon = sys.argv[0]
        #
        # Get HTML page...
        #
        httpCommunicator = HTTPCommunicator()
        url = "http://channel9.msdn.com/%s?page=%u&lang=en" % (self.show_url, self.current_page)
        htmlData = httpCommunicator.get(url)
        htmlParser = HTMLParser.HTMLParser()
        #        
        # Parse response...
        #
        soupStrainer = SoupStrainer("div", {"class": "tab-content"})
        beautifulSoup = BeautifulSoup(htmlData, soupStrainer, convertEntities=BeautifulSoup.HTML_ENTITIES)

        #
        # Parse movie entries...
        #
        ul_entries = beautifulSoup.find("ul", {"class": "entries sessions sessionList"})
        li_entries = ul_entries.findAll("li")
        for li_entry in li_entries:
            # Thumbnail...
            div_entry_image = li_entry.find("div", {"class": "entry-image"})
            # if there isn't a thumb, we don't want this node.
            if div_entry_image is None:
                continue

            thumbnail = div_entry_image.find("img", {"class": "thumb"})["src"]

            # Title
            div_entry_meta = li_entry.find("div", {"class": "entry-meta"})
            a_title = div_entry_meta.find("a", {"class": "title"})
            title = htmlParser.unescape(a_title.string)

            # Video page
            video_page_url = a_title["href"]

            # Genre (date)...
            # if there isnt a "data" then we dont have a date/genre
            div_data = div_entry_meta.find("div", {"class": "data"})
            if div_data is None:
                genre = "none"
            else:
                span_class_date = div_data.find("span", {"class": "date"})
                genre = span_class_date.string

            # Plot
            div_description = div_entry_meta.find("div", {"class": "description"})
            plot = div_description.string

            # Add to list...
            # cm = []
            # cm.append(xbmcplugin.lang(30239).encode('utf-8'), 'RunPlugin(%s?action=tvshowToLibrary&tvshowtitle=%s)' % (sysaddon, title))

            listitem = xbmcgui.ListItem(title, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
            listitem.setInfo("video", {"Title": title, "Studio": "Microsoft Channel 9", "Plot": plot, "Genre": genre})
            plugin_play_url = '%s?action=play&video_page_url=%s' % (sys.argv[0], urllib.quote_plus(video_page_url))
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=plugin_play_url, listitem=listitem, isFolder=False)

        # Next page entry...
        ul_paging = beautifulSoup.find("ul", {"class": "paging"})
        if ul_paging:
            listitem = xbmcgui.ListItem(__language__(30503), iconImage="DefaultFolder.png",
                                        thumbnailImage=os.path.join(self.IMAGES_PATH, 'next-page.png'))
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url="%s?action=list-event&event-url=%s&page=%i" % (
                sys.argv[0], urllib.quote_plus(self.show_url), self.current_page + 1), listitem=listitem, isFolder=True)

        # Disable sorting...
        xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_NONE)

        # End of directory...
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
