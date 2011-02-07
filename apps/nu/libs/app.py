import mc
import re
import Func
from BeautifulSoup import BeautifulSoup
global url

url = "http://www.nu.nl/feeds/rss/algemeen.rss"

def Show():
    	mc.ShowDialogWait()
	targetcontrol  	= 51
	targetwindow   	= 14000

        data = Func.GetCached(url, 3600)
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

	list = mc.GetWindow(targetwindow).GetList(targetcontrol)
	list_items = mc.ListItems()

        for info in soup.findAll('item'):
            title = info.title.contents[0]
            desc = info.description.contents[0]
            time = info.findAll('pubdate')[0].contents[0]
            thumb = info.enclosure['url']
            list_item 	= mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(str(title))
            list_item.SetThumbnail(str(thumb))
            list_item.SetProperty("desc", str(desc))
            list_item.SetProperty("time", str(time))
            list_items.append(list_item)

	mc.HideDialogWait()
        list.SetItems(list_items)

		