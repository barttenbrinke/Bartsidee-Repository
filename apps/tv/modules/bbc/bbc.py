import mc, re, os, sys
sys.path.append(os.path.join(mc.GetApp().GetAppDir(), 'libs'))
import ba, md5, time, base64
from beautifulsoup.BeautifulSoup import BeautifulSoup
from urllib import quote_plus, quote
import datetime, time
import simplejson as json

class Module(object):
    def __init__(self):
        self.name = "BBC iPlayer"                   #Name of the channel
        self.type = ['search', 'genre']                      #Choose between 'search', 'list', 'genre'
        self.episode = True                         #True if the list has episodes
        self.filter = []                            #Option to set a filter to the list
        self.genre = []                             #Array to add a genres to the genre section [type genre must be enabled]
        self.content_type = 'video/x-flv'           #Mime type of the content to be played
        self.country = 'UK'                         #2 character country id code
        
        self.url_base = 'http://www.bbc.co.uk'
        #self.genre_links = {"Children's":"childrens", "Comedy":"comedy", "Drama":"drama", "Entertainment":"entertainment", "Factual":"factual", "Films":"films", "Learning":"learning", "Lifestyle and Leisure":"lifestyle_and_leisure", "Music":"music", "News":"news", "Religion and Ethics":"religion_and_ethics", "Sport":"sport", "Northern Ireland":"northern_ireland", "Scotland":"scotland", "Wales":"wales", "Audio Described":"audiodescribed", "Sign Zone":"signed"}
        self.genre_links = {"Children's":"9100001", "Comedy":"9100098", "Drama":"9100003", "Entertainment":"9100099", "Factual":"9100005", "Films":"9100093", "Learning":"9100004", "Lifestyle and Leisure":"9300054", "Music":"9100006", "News":"9100007", "Religion and Ethics":"9100008", "Sport":"9100010", "Northern Ireland":"9100094", "Scotland":"9100095", "Wales":"9100097", "Audio Described":"dubbedaudiodescribed", "Sign Zone":"signed"}
        self.Categories()

    def Search(self, search):
        url = 'http://search.bbc.co.uk/suggest?scope=iplayer&format=xml&callback=xml.suggest&q=' + quote_plus(search)
        data = ba.FetchUrl(url, 0)

        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        streamlist = list()
        for info in soup.findAll('text'):
            stream = ba.CreateStream()
            stream.SetName(info.contents[0])
            stream.SetId(ba.ConvertASCII(info.contents[0]))
            streamlist.append(stream)

        return streamlist
    
    def Episode(self, stream_name, stream_id, page, totalpage):
        url = self.url_base + '/iplayer/widget/startswith/site/bigscreen/media_set/pc-bigscreen/json/1/bigscreen_layout/sd/service_type/tv/template/index/starts_with/' + quote(stream_id)
        data = ba.FetchUrl(url, 3600)

        if len(data) < 10:
            mc.ShowDialogNotification("No episode found for " + str(stream_name))
            episodelist = list()
            return episodelist

        json_data = json.loads(data)

        episodelist = list()
        for info in json_data['data']:
            episode = ba.CreateEpisode()
            episode.SetName(info['s'])
            episode.SetId(self.url_base + info['url'])
            episode.SetDescription('')
            episode.SetThumbnails('http://node1.bbcimg.co.uk/iplayer/images/episode/' + re.compile('episode\/(.*?)\/', re.DOTALL + re.IGNORECASE).search(info['url']).group(1) + '_288_162.jpg')
            episode.SetDate(info['t'])
            episode.SetPage(page)
            episode.SetTotalpage(totalpage)
            episodelist.append(episode)
        return episodelist

    def Genre(self, genre, filter, page, totalpage):
        url = self.url_base + '/iplayer/widget/listview/site/bigscreen/media_set/pc-bigscreen/json/1/bigscreen_layout/sd/service_type/tv/category/' + quote(self.genre_links[genre]) + '/perpage/100/block_type/episode'
        data = ba.FetchUrl(url, 3600)

        if len(data) < 10:
            mc.ShowDialogNotification("No episode found for " + str(stream_name))
            episodelist = list()
            return episodelist

        json_data = json.loads(data)
        
        genrelist = list()
        for info in json_data['data']:
            genreitem = ba.CreateEpisode()
            genreitem.SetName(info['s'])
            genreitem.SetId(self.url_base + info['url'])
            genreitem.SetDate(info['t'])
            genreitem.SetPage(page)
            genreitem.SetTotalpage(totalpage)
            genrelist.append(genreitem)

        return genrelist

    def Play(self, stream_name, stream_id, subtitle):

        id = re.compile('episode\/(.*?)\/', re.DOTALL + re.IGNORECASE).search(str(stream_id)).group(1)
        url = self.url_base + '/iplayer/episode/' + id + '/'
        #data = ba.FetchUrl(stream_id)
        #pid = re.compile('ep.setVersionPid\("(.*?)"\)', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
        
        #surl = 'http://www.bbc.co.uk/mediaselector/4/mtis/stream/' + pid
        #bitrate = []
        #data = ba.FetchUrl(surl)
        #soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
        #for info in soup.findAll('media', {'bitrate':True}):
        #   bitrate.append(int(info['bitrate']))
        #bitrate.sort()
        #max = str(bitrate[-1])
        
        #media = soup.find('media', {'bitrate':max})
        #print media
        #connection = media.find('connection', {'supplier':'akamai'})
        #if not connection: connection = media.find('connection', {'supplier':'limelight'})

        #identifier  = connection['identifier']
        #server      = connection['server']
        #supplier    = connection['supplier']
        #try:
        #    auth    = connection['authString']
        #except:
        #    auth    = connection['authstring']

        #try:
        #    application = connection['application']
        #except:
        #    application = 'live'

        #if subtitle:
        #    sub_url = soup.find('media', {'kind':'captions'})
        #    sub_url = sub_url.connection['href']

        #timeout = 600
        #swfplayer = 'http://www.bbc.co.uk/emp/10player.swf'
        #params = dict(protocol = "rtmp", port = "1935", server = server, auth = auth, ident = identifier, app = application)

        #if supplier == "akamai":
        #    url = "%(protocol)s://%(server)s:%(port)s/%(app)s?%(auth)s playpath=%(ident)s" % params
        #elif supplier == 'limelight':
            # note that librtmp has a small issue with constructing the tcurl here. we construct it ourselves for now (fixed in later librtmp)
        #    url = "%(protocol)s://%(server)s:%(port)s/ app=%(app)s?%(auth)s tcurl=%(protocol)s://%(server)s:%(port)s/%(app)s?%(auth)s playpath=%(ident)s" % params

        #    url += " swfurl=%s swfvfy=true timeout=%s" % (swfplayer, timeout)

        #play.SetPath(url)


        #url = 'http://www.bartsidee.nl/flowplayer2/index.html?net=' + str(domain) + '&id=mp4:' + str(id)
        #play = ba.CreatePlay()
        #play.SetPath(quote_plus(url))
        #play.SetDomain('bartsidee.nl')
        #play.SetJSactions(quote_plus('http://bartsidee.nl/boxee/apps/flow.js'))

        if subtitle:
            play = ba.CreatePlay()
            play.SetPath(quote_plus(url))
            play.SetDomain('bbc.co.uk')
            play.SetJSactions(quote_plus('http://bartsidee.nl/boxee/apps/bbc1.js'))
        else:
            play = ba.CreatePlay()
            play.SetPath(quote_plus(url))
            play.SetDomain('bbc.co.uk')
            play.SetJSactions(quote_plus('http://bartsidee.nl/boxee/apps/bbc0.js'))

        return play

    def Categories(self):
        for key in self.genre_links.keys():
            self.genre.append(key)