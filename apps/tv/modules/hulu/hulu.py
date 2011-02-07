import mc, re, os, sys
sys.path.append(os.path.join(mc.GetApp().GetAppDir(), 'libs'))
import ba, md5, time, base64
from beautifulsoup.BeautifulSoup import BeautifulSoup
from urllib import quote_plus

class Module(object):
    def __init__(self):
        self.name = "Hulu"                   #Name of the channel
        self.type = ['search']                      #Choose between 'search', 'list', 'genre'
        self.episode = True                         #True if the list has episodes
        self.filter = []                            #Option to set a filter to the list
        self.genre = []                             #Array to add a genres to the genre section [type genre must be enabled]
        self.content_type = 'video/x-flv'           #Mime type of the content to be played
        self.country = 'US'                         #2 character country id code
        
        self.url_base = 'http://www.hulu.com'

    def Search(self, search):
        url = self.url_base + '/browse/search?alphabet=All&family_friendly=0&closed_captioned=0&has_free=1&has_huluplus=0&has_hd=0&channel=All&subchannel=&network=All&display=Shows%20with%20full%20episodes%20only&decade=All&type=tv&view_as_thumbnail=false&block_num=0&keyword=' + quote_plus(search)
        data = ba.FetchUrl(url)

        data = re.compile('"show_list", "(.*?)"\)', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
        data = data.replace('\\u003c','<').replace('\\u003e','>').replace('\\','').replace('\\n','').replace('\\t','')
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        streamlist = list()
        for info in soup.findAll('a', {'onclick':True}):
            stream = ba.CreateStream()
            stream.SetName(info.contents[0])
            stream.SetId(info['href'])
            streamlist.append(stream)

        return streamlist
    
    def Episode(self, stream_name, stream_id, page, totalpage):
        data = ba.FetchUrl(stream_id, 3600)

        if data == "":
            mc.ShowDialogNotification("No episode found for " + str(stream_name))
            return ba.CreateEpisode()

        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
        totalpage = len(soup.findAll('tr', 'srh'))

        try:
            episode_url = re.compile('VideoExpander.subheadingClicked\((.*?)\)"', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
        except:
            mc.ShowDialogNotification("No episode found for " + str(stream_name))
            return ba.CreateEpisode()

        season_number = re.compile('season_number=(.*?)\&', re.DOTALL + re.IGNORECASE).search(str(episode_url)).group(1)
        show_id = re.compile('show_id=(.*?)\&', re.DOTALL + re.IGNORECASE).search(str(episode_url)).group(1)

        pp = []
        for i in range(0,totalpage):
            pp.append(str(int(season_number) - i))
        intpage = int(page) - 1

        url = "http://www.hulu.com/videos/season_expander?order=desc&page=1&season_number=" + str(pp[intpage]) + "&show_id=" + str(show_id) + "&sort=season&video_type=episode"

        data = ba.FetchUrl(url)
        data = re.compile('srh-bottom-' + pp[intpage] +'", "(.*?)"\);', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
        data = data.replace('\\u003c','<').replace('\\u003e','>').replace('\\','')
        soup = BeautifulSoup(data)

        episodelist = list()
        name = []
        link = []
        number = []
        thumb = []
        for tmp in soup.findAll('td', {'class':'c0'}):
            number.append(tmp.contents[0])

        i = 0
        b = 0
        for tmp in soup.findAll('td', {'class':'c1'}):
            name.append(tmp.a.contents[0])
            link.append(tmp.a['href'])
            try:
                thumb.append(self.GetThumb(re.compile('/watch/(.*?)/', re.DOTALL + re.IGNORECASE).search(str(tmp.a['href'])).group(1)))
            except:
                thumb.append('')
            b += 1
            if len(tmp.findAll('div', 'vex-h')) == 0:
                i += 1

        if i != b: totalpage = page

        for x in range(0,i):
            episode = ba.CreateEpisode()
            episode.SetName(stream_name)
            episode.SetId(link[x])
            episode.SetDescription('Episode: ' + number[x] + ' - '  + name[x])
            episode.SetThumbnails(thumb[x])
            episode.SetDate('Season: ' + pp[intpage])
            episode.SetPage(page)
            episode.SetTotalpage(totalpage)
            episodelist.append(episode)

        return episodelist

    def Play(self, stream_name, stream_id, subtitle):
        path = self.tinyurl(stream_id)
        play = ba.CreatePlay()
        play.SetPath(quote_plus(path))
        play.SetDomain('bartsidee.nl')
        play.SetJSactions(quote_plus('http://bartsidee.nl/boxee/apps/hulu.js'))
        return play

    def tinyurl(self, params):
        url = "http://tinyurl.com/api-create.php?url=" + str(params)
        return ba.FetchUrl(url)

    def GetThumb(self, id):
        url = "http://www.hulu.com/videos/info/" + str(id)
        data = ba.FetchUrl(url,0,True)
        try:
            return re.compile('"thumbnail_url":"(.*?)"', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
        except:
            try:
                return re.compile('"thumbnail_url": "(.*?)"', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
            except:
                return str('')