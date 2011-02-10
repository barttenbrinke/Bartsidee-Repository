import mc, re, os, sys
sys.path.append(os.path.join(mc.GetApp().GetAppDir(), 'libs'))
import ba
from beautifulsoup.BeautifulSoup import BeautifulSoup
from itertools import izip

class Module(object):
    def __init__(self):
        self.name = "Net5 Gemist"                   #Name of the channel
        self.type = ['list']              #Choose between 'search', 'list', 'genre'
        self.episode = True                         #True if the list has episodes
        self.filter = []                            #Option to set a filter to the list
        self.genre = []                             #Array to add a genres to the genre section [type genre must be enabled]
        self.content_type = 'video/x-ms-asf'        #Mime type of the content to be played
        self.country = 'NL'                         #2 character country id code


        self.url_base = 'http://www.net5.nl'
        self.url_home = '%s/web/show/id=95681/langid=43' % self.url_base
        self.exclude = []

    def List(self):
        url = self.url_home
        data = ba.FetchUrl(url)
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        div_main  = soup.findAll( 'div', {'class' : 'mo-a alphabetical'})[0]
        div_show  = div_main.findAll( 'div', {'class' : 'wrapper'})[0]

        streamlist = list()
        for info in div_show.findAll('a'):
            stream = ba.CreateStream()
            name = info.contents[0]
            id = self.url_base + info['href']
            if not name in self.exclude:
                stream.SetName(name)
                stream.SetId(id)
                streamlist.append(stream)

        return streamlist

    def Episode(self, stream_name, stream_id, page, totalpage):
        url = str(stream_id) + '/page=' + str(page)
        data = ba.FetchUrl(url, 3600)

        if data == "":
            mc.ShowDialogNotification("Geen afleveringen gevonden voor " + str(stream_name))
            return ba.CreateEpisode()

        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        if totalpage == "":
            try:
                pages = soup.findAll( 'div', {'class' : 'paginator'})[0]
                pages = pages.findAll('span')
                totalpage = len(pages) - 1
            except:
                totalpage = 1

        div_main = soup.findAll('div', {'class' : 'mo-c double'})[0]
        div_show = div_main.findAll('div', {'class' : 'wrapper'})[0]

        info = div_show.findAll('div', {'class' : 'thumb'})
        airtime = div_show.findAll('div', {'class' : 'airtime'})

        if len(info) < 1:
            mc.ShowDialogNotification("Geen afleveringen gevonden voor " + str(stream_name))
            return ba.CreateEpisode()

        episodelist = list()
        for info_i, airtime_i in izip(info, airtime):
            episode = ba.CreateEpisode()
            episode.SetName(stream_name)
            episode.SetId(self.url_base + info_i.a['href'])
            episode.SetThumbnails(self.url_base + info_i.find('img')['src'])
            episode.SetDate(airtime_i.a.span.contents[0])
            episode.SetPage(page)
            episode.SetTotalpage(totalpage)
            episodelist.append(episode)

        return episodelist

    def Play(self, stream_name, stream_id, subtitle):
        data = ba.FetchUrl(stream_id)
        url_play = re.compile('<a class="wmv-player-holder" href="(.*?)"></a>', re.DOTALL + re.IGNORECASE).search(data).group(1)

        play = ba.CreatePlay()
        play.SetPath(url_play)

        return play
