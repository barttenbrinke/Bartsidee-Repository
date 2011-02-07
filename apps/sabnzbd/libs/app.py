import mc, time, re, sys, os, random, ba
from threading import Thread
from urllib import quote, quote_plus
from beautifulsoup.BeautifulSoup import BeautifulSoup

class Sabnzbd(object):
    def __init__(self):
        self.api = mc.GetApp().GetLocalConfig().GetValue("api")
        self.host = mc.GetApp().GetLocalConfig().GetValue("host")
        self.port = mc.GetApp().GetLocalConfig().GetValue("port")
        self.retention = mc.GetApp().GetLocalConfig().GetValue("retention")

        if (self.api or self.host or self.port or self.retention) == '':
            mc.ShowDialogNotification("No credentials set, please fill in your Sabnzbd settings")

        self.db_rm_exclude = ['api', 'host', 'port', 'retention']
        ba.CleanDb(1209600, self.db_rm_exclude)
  
    def GetQuery(self):
        url = 'http://'+ self.host + ':' + self.port + '/api?mode=queue&start=START&limit=LIMIT&output=xml&apikey=' + self.api

        try:
            data = ba.FetchUrl(url)
        except:
            return
        
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
        try: speed = soup.findAll('speed')[0].contents[0]
        except: speed = ''
        timeleft = soup.findAll('timeleft')[0].contents[0]
        pause_int = soup.findAll('pause_int')[0].contents[0]
        paused = soup.findAll('paused')[0].contents[0]
        slot = soup.findAll('slot')
        
        if pause_int == '0': pause_int = 'Unlimited'
        else: pause_int = pause_int + ' s'
        window = mc.GetWindow(14444)
        if str(paused) == "True":
            window.GetToggleButton(10198).SetSelected(True)
        else:
            window.GetToggleButton(10198).SetSelected(False)
            
        if slot:
            list = window.GetList(51)
            focus = int(list.GetFocusedItem())
            print focus

            list_items = mc.ListItems()
            for info in soup.findAll('slot'):
                percentage = int(info.percentage.contents[0])
                percentage = int(round(percentage/10.0)*10.0)
                list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
                list_item.SetLabel(ba.ConvertASCII(info.filename.contents[0]))
                list_item.SetPath(str(info.nzo_id.contents[0]))
                list_item.SetProperty('queued', str(info.status.contents[0]))
                list_item.SetProperty('info', str(info.mb.contents[0]) + 'Mb - ' + str(info.timeleft.contents[0]))
                list_item.SetProperty('status', 'download-' + str(percentage) + '.png')
                list_item.SetProperty('speed', str(speed) + 'bps')
                list_item.SetProperty('timeleft', str(timeleft))
                list_item.SetProperty('paused', str(paused))
                list_item.SetProperty('pause_int', str(pause_int))
                list_item.SetProperty('percentage', str(info.percentage.contents[0]) + '%')
                list_items.append(list_item)
            list.SetItems(list_items)
            print len(list_items)
            max = len(list_items) - 1
            if focus > 0 and focus < max:
                list.SetFocusedItem(focus)
            elif focus >= max:
                list.SetFocusedItem(max)
        else:
            self.EmptySearch(14444)

    def AddQuery(self, nzb, name, cat='None'):
        url = 'http://'+ self.host + ':' + self.port + '/api?mode=addurl&name=' + nzb.replace(" ","_") + '&cat=' + quote_plus(cat) + '&nzbname=' + quote_plus(name) + '&apikey=' + self.api
        try:
            ba.FetchUrl(url)
            return True
        except:
            return False

    def ResumeQueue(self):
        url = 'http://'+ self.host + ':' + self.port + '/api?mode=resume' + '&apikey=' + self.api
        try:
            ba.FetchUrl(url)
            return True
        except:
            return False

    def PauseTime(self, length=''):
        if length == '':
            url = 'http://'+ self.host + ':' + self.port + '/api?mode=pause&apikey=' + self.api
        else:
            url = 'http://'+ self.host + ':' + self.port + '/api?mode=config&name=set_pause&value=' + str(length) + '&apikey=' + self.api

        try:
            ba.FetchUrl(url)
            return True
        except:
            return False
			
    def Delete(self, deleteid):
        url = 'http://'+ self.host + ':' + self.port + '/api?mode=queue&name=delete&value=' + deleteid + '&apikey=' + self.api
        try:
            ba.FetchUrl(url)
            return True
        except:
            return False

    def SearchNzb(self, name):
        url = 'http://www.nzbclub.com/nzbfeed.aspx?ig=1&st=5&sp=1&ns=1&sn=1&q=' + quote_plus(name) + '&de=' + self.retention
        data = ba.FetchUrl(url, 3600)
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
        list = mc.GetWindow(14445).GetList(51)
        focus = int(list.GetFocusedItem())
        list_items = mc.ListItems()

        for info in soup.findAll('item'):
            title = info.title.contents[0]
            description = info.description.contents[0]
            description = description.replace("<br />","\n")
            path = info.enclosure['url']
            date = info.findAll('pubdate')[0].contents[0]
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(ba.ConvertASCII(title))
            list_item.SetProperty('info', ba.ConvertASCII(description))
            list_item.SetProperty('date', str(date))
            list_item.SetPath(str(path))
            list_items.append(list_item)
        list.SetItems(list_items)

        max = len(list_items) - 1
        if focus > 0 and focus < max:
            list.SetFocusedItem(focus)
        elif focus >= max:
            list.SetFocusedItem(max)

    def GetCategory(self):
        url = 'http://'+ self.host + ':' + self.port + '/api?mode=queue&start=START&limit=LIMIT&output=xml&apikey=' + self.api
        data = ba.FetchUrl(url, 360).decode('utf-8')
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        list = mc.GetWindow(15000).GetList(51)
        list_items = mc.ListItems()
        for info in soup.findAll('category'):
            title = info.contents[0]
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(str(title.encode('utf-8')))
            list_items.append(list_item)
        list.SetItems(list_items)

    def EmptySearch(self, window):
        list = mc.GetWindow(window).GetList(51)
        list_items = mc.ListItems()
        del list_items[:]
        list.SetItems(list_items)

    def GetRet(self):
        retention = ['unlimited','1 month','3 months','6 months','12 months','24 months']
        value = ['','1','3','6','12','24']

        list = mc.GetWindow(16000).GetList(52)
        list_items = mc.ListItems()
        for i, val in enumerate(retention):
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(str(retention[i]))
            list_item.SetPath(str(value[i]))
            list_items.append(list_item)
        list.SetItems(list_items)

        valueret = mc.GetApp().GetLocalConfig().GetValue("retention")
        if valueret:
            for index, item in enumerate(value):
                if item == valueret:
                    list.SetFocusedItem(index)

    def GetPauze(self):
        pauze = ['unlimited','5 Minutes','10 Minutes','30 Minutes','60 Minutes','120 Minutes']
        value = ['','5','10','30','60','120']

        list = mc.GetWindow(16001).GetList(51)
        list_items = mc.ListItems()
        for i, val in enumerate(pauze):
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(str(pauze[i]))
            list_item.SetPath(str(value[i]))
            list_items.append(list_item)
        list.SetItems(list_items)

class _Refresh(Thread):
    # Define class vars. #
    def __init__ (self):
        Thread.__init__(self)

    # Run() method required for Thread. #
    def run(self):
        b = Sabnzbd()
        while self._window():
            b.GetQuery()
            time.sleep(5)
    def _window(self):
        try:
            mc.GetWindow(14444)
            return True
        except:
            return False
