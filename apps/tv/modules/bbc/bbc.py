import mc, re, os, sys
sys.path.append(os.path.join(mc.GetApp().GetAppDir(), 'libs'))
import ba, md5, time, base64
from beautifulsoup.BeautifulSoup import BeautifulSoup
from urllib import quote_plus
import datetime, time

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
        self.genre_links = {"Children's":"childrens", "Comedy":"comedy", "Drama":"drama", "Entertainment":"entertainment", "Factual":"factual", "Films":"films", "Learning":"learning", "Lifestyle and Leisure":"lifestyle_and_leisure", "Music":"music", "News":"news", "Religion and Ethics":"religion_and_ethics", "Sport":"sport", "Northern Ireland":"northern_ireland", "Scotland":"scotland", "Wales":"wales", "Audio Described":"audiodescribed", "Sign Zone":"signed"}
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
        url = self.url_base + '/iplayer/search?q=' + quote_plus(stream_id)
        data = ba.FetchUrl(url, 3600)

        if data == "":
            mc.ShowDialogNotification("No episode found for " + str(stream_name))
            episodelist = list()
            return episodelist

        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        div_show = soup.find( 'ul', {'class' : 'result-list listview episodelist'})

        episodelist = list()
        for info in div_show.findAll(lambda tag: tag.name == 'li' and not tag.attrs) + div_show.findAll('li',{'class':'audio'}):
            link = info.findAll('a')
            if len(link) > 1:
                title = link[1]['title'].split(': ')
                if len(title) > 2:
                    date = title[2]
                else:
                    date = ''
                episode = ba.CreateEpisode()
                episode.SetName(title[0])
                episode.SetId(self.url_base + link[1]['href'])
                episode.SetDescription(str(info.find('p', {'class':'additional'}).contents[0] + ' - ' + info.find('p', {'class':'episode-synopsis'}).contents[0]).replace('\n','').replace('\t',''))
                episode.SetThumbnails(str(link[0].img['src'][:-11] + "_314_176.jpg"))
                episode.SetDate(date)
                episode.SetPage(page)
                episode.SetTotalpage(totalpage)
                episodelist.append(episode)

        return episodelist

    def Genre(self, genre, filter, page, totalpage):
        url = self.url_base + '/iplayer/tv/categories/' + self.genre_links[genre] + '?sort=dateavailable&page=' + str(page)
        data = ba.FetchUrl(url, 3600)

        if data == "":
            mc.ShowDialogNotification("No episode found for " + str(genre))
            genrelist = list()
            return genrelist

        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        if totalpage == "":
            try:
                pagediv = soup.findAll( 'div', {'class' : 'pagination-control'})[0]
                apage = pagediv.findAll("li")
                totalpage = int(len(apage))
            except:
                totalpage = 1


        div_show = soup.find( 'ul', {'class' : 'listview episodelist'})

        genrelist = list()
        for info in div_show.findAll(lambda tag: tag.name == 'li' and not tag.attrs) + div_show.findAll('li',{'class':'multi-episode'}):
            link = info.findAll('a')

            if len(link) > 1:
                title = link[1]['title'].split(': ')
                if len(title) > 1:
                    filters = title[1]
                    if len(title) > 2:
                        date = title[2]
                    else:
                        date = ''
                else:
                    filters = ''
                genreitem = ba.CreateEpisode()
                genreitem.SetName(title[0])
                genreitem.SetId(self.url_base + link[1]['href'])
                genreitem.SetDescription(str(info.find('p', {'class':'episode-synopsis'}).contents[0]).replace('\n','').replace('\t',''))
                genreitem.SetThumbnails(str(link[0].img['src'][:-11] + "_314_176.jpg"))
                genreitem.SetDate(filters)
                genreitem.SetFilter(date)
                genreitem.SetPage(page)
                genreitem.SetTotalpage(totalpage)
                genrelist.append(genreitem)

        return genrelist

    def Play(self, stream_name, stream_id, subtitle):
        #data = ba.FetchUrl(stream_id)
        #data = re.compile('emp.setPid\("(.*?)\)', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
        #pid = re.compile('", "(.*?)"', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
        
        #surl = 'http://www.bbc.co.uk/mediaselector/4/mtis/stream/' + pid
        
        #bitrate = []
        #data = ba.FetchUrl(surl)
        #soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
        #for info in soup.findAll('media', {'bitrate':True}):
        #   bitrate.append(int(info['bitrate']))
        #bitrate.sort()
        #max = str(bitrate[-1])
        
        #media = soup.find('media', {'bitrate':max})
        #connection = media.find('connection', {'supplier':'limelight'})

        #identifier  = connection['identifier']
        #server      = connection['server']
        #supplier    = connection['supplier']
        #try:
        #    auth    = connection['authString']
        #except:
        #    auth    = connection['authstring']
        # not always listed for some reason
        #try:
        #    application = connection['application']
        #except:
        #    application = 'live'

        #if subtitle:
        #    sub_url = soup.find('media', {'kind':'captions'})
        #    sub_url = sub_url.connection['href']

        play = ba.CreatePlay()
        play.SetPath(quote_plus(stream_id))
        play.SetDomain('bbc.co.uk')
        if subtitle:
            play.SetJSactions(quote_plus('http://bartsidee.nl/boxee/apps/bbc1.js'))
        else:
            play.SetJSactions(quote_plus('http://bartsidee.nl/boxee/apps/bbc0.js'))
        return play

    def Categories(self):
        for key in self.genre_links.keys():
            self.genre.append(key)