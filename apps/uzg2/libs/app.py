import mc, re, base64, md5, xbmc, time, os
from urllib import quote_plus
from Func import FetchUrl, CleanDb
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

class betaUZG(object):
    def __init__(self):
        self.mainurl = 'http://beta.uitzendinggemist.nl'
        CleanDb(259200)

    def GetShow(self, search):
        url = 'http://beta.uitzendinggemist.nl/programmas/search'
        params = 'query=' + quote_plus(search)
        data = FetchUrl(url, 0, True, params).decode('utf-8')
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
        pagdiv = soup.find("ul")
        if len(pagdiv.findAll("a")) == 0:
            mc.ShowDialogNotification("Geen resultaten gevonden")

        mc.GetWindow(14444).GetControl(1200).SetVisible(True)
        mc.GetWindow(14444).GetControl(1201).SetVisible(False)
        list = mc.GetWindow(14444).GetList(51)
        list_items = mc.ListItems()

        for info in pagdiv.findAll("a"):
            link = info['href'].split('/')[2]
            title = info.contents[0]
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(str(title.encode('utf-8')))
            list_item.SetPath(str(link))
            list_items.append(list_item)
        list.SetItems(list_items)

    def GetEpisode(self, id, title="", page=1, totalpage=""):
        mc.ShowDialogWait()
        url = 'http://beta.uitzendinggemist.nl/quicksearch?page=' + str(page) + '&series_id=' + id
        data = FetchUrl(url, 3600, True).decode('utf-8')
        data = re.compile('"quicksearch-results", "(.*?)"\)', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
        data = data.replace('\\"','"').replace('\\n','').replace('\\t','')
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        if totalpage == "":
            try:
                pagediv = soup.findAll( 'div', {'class' : 'pagination'})[0]
                apage = pagediv.findAll("a")
                totalpage = int(apage[len(apage)-2].contents[0])
            except:
                totalpage = 1

        mc.GetWindow(14444).GetControl(1200).SetVisible(False)
        mc.GetWindow(14444).GetControl(1201).SetVisible(True)
        list = mc.GetWindow(14444).GetList(52)
        list_items = mc.ListItems()

        for info in soup.findAll("li"):
            views = info.span.contents[0].replace(' ','')
            thumb = info.a.img['src']
            path = self.mainurl + info.h3.a['href']
            date = info.h3.a.contents[0]
            desc = info.p.contents[0]
            print str(thumb)
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(str(title))
            list_item.SetPath(str(path))
            list_item.SetThumbnail(str(thumb))
            list_item.SetProperty('date', str(date))
            list_item.SetProperty('desc', str(desc))
            list_item.SetProperty('views', str(views))
            list_item.SetProperty('net', str(''))
            list_item.SetProperty('page', str(page))
            list_item.SetProperty('id', str(id))
            list_item.SetProperty('totalpage', str(totalpage))
            list_items.append(list_item)

        mc.HideDialogWait()
        list.SetItems(list_items)
        mc.GetWindow(14444).GetControl(1201).SetFocus()

    def GetRecent(self, time, net="", page=1, totalpage=""):
        mc.ShowDialogWait()
        url = 'http://beta.uitzendinggemist.nl/7dagen/' + time
        if net != "": url = url + str(net)
        url = url + '?weergave=detail&page=' + str(page)
        data = FetchUrl(url, 3600).decode('utf-8')
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
        if totalpage == "":
            try:
                pagediv = soup.findAll( 'div', {'class' : 'pagination'})[0]
                apage = pagediv.findAll("a")
                totalpage = int(apage[len(apage)-2].contents[0])
            except:
                totalpage = 1

        showdiv = soup.find( 'table', {'class' : 'broadcasts detail'})
        mc.GetWindow(14444).GetControl(1200).SetVisible(False)
        mc.GetWindow(14444).GetControl(1201).SetVisible(True)
        list = mc.GetWindow(14444).GetList(52)
        list_items = mc.ListItems()

        for info in showdiv.findAll("tr"):
            omroep = info.findAll(attrs={"class" : "broadcaster-logo"})[0]['alt']
            if omroep == "Nederland 1": omroep = "nl11.png"
            elif omroep == "Nederland 2": omroep = "nl22.png"
            elif omroep == "Nederland 3": omroep = "nl33.png"

            try:
                thumb = info.findAll(attrs={"class" : "thumbnail"})[0]['src']
            except:
                thumb = info.findAll(attrs={"class" : "thumbnail placeholder"})[0]['src']
            path = self.mainurl + info.find(attrs={"class" : "thumbnail_wrapper"})['href']
            date = info.find(attrs={"class" : "episode"}).contents[0]
            title = info.findAll(attrs={"class" : "series"})[0].contents[0]
            desc = info.find('div', {'class' : 'description'}).p.contents[0]
            
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(str(title))
            list_item.SetPath(str(path))
            list_item.SetThumbnail(str(thumb))
            list_item.SetProperty('date', str(date))
            list_item.SetProperty('desc', str(desc))
            list_item.SetProperty('net', str(net))
            list_item.SetProperty('omroep', str(omroep))
            list_item.SetProperty('page', str(page))
            list_item.SetProperty('totalpage', str(totalpage))
            list_items.append(list_item)

        mc.HideDialogWait()
        list.SetItems(list_items)
        mc.GetWindow(14444).GetControl(1201).SetFocus()

    def GetStream(self, url, title="", sub=False):
        mc.ShowDialogWait()
        data = FetchUrl(url, 3600).decode('utf-8')
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
        streamid = re.compile("load_player\('(.*?)'", re.DOTALL + re.IGNORECASE).search(str(soup)).group(1)
        if streamid == "": mc.ShowDialogNotification("Geen stream beschikbaar...")
        
        data = FetchUrl('http://player.omroep.nl/info/security', 0)
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
        try:
            key = soup.session.key.contents[0]
        except:
            mc.ShowDialogNotification("Kan de security key niet ophalen")
            return
        security = base64.b64decode(key)

        sub = mc.GetApp().GetLocalConfig().GetValue('sub')
        if sub == 'True':
            subFilePath = self.GetSub(security, streamid)

        securitystr = str(security).split('|')[1]
        md5code = streamid + '|' + securitystr
        md5code = md5.md5(md5code).hexdigest()

        streamdataurl = 'http://player.omroep.nl/info/stream/aflevering/' + str(streamid) + '/' + str(md5code).upper()
        data = FetchUrl(streamdataurl, 0).decode('utf-8')
        xmlSoup = BeautifulSoup(data)
        streamurl = xmlSoup.find(attrs={"compressie_formaat" : "wvc1"})
        streamurl = streamurl.streamurl.contents[0].replace(" ","").replace("\n","").replace("\t","")
        mc.HideDialogWait()

        player = mc.GetPlayer()
        list_item  = mc.ListItem(mc.ListItem.MEDIA_VIDEO_EPISODE)
        list_item.SetLabel(str(title))
        list_item.SetTitle(str(title))
        list_item.SetPath(str(streamurl))
        list_item.SetContentType(str('video/x-ms-asf'))
        list_item.SetProviderSource('UZG')
        list_item.SetReportToServer(True)
        list_item.SetAddToHistory(True)
        player.Play(list_item)
        if sub == 'True':
            time.sleep(5)
            xbmc.Player().setSubtitles(str(subFilePath))

    def GetSub(self, security, streamid):
        samisecurity1 = int(str(security).split('|')[0])
        samisecurity2 = str(security).split('|')[3]
        str4 = hex(samisecurity1)[2:]
        str5 = 'aflevering/' + streamid + '/format/sami'
        str6 = 'embedplayer'
        samimd5 = str(samisecurity2) + str(str5) + str(str4) + str(str6)
        str7 = md5.md5(samimd5).hexdigest()
        samiurl = 'http://ea.omroep.nl/tt888/' + str(str6) + '/' + str(str7).lower() + '/' + str(str4) + '/' + str(str5)
        data = FetchUrl(samiurl, 0)
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
        i = 1
        sync = ''
        temp = ''
        for info in soup.findAll("sync"):
            if info.find(attrs={"class" : "ENUSCC"}):
                sync  = sync + str(i) + '\n'
                temp = info.find(attrs={"class" : "ENUSCC"}).contents[0]
                timemsec = str(info['start'])[-3:]
                timesec = int(str(info['start']))/1000
                hour = timesec / 3600
                minute = (timesec - (hour*3600)) / 60
                sec = timesec - (hour*3600) - (minute*60)
                srttime = str(hour) + ':' + str(minute) + ':' + str(sec) + ',' + str(timemsec)
                sync = sync + str(srttime)
                i = i + 1
            else:
                timemsec = str(info['start'])[-3:]
                timesec = int(str(info['start']))/1000
                hour = timesec / 3600
                minute = (timesec - (hour*3600)) / 60
                sec = timesec - (hour*3600) - (minute*60)
                srttime = str(hour) + ':' + str(minute) + ':' + str(sec) + ',' + str(timemsec)
                sync = sync + ' --> ' + str(srttime) + '\n'
                sync = sync + str(temp) + '\n' + '\n'
        tmpPath = mc.GetTempDir()
        subFilePath = tmpPath+os.sep+'subcache.srt'
        f = open(subFilePath, "w")
        f.write(sync)
        f.close()
        return subFilePath