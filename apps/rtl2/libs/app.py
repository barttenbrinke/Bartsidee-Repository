import mc
import re
import Func
from BeautifulSoup import BeautifulSoup, SoupStrainer

def clean():
    Func.CleanDb(259200)
    
def ShowDay(day):
    	mc.ShowDialogWait()
	targetcontrol  	= 51
	targetwindow   	= 14000

	if day == "vandaag":
		url = "http://www.rtl.nl/service/gemist/device/ipad/feed/index.xml"
	else:
		url = "http://www.rtl.nl/service/gemist/device/ipad/feed/index.xml?day="+str(day)

        data = Func.FetchUrl(url, 3600).decode('utf-8')
        soupStrainer  = SoupStrainer ( 'li', {'class' : 'video_item'})
        video = BeautifulSoup( str(data), soupStrainer )

	list = mc.GetWindow(targetwindow).GetList(targetcontrol)
	list_items = mc.ListItems()

        for prog in video:
            title = re.compile('.mp4">(.*?)<br', re.DOTALL + re.IGNORECASE).search(str(prog)).group(1)
            desc = re.compile('<span>(.*?)</span>', re.DOTALL + re.IGNORECASE).search(str(prog)).group(1)
            info = re.compile('<a class="v" href=(.*?)>', re.DOTALL + re.IGNORECASE).search(str(prog)).group(1)
            link = re.compile('ns_url=(.*?)"', re.DOTALL + re.IGNORECASE).search(str(info)).group(1)
            id = re.compile('http://iptv.rtl.nl/nettv/(.*?).mp4', re.DOTALL + re.IGNORECASE).search(str(link)).group(1)
            thumb = "http://iptv.rtl.nl/nettv/imagestrip/default.aspx?&width=194&height=140&files=" + id + ".poster.jpg"
            list_item 	= mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
            list_item.SetLabel(str(title.encode('utf-8','ignore')))
            list_item.SetTitle(str(title.encode('utf-8','ignore')))
            list_item.SetThumbnail(str(thumb.encode('utf-8','ignore')))
            list_item.SetDescription(str(desc.encode('utf-8','ignore')))
            list_item.SetPath(str(link.encode('utf-8','ignore')))
            list_item.SetContentType(str('video/mp4'))
            list_item.SetProviderSource('RTL')
            list_item.SetReportToServer(True)
            list_item.SetAddToHistory(True)
            list_items.append(list_item)

	mc.HideDialogWait()
        list.SetItems(list_items)

		