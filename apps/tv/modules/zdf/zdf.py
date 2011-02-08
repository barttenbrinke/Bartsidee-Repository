import mc, re, os, sys
sys.path.append(os.path.join(mc.GetApp().GetAppDir(), 'libs'))
import ba
from beautifulsoup.BeautifulSoup import BeautifulSoup
from itertools import izip
import datetime, time

class Module(object):
    def __init__(self):
        self.name = "ZDF Mediathek"             #Name of the channel
        self.type = ['list', 'genre']             #Choose between 'search', 'list', 'genre'
        self.episode = True                         #True if the list has episodes
        self.filter = []           #Option to set a filter to the list
        self.genre = {}           #Array to add a genres to the genre section [type genre must be enabled]
        self.content_type = 'video/x-ms-asx'        #Mime type of the content to be played
        self.country = 'DE'                         #2 character country id code
        
        self.url_base = 'http://www.zdf.de'
        self.initDate()

    def List(self):
        array = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        title = []
        id = []
        for letter in array:
            url = self.url_base + '/ZDFmediathek/xmlservice/web/sendungenAbisZ?characterRangeStart='+letter+'&detailLevel=2&characterRangeEnd='+letter
            data = ba.FetchUrl(url)
            soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

            title.extend(soup.findAll('title'))
            id.extend(soup.findAll('assetid'))

        streamlist = list()
        for title_i,id_i in izip(title,id):
            stream = ba.CreateStream()
            stream.SetName(title_i.contents[0].replace('"',''))
            stream.SetId(id_i.contents[0])
            streamlist.append(stream)

        return streamlist
    
    def Episode(self, stream_name, stream_id, page, totalpage):

        url = self.url_base + '/ZDFmediathek/xmlservice/web/aktuellste?id='+stream_id+'&maxLength=50'
        data = ba.FetchUrl(url, 3600)
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
        
        if len(data) < 5:
            mc.ShowDialogNotification("No episode found for " + str(stream_name))
            episodelist = list()
            return episodelist

        teaser = soup.findAll('teaser')

        episodelist = list()
        for info in teaser:
            if info.type.contents[0] == 'video':
                title = info.find('title')
                title = info.find('title')
                detail = info.find('detail')
                id = info.find('assetid')
                airtime = info.find('airtime')
                airtime = airtime.contents[0]
                thumb = self.url_base + '/ZDFmediathek/contentblob/'+ str(id.contents[0]) +'/timg276x155blob'

                episode = ba.CreateEpisode()
                episode.SetName(title.contents[0])
                episode.SetId(id.contents[0])
                episode.SetDescription(stream_name + ': ' + detail.contents[0])
                episode.SetThumbnails(thumb)
                episode.SetDate(airtime)
                episode.SetPage(page)
                episode.SetTotalpage(totalpage)
                episodelist.append(episode)

        return episodelist

    def Genre(self, genre, filter, page, totalpage):
        id = self.genre[genre]
        url = self.url_base + '/ZDFmediathek/xmlservice/web/sendungVerpasst?startdate=' + id +'&enddate='+id+'&maxLength=50'
        data = ba.FetchUrl(url, 2400)
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        genrelist = list()
        if len(soup) < 20:
            mc.ShowDialogNotification("No episode found for " + str(genre))
            return genrelist

        teaser = soup.findAll('teaser')

        for info in teaser:
            if info.type.contents[0] == 'video':
                title = info.find('title')
                title = info.find('title')
                id = info.find('assetid')
                airtime = info.find('airtime')
                airtime = airtime.contents[0]

                genreitem = ba.CreateEpisode()
                genreitem.SetName(title.contents[0])
                genreitem.SetId(id.contents[0])
                genreitem.SetDate(airtime[-5:])
                genreitem.SetPage(page)
                genreitem.SetTotalpage(totalpage)
                genrelist.append(genreitem)
        if len(genrelist) < 1:
            mc.ShowDialogNotification("No episode found for " + str(genre))
        return genrelist
        
    def Play(self, stream_name, stream_id, subtitle):
        url = 'http://www.zdf.de/ZDFmediathek/xmlservice/web/beitragsDetails?ak=web&id='+stream_id
        data = ba.FetchUrl(url)
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        url = soup.find('formitaet',{'basetype':'wmv3_wma9_asf_mms_asx_http'})
        url = url.url.contents[0]

        sub = soup.find('caption')
        try:
            sub = sub.url.contents[0]
        except:
            sub = ''

        play = ba.CreatePlay()
        play.SetPath(url)
        if subtitle:
            if sub:
                play.SetSubtitle(str(sub))
                play.SetSubtitle_type('flashxml')

        return play

    def initDate(self):
        now = datetime.datetime.now()
        for i in range(0, 6):
            newdate = now - datetime.timedelta(days=i)
            key = newdate.strftime("%d-%m-%y")
            if key == now.strftime("%d-%m-%y"):
                key = 'Heute'
            self.genre[key] = newdate.strftime("%d%m%y")


   