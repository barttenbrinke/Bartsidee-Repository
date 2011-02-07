import mc
import re
from BeautifulSoup import BeautifulSoup
from Func import GetCached
global urlbase, urlshow, zender

NET5_BASE                   = 'http://www.net5.nl'
NET5_HOME                   = '%s/web/show/id=95681/langid=43' % NET5_BASE
SBS6_BASE                   = 'http://www.sbs6.nl'
SBS6_HOME                   = '%s/web/show/id=73863/langid=43' % SBS6_BASE
VERONICA_BASE               = 'http://www.veronicatv.nl'
VERONICA_HOME               = '%s/web/show/id=96520/langid=43' % VERONICA_BASE
#path = sys.path[0]

def ShowNet(net):
    mc.ShowDialogWait()
    targetcontrol  	= 51
    targetwindow   	= 14000
	
    if net == 1:
        urlbase = SBS6_BASE
        url = SBS6_HOME
        zender = 'sbs'
    if net == 2:
        urlbase = NET5_BASE
        url = NET5_HOME
        zender = 'net5'
    if net == 3:
        urlbase = VERONICA_BASE
	url = VERONICA_HOME
        zender = 'veronica'
		
    data = GetCached(url, 3600).decode('utf-8')
    soup = BeautifulSoup(data)
    maindiv  = soup.findAll( 'div', {'class' : 'mo-a alphabetical'})[0]
    showdiv  = maindiv.findAll( 'div', {'class' : 'wrapper'})[0]

    list = mc.GetWindow(targetwindow).GetList(targetcontrol)
    list_items = mc.ListItems()

    for info in showdiv.findAll('a'):
	title = info.renderContents()
        link = urlbase + str(info['href'])
        list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
        list_item.SetLabel(str(title))
        list_item.SetProperty("zender", str(zender))
        list_item.SetPath(str(link))
        list_items.append(list_item)

    list.SetItems(list_items)
    mc.HideDialogWait()

def ShowEpisode(urlshow):
    mc.ShowDialogWait()
    targetcontrol  	= 52
    targetwindow   	= 14000

    urlbase = re.compile('http://(.*?).nl').findall(urlshow)[0]
    data = GetCached(urlshow, 3600).decode('utf-8')
    soup = BeautifulSoup(data)
    try:
	pages = soup.findAll( 'div', {'class' : 'paginator'})[0]
	pages = pages.findAll('span')
	pages = len(pages) - 1
    except:
        pages = 1
        
    list = mc.GetWindow(targetwindow).GetList(targetcontrol)
    list_items = mc.ListItems()

    for i in range(1, pages+1):
        url  = str(urlshow) + '/page=' + str(i)
        data = GetCached(url, 3600).decode('utf-8')
        soup = BeautifulSoup(data)

        maindiv  = soup.findAll( 'div', {'class' : 'mo-c double'})[0]
        showdiv  = maindiv.findAll( 'div', {'class' : 'wrapper'})[0]
        thumb = showdiv.findAll( 'div', {'class' : 'thumb'})
        airtime = showdiv.findAll( 'div', {'class' : 'airtime'})

        count = len(thumb)

        for i in range(0, count):
            link = 'http://' + urlbase + '.nl' + thumb[i].a['href']
            thumbnail = 'http://' + urlbase + '.nl' + thumb[i].img['src']
            date = airtime[i].a.span.renderContents()
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetThumbnail(str(thumbnail))
            list_item.SetLabel(str(date))
            list_item.SetPath(str(link))
            list_items.append(list_item)
            
    mc.HideDialogWait()
    list.SetItems(list_items)
    list.control.SetFocus(0)

def ShowPlay(url):
    mc.ShowDialogWait()
    player = mc.GetPlayer()
    data = GetCached(url, 3600).decode('utf-8')
    playurl = re.compile('<a class="wmv-player-holder" href="http://asx.sbsnet.nl/(.*?)"></a>', re.DOTALL + re.IGNORECASE).search(data).group(1)
    list_item  = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
    list_item.SetPath("mms://pssbswm.fplive.net/pssbswm/w/"+ str(playurl))
    list_item.SetReportToServer(True)
    list_item.SetAddToHistory(True)
    mc.HideDialogWait()
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