import mc, re, os, sys
sys.path.append(os.path.join(mc.GetApp().GetAppDir(), 'libs'))
import ba, md5, time, base64
from beautifulsoup.BeautifulSoup import BeautifulSoup
from urllib import quote_plus
import datetime, time

class Module(object):
    def __init__(self):
        self.name = "Uitzending Gemist"             #Name of the channel
        self.type = ['search','genre']             #Choose between 'search', 'list', 'genre'
        self.episode = True                         #True if the list has episodes
        self.filter = ['nl1','nl2','nl3']           #Option to set a filter to the list
        self.genre = ['vandaag','gisteren']           #Array to add a genres to the genre section [type genre must be enabled]
        self.content_type = 'video/x-ms-asf'        #Mime type of the content to be played
        self.country = 'NL'                         #2 character country id code
        
        self.url_base = 'http://beta.uitzendinggemist.nl'
        self.initDate()

    def Search(self, search):
        url = self.url_base + '/programmas/search'
        params = 'query=' + quote_plus(search)
        data = ba.FetchUrl(url, 0, True, params)

        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
        div_page = soup.find("ul")
        
        streamlist = list()
        try:
            div_page.findAll("a")
        except:
            return streamlist

        for info in div_page.findAll('a'):
            stream = ba.CreateStream()
            stream.SetName(info.contents[0])
            stream.SetId(info['href'].split('/')[2])
            streamlist.append(stream)

        return streamlist
    
    def Episode(self, stream_name, stream_id, page, totalpage):
        url = self.url_base + '/quicksearch?page=' + str(page) + '&series_id=' + stream_id
        data = ba.FetchUrl(url, 3600)

        if data == "":
            mc.ShowDialogNotification("No episode found for " + str(stream_name))
            episodelist = list()
            return episodelist

        data = re.compile('"quicksearch-results", "(.*?)"\)', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
        data = data.replace('\\"','"').replace('\\n','').replace('\\t','')
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        if totalpage == "":
            try:
                pages = soup.findAll( 'div', {'class' : 'pagination'})[0]
                pages = pages.findAll('a')
                totalpage = int(pages[len(pages)-2].contents[0])
            except:
                totalpage = 1

        episodelist = list()
        for info in soup.findAll('li'):
			try: 
				id = info.h3.a['href']
			except:
				id = False
			if id:
				episode = ba.CreateEpisode()
				episode.SetName(stream_name)
				episode.SetId(self.url_base + id)
				episode.SetDescription(info.span.contents[0].replace(' ','') + ' - '+ info.p.contents[0])
				episode.SetThumbnails(info.a.img['src'])
				episode.SetDate(info.h3.a.contents[0])
				episode.SetPage(page)
				episode.SetTotalpage(totalpage)
				episodelist.append(episode)

        return episodelist

    def Genre(self, genre, filter, page, totalpage):
        url = self.url_base + '/7dagen/' + genre
        if filter != "": url = url + ',' + str(filter)
        url = url + '?weergave=detail&page=' + str(page)
        data = ba.FetchUrl(url, 3600)
        if data == "":
            mc.ShowDialogNotification("No genre found for " + str(genre))
            genrelist = list()
            return genrelist
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
        if totalpage == "":
            try:
                pagediv = soup.findAll( 'div', {'class' : 'pagination'})[0]
                apage = pagediv.findAll("a")
                totalpage = int(apage[len(apage)-2].contents[0])
            except:
                totalpage = 1

        div_show = soup.find( 'table', {'class' : 'broadcasts detail'})

        genrelist = list()
        for info in div_show.findAll("tr"):
            omroep = info.findAll(attrs={"class" : "broadcaster-logo"})[0]['alt']
            if omroep == "Nederland 1": omroep = "nl1"
            elif omroep == "Nederland 2": omroep = "nl2"
            elif omroep == "Nederland 3": omroep = "nl3"
            try:
                thumb = info.findAll(attrs={"class" : "thumbnail"})[0]['src']
            except:
                thumb = info.findAll(attrs={"class" : "thumbnail placeholder"})[0]['src']
            path = self.url_base + info.find(attrs={"class" : "thumbnail_wrapper"})['href']
            date = info.find(attrs={"class" : "time"}).time.contents[0].replace(' ','').replace('\n','').replace('\t','')
            title = info.findAll(attrs={"class" : "series"})[0].contents[0]
            desc = info.find('div', {'class' : 'description'}).p.contents[0]

            genreitem = ba.CreateEpisode()
            genreitem.SetName(title)
            genreitem.SetId(path)
            genreitem.SetDescription(desc)
            genreitem.SetThumbnails(thumb)
            genreitem.SetDate(date)
            genreitem.SetFilter(str(omroep).upper())
            genreitem.SetPage(page)
            genreitem.SetTotalpage(totalpage)
            genrelist.append(genreitem)

        return genrelist
        
    def Play(self, stream_name, stream_id, subtitle):
        data = ba.FetchUrl(stream_id, 3600)
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
        streamid = re.compile("load_player\('(.*?)'", re.DOTALL + re.IGNORECASE).search(str(soup)).group(1)
        if streamid == "": mc.ShowDialogNotification("Geen stream beschikbaar...")

        data = ba.FetchUrl('http://player.omroep.nl/info/security', 0)
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
        try:
            key = soup.session.key.contents[0]
        except:
            mc.ShowDialogNotification("Kan de security key niet ophalen")
            return
        security = base64.b64decode(key)

        securitystr = str(security).split('|')[1]
        md5code = streamid + '|' + securitystr
        md5code = md5.md5(md5code).hexdigest()

        streamdataurl = 'http://player.omroep.nl/info/stream/aflevering/' + str(streamid) + '/' + str(md5code).upper()
        data = ba.FetchUrl(streamdataurl, 0).decode('utf-8')
        xmlSoup = BeautifulSoup(data)
        streamurl = xmlSoup.find(attrs={"compressie_formaat" : "wvc1"})
        url_play = streamurl.streamurl.contents[0].replace(" ","").replace("\n","").replace("\t","")

        play = ba.CreatePlay()
        play.SetPath(url_play)
        if subtitle:
            play.SetSubtitle(self.GetSubtitle(security, streamid))
            play.SetSubtitle_type('sami')

        return play

    def initDate(self):
        now = datetime.datetime.now()
        for i in range(2, 7):
            newdate = now - datetime.timedelta(days=i)
            self.genre.append(newdate.strftime("%Y-%m-%d"))

    def GetSubtitle(self, security, streamid):
        samisecurity1 = int(str(security).split('|')[0])
        samisecurity2 = str(security).split('|')[3]
        str4 = hex(samisecurity1)[2:]
        str5 = 'aflevering/' + streamid + '/format/sami'
        str6 = 'embedplayer'
        samimd5 = str(samisecurity2) + str(str5) + str(str4) + str(str6)
        str7 = md5.md5(samimd5).hexdigest()
        url = 'http://ea.omroep.nl/tt888/' + str(str6) + '/' + str(str7).lower() + '/' + str(str4) + '/' + str(str5)
        return url



   