import mc, re, os, sys
sys.path.append(os.path.join(mc.GetApp().GetAppDir(), 'libs'))
import ba, md5, time, base64
from beautifulsoup.BeautifulSoup import BeautifulSoup
from urllib import quote_plus
import datetime, time

class Module(object):
    def __init__(self):
        self.name = "Svt play"                      #Name of the channel
        self.type = ['list']                        #Choose between 'search', 'list', 'genre'
        self.episode = True                         #True if the list has episodes
        self.filter = []                            #Option to set a filter to the list
        self.genre = []                             #Array to add a genres to the genre section [type genre must be enabled]
        self.content_type = 'video/x-flv'           #Mime type of the content to be played
        self.country = 'SE'                         #2 character country id code

        self.url_base = 'http://svtplay.se'

    def List(self):
        url = self.url_base + '/alfabetisk'
        data = ba.FetchUrl(url)
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        div_main  = soup.findAll( 'div', {'class' : 'tab active'})[0]

        streamlist = list()
        for info in div_main.findAll('a'):
            if len(info.contents[0]) > 4:
                stream = ba.CreateStream()
                stream.SetName(info.contents[0])
                stream.SetId(info['href'])
                streamlist.append(stream)

        return streamlist

    def Episode(self, stream_name, stream_id, page, totalpage):
        url = self.url_base + stream_id + '?ajax,sb/sb'
        data = ba.FetchUrl(url, 3600)

        if data == "":
            mc.ShowDialogNotification("No episode found for " + str(stream_name))
            episodelist = list()
            return episodelist

        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        episodelist = list()
        for info in soup.findAll('li'):
            if len(info.a.findAll('em')) > 0:
                episode = ba.CreateEpisode()
                episode.SetName(stream_name)
                episode.SetId(info.a['href'])
                episode.SetDescription(info.a.span.contents[0].replace(' ','').replace('\n','').replace('\t',''))
                episode.SetThumbnails(info.a.img['src'])
                episode.SetDate(info.a.em.contents[0][-10:])
                episode.SetPage(page)
                episode.SetTotalpage(totalpage)
                episodelist.append(episode)

        return episodelist

    def Play(self, stream_name, stream_id, subtitle):
        url = self.url_base + stream_id
        data = ba.FetchUrl(url)
	try:
            data = re.compile('dynamicStreams=url:(.*?)\.mp4', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
            domain = re.compile('^(.*?)/kluster', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
            id = re.compile('_definst_/(.*?)$', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
        except:
            mc.ShowDialogNotification("No stream found for " + str(stream_name))
            play = ba.CreatePlay()
            return play
		
	url = 'http://www.bartsidee.nl/flowplayer/index.html?net=' + str(domain) + '&id=mp4:' + str(id) + '.mp4'
        play = ba.CreatePlay()
        play.SetPath(quote_plus(url))
        play.SetDomain('bartsidee.nl')
        play.SetJSactions(quote_plus('http://bartsidee.nl/boxee/apps/flow.js'))

        return play
