import mc, re, os, sys
sys.path.append(os.path.join(mc.GetApp().GetAppDir(), 'libs'))
import ba
from beautifulsoup.BeautifulSoup import BeautifulSoup
import simplejson as json
from urllib import quote_plus
import datetime, time


class Module(object):
    def __init__(self):
        self.name = "ARD Mediathek"             #Name of the channel
        self.type = ['list', 'genre']           #Choose between 'search', 'list', 'genre'
        self.episode = True                     #True if the list has episodes
        self.filter = []                        #Option to set a filter to the list
        self.genre = {}                         #Array to add a genres to the genre section [type genre must be enabled]
        self.content_type = ''                  #Mime type of the content to be played
        self.country = 'DE'                     #2 character country id code
        
        self.url_base = 'http://www.ardmediathek.de'
        self.initDate()
        
    def List(self):
        url = self.url_base + '/ard/servlet/ajax-cache/3551682/view=module/index.html'
        data = ba.FetchUrl(url)
        data = '[' +re.compile('sendungVerpasstListe = \[(.*?)\]', re.DOTALL + re.IGNORECASE).search(str(data)).group(1) + ']'
        json_data = json.loads(data)
        streamlist = list()
        for info in json_data:
            stream = ba.CreateStream()
            stream.SetName(info['titel'])
            print info['link'].split('=')[1]
            stream.SetId(info['link'].split('=')[1])
            streamlist.append(stream)

        return streamlist
    
    def Episode(self, stream_name, stream_id, page, totalpage):

        url = self.url_base + '/ard/servlet/ajax-cache/3516962/view=list/documentId='+stream_id+'/goto='+str(page)+'/index.html'
        data = ba.FetchUrl(url, 3600)
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
        
        if data < 20:
            mc.ShowDialogNotification("No episode found for " + str(stream_name))
            episodelist = list()
            return episodelist

        if totalpage == "":
            try:
                pages = soup.find( 'li', {'class' : 'mt-paging ajax-paging-li'})
                pages = pages.findAll('span')[2]
                pages = pages.contents[0][-2:].replace(' ','')
                print pages
                totalpage = int(pages)
            except:
                totalpage = 1


        episodelist = list()
        for info in soup.findAll( 'div', {'class' : 'mt-media_item'}):
            if info.findAll( 'span', {'class' : 'mt-icon mt-icon_video'}):
                detail = info.find('a')
                title = stream_name
                airtime = info.find('span', {'class' : 'mt-airtime'})
                thumb = info.find('img')

                episode = ba.CreateEpisode()
                episode.SetName(stream_name)
                episode.SetId(detail['href'].split('=')[1])
                episode.SetDescription(detail.contents[0])
                episode.SetThumbnails(self.url_base + thumb['data-src'])
                episode.SetDate(airtime.contents[0])
                episode.SetPage(page)
                episode.SetTotalpage(totalpage)
                episodelist.append(episode)

        return episodelist

    def Genre(self, genre, filter, page, totalpage):
        id = self.genre[genre]
        url = self.url_base + '/ard/servlet/ajax-cache/3517242/view=list/datum='+id+'/senderId=208/zeit=1/index.html'
        data = ba.FetchUrl(url, 2400)
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        genrelist = list()
        if data < 20:
            mc.ShowDialogNotification("No episode found for " + str(stream_name))
            genrelist = list()
            return genrelist

        for info in soup.findAll( 'div', {'class' : 'mt-media_item'}):
            if info.findAll( 'span', {'class' : 'mt-icon mt-icon_video'}):
                detail = info.find('a')
                title = detail.contents[0]
                airtime = info.find('span', {'class' : 'mt-airtime'})

                genreitem = ba.CreateEpisode()
                genreitem.SetName(title)
                genreitem.SetId(detail['href'].split('=')[1])
                genreitem.SetDate(airtime.contents[0][-9:])
                genreitem.SetPage(page)
                genreitem.SetTotalpage(totalpage)
                genrelist.append(genreitem)
        if len(genrelist) < 1:
            mc.ShowDialogNotification("No episode found for " + str(genre))
        return genrelist
        
    def Play(self, stream_name, stream_id, subtitle):
        url = self.url_base + '/ard/servlet/content/3517136?documentId='+stream_id
        data = ba.FetchUrl(url)
        try:
            rtmpdata = re.compile('mediaCollection.addMediaStream\(0, 2, "(.*?)"\);', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
        except:
            rtmpdata = re.compile('mediaCollection.addMediaStream\(0, 1, "(.*?)"\);', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
        rtmplist = rtmpdata.split('", "')

        if 'rtmp' in rtmplist[0]:
            play = ba.CreatePlay()
            play.SetContent_type('video/x-flv')
            playPath =  rtmplist[1]
            rtmpURL = rtmplist[0]
            authPath = ''

            play.SetRTMPPath(playPath)
            play.SetRTMPDomain(rtmpURL)
            play.SetRTMPAuth(authPath)

        else:
            play = ba.CreatePlay()
            play.SetPath(rtmplist[1])

        return play

    def initDate(self):
        now = datetime.datetime.now()
        for i in range(0, 6):
            newdate = now - datetime.timedelta(days=i)
            key = newdate.strftime("%d-%m-%y")
            if key == now.strftime("%d-%m-%y"):
                key = 'Heute'
            self.genre[key] = newdate.strftime("%d.%m.%Y")
   