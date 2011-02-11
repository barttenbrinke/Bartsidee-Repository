import mc
import re
from BeautifulSoup import BeautifulSoup
from Func import GetCached
global url, zender, urlshow

ITUNES_BASE                  = 'http://itunes.apple.com/nl/rss/toppodcasts/limit=50/genre=1310/xml'
RADIO_BASE                   = 'http://www.radio-overzicht.nl'


def ShowNet(net):
    mc.ShowDialogWait()
    targetcontrol  	= 51
    targetwindow   	= 14000

    list = mc.GetWindow(targetwindow).GetList(targetcontrol)
    list_items = mc.ListItems()

    if net == 1:
        url = RADIO_BASE
        zender = "radio"

        data = GetCached(url, 3600).decode('utf-8')
        soup = BeautifulSoup(data, smartQuotesTo=None)
        maindiv  = soup.findAll( 'div', {'id' : 'container'})[0]

        for info in maindiv.findAll('a', {'class' : re.compile('box(| last)')}):
            try: title = re.compile('om naar (.*?) te luisteren', re.DOTALL + re.IGNORECASE).search(str(info)).group(1)
            except: title = info['title']
            link = info['href']
            thumb = info.img['src']
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(str(title))
            list_item.SetThumbnail(str(thumb))
            list_item.SetProperty("zender", str(zender))
            list_item.SetPath(str(link))
            list_items.append(list_item)

    if net == 2:
        url = ITUNES_BASE
        zender = "pod"

        data = GetCached(url, 3600).decode('utf-8')
        soup = BeautifulSoup(data, smartQuotesTo=None)

        for info in soup.findAll('entry'):
            title = info.findAll('im:name')[0].renderContents()
            link = info.link['href']
            thumb = info.findAll('im:image', {'height' : '170'})[0].renderContents()

            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(str(title))
            list_item.SetThumbnail(str(thumb))
            list_item.SetProperty("zender", str(zender))
            list_item.SetPath(str(link))
            list_items.append(list_item)

    mc.HideDialogWait()
    list.SetItems(list_items)



def ShowEpisode(urlshow, title = "", zender = ""):
    targetcontrol  	= 52
    targetwindow   	= 14000
    if zender == "radio":
        mc.ShowDialogWait()
        data = GetCached(urlshow, 3600).decode('utf-8')
        urlplay  = re.compile('<PARAM NAME="URL" VALUE="(.*?)" />', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
        data = GetCached(urlplay, 3600)
        try:
            urlplay = re.compile('mms\://(.*?)"', re.DOTALL + re.IGNORECASE + re.M).findall(data)[0]
            urlplay = 'mms://' + str(urlplay)
        except:
            urlplay = urlplay
        if '3FM' in title: urlplay = "http://shoutcast2.omroep.nl:8104"
        mc.HideDialogWait()
        ShowPlay(urlplay, title)

    if zender == "pod":
        mc.ShowDialogWait()
        data = GetCached(urlshow, 3600).decode('utf-8')
        soup = BeautifulSoup(data)

        list = mc.GetWindow(targetwindow).GetList(targetcontrol)
        list_items = mc.ListItems()

        for info in soup.findAll('tr', {'class' : 'podcast-episode'}):
            link = info['audio-preview-url']
            title = info['preview-title']
            list_item = mc.ListItem(mc.ListItem.MEDIA_AUDIO_RADIO)
            list_item.SetLabel(str(title))
            list_item.SetPath(str(link))
            list_items.append(list_item)
            
        mc.HideDialogWait()
        list.SetItems(list_items)

def ShowPlay(url, title = ""):
    player = mc.GetPlayer()
    list_item  = mc.ListItem(mc.ListItem.MEDIA_AUDIO_RADIO)
    list_item.SetPath(str(url))
    list_item.SetLabel(str(title))
    list_item.SetReportToServer(True)
    list_item.SetAddToHistory(True)
    player.Play(list_item)

def EmptyEpisode():
    targetcontrol  	= 52
    targetwindow   	= 14000
    list = mc.GetWindow(targetwindow).GetList(targetcontrol)
    list_items = mc.ListItems()
    list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    list_item.SetLabel('')
    list_item.SetPath('')
    list_items.append(list_item)
    list.SetItems(list_items)