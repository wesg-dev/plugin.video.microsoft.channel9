# episodes: sort=episodes
# a-z: sort: atoz

import os
import sys
import urllib
import HTMLParser
import re
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
from BeautifulSoup import SoupStrainer
from BeautifulSoup import BeautifulSoup
import http_request
import control
import utils


class Main:
    def __init__(self):
        # Parse parameters...
        params = dict(part.split('=') for part in sys.argv[2][1:].split('&'))
        self.current_page = int(params.get("page", "1"))
        self.action = params.get("action", None)
        # self.sort_method = params.get("sort", control.infoLabel("Container.SortMethod"))
        self.sort_method = urllib.unquote_plus(params.get("sort", "NONE"))
        self.browse_url = "%sBrowse/Authors?direction=desc&sort=%s&page=%i&term=%s&%s"
        self.search_term = urllib.unquote_plus(params.get("query", ""))
        self.author_url = urllib.unquote_plus(params.get("author-url", ""))
        utils.set_no_sort()

        if self.action is None or self.action == "browse-authors":
            if self.sort_method == control.lang(30705):  # episodes
                self.sort = "episodes"
            elif self.sort_method == control.lang(30704):  # AtoZ
                self.sort = "atoz"
            else:
                self.show_sort()
                return
            self.browse()
            return
        elif self.action == "search-authors":
            self.sort = ""
            self.search()
            return
        elif self.action == "list-author" and self.author_url != "":
            self.list()
            return

        print "fail: action=%s&sort=%s&author-url=%s" % (self.action, self.sort_method, self.author_url)
        return

    def show_sort(self):
        # search
        utils.add_directory(control.lang(30409), utils.icon_search, None,
                            "%s?action=search-authors" % (sys.argv[0]))
        # episodes
        utils.add_directory(control.lang(30705), utils.icon_folder, None,
                            "%s?action=browse-authors&page=%i&sort=%s" % (
                                sys.argv[0], 1, urllib.quote_plus(control.lang(30705))))
        # A to Z
        utils.add_directory(control.lang(30704), utils.icon_folder, None,
                            "%s?action=browse-authors&page=%i&sort=%s" % (
                                sys.argv[0], 1, urllib.quote_plus(control.lang(30704))))
        control.directory_end()
        return

    def browse(self):
        url = self.browse_url % (
            utils.url_root, urllib.quote_plus(self.sort), self.current_page, urllib.quote_plus(self.search_term),
            utils.selected_languages())
        html_data = http_request.get(url)
        soup_strainer = SoupStrainer("main")
        beautiful_soup = BeautifulSoup(html_data, soup_strainer, convertEntities=BeautifulSoup.HTML_ENTITIES)

        ul_entries = beautiful_soup.find("ol", {"class": "authorsByLetter"})
        if ul_entries is None:
            control.directory_end()
            return

        li_entries = ul_entries.findAll("li")
        for li_entry in li_entries:
            self.add_author_directory(li_entry)

        if self.search_term == "":
            next_url = "%s?action=browse-authors&page=%i&sort=%s" % (
                sys.argv[0], self.current_page + 1, urllib.quote_plus(self.sort_method))
        else:
            next_url = "%s?action=search-authors&page=%i&query=%s" % (
                sys.argv[0], self.current_page + 1, urllib.quote_plus(self.search_term))
        print next_url
        utils.add_next_page(beautiful_soup, next_url, self.current_page + 1)

        control.directory_end()
        return

    def list(self):
        url = "%s/%s/posts?page=%u&%s" % (
            utils.url_root, self.author_url, self.current_page, utils.selected_languages())
        html_data = http_request.get(url)
        soup_strainer = SoupStrainer("main")
        beautiful_soup = BeautifulSoup(html_data, soup_strainer, convertEntities=BeautifulSoup.HTML_ENTITIES)
        articles = beautiful_soup.findAll("article")
        if articles is None:
            control.directory_end()
            return

        for article in articles:
            utils.add_entry_video(article)

        next_url = "%s?action=list-author&page=%i&author-url=%s" % (
            sys.argv[0], self.current_page + 1, urllib.quote_plus(self.author_url))
        utils.add_next_page(beautiful_soup, next_url, self.current_page + 1)

        control.directory_end()
        return

    def search(self):
        if self.search_term is None or self.search_term == '':
            t = control.lang(30201).encode('utf-8')
            k = control.keyboard('', t)
            k.doModal()
            self.search_term = k.getText() if k.isConfirmed() else None

        if self.search_term is None or self.search_term == '':
            return

        self.browse()
        return

    def add_author_directory(self, entry):
        html_parser = HTMLParser.HTMLParser()
        div_author_image = entry.find("img")
        if div_author_image is None:
            return

        author_thumb = div_author_image['src']
        if not re.match("^https?:", author_thumb):
            thumbnail = "%s%s" % (utils.url_root, author_thumb)

        author_a = entry.find("a")
        author_link = author_a['href']

        span_name = entry.find("span", {"class": "name"})
        span_displayname = entry.find("span", {"class": "displayName"})

        author_name = html_parser.unescape("%s - %s" %(span_displayname.string.strip(), span_name.string.strip()) )
        span_count = entry.find("span", {"class": "count"})
        episode_count = span_count.string.strip()

        folder_url = '%s?action=list-author&author-url=%s' % (sys.argv[0], urllib.quote_plus(author_link))
        utils.add_directory("%s %s" % (author_name, episode_count), "DefaultDirectory.png", author_thumb, folder_url)
        return
