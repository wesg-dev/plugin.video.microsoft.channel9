import sys
import urllib
import os
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import control

url_langs = "lang=id&lang=cs&lang=da&lang=de&lang=et&lang=en&lang=es&lang=fr&lang=hr&lang=it&lang=sw&lang=lv&"
url_langs += "lang=hu&lang=nl&lang=nb&lang=uz&lang=pl&lang=pt&lang=pt-br&lang=ro&lang=sk&lang=sl&lang=sr-cyrl&"
url_langs += "lang=fi&lang=sv&lang=vi&lang=tr&lang=el&lang=bg&lang=ru&lang=uk&lang=hy&lang=he&lang=ur&lang=ar&"
url_langs += "lang=hi&lang=th&lang=ko&lang=ja&lang=zh-cn&lang=zh-tw"

url_root = "https://channel9.msdn.com/"

def add_entry_video(entry):
    # Thumbnail...
    div_entry_image = entry.find("div", {"class": "entry-image"})
    thumbnail = div_entry_image.find("img", {"class": "thumb"})["src"]

    # Title
    div_entry_meta = entry.find("div", {"class": "entry-meta"})
    a_title = div_entry_meta.find("a", {"class": "title"})
    title = a_title.string

    # Video page
    video_page_url = a_title["href"]

    # Genre (date)...
    div_data = div_entry_meta.find("div", {"class": "data"})
    span_class_date = div_data.find("span", {"class": "date"})
    genre = span_class_date.string

    # Plot
    div_description = div_entry_meta.find("div", {"class": "description"})
    plot = div_description.string

    list_item = control.item(title, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
    list_item.setInfo("video", {"Title": title, "Studio": "Microsoft Channel 9", "Plot": plot, "Genre": genre})
    plugin_play_url = '%s?action=play&video_page_url=%s' % (sys.argv[0], urllib.quote_plus(video_page_url))
    control.addItem(handle=int(sys.argv[1]), url=plugin_play_url, listitem=list_item, isFolder=False)


def add_next_page(self, bs, item_url, page):
    ul_paging = bs.find("ul", {"class": "paging"})
    if ul_paging is not None:
        list_item = control.item(control.lang(30503) % page, iconImage="DefaultFolder.png",
                                 thumbnailImage=os.path.join(self.IMAGES_PATH, 'next-page.png'))
        control.addItem(handle=int(sys.argv[1]), url=item_url, listitem=list_item, isFolder=True)


def add_directory(text, icon, thumbnail, url):
    list_item = xbmcgui.ListItem(text, iconImage=icon, thumbnailImage=thumbnail)
    control.addItem(handle=int(sys.argv[1]), url=url, listitem=list_item, isFolder=True)


def set_no_sort():
    control.sort(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_NONE)
