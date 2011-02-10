import mc, re, os, sys
sys.path.append(os.path.join(mc.GetApp().GetAppDir(), 'libs'))
import ba

import simplejson as json
from beautifulsoup.BeautifulSoup import BeautifulSoup
from urllib import quote_plus
from itertools import izip


class Module(object):
    def __init__(self):
        self.name = "Youtube"                       #Name of the channel
        self.type = ['search']                      #Choose between 'search', 'list', 'genre'
        self.episode = True                         #True if the list has episodes
        self.filter = []                            #Option to set a filter to the list
        self.genre = []                             #Array to add a genres to the genre section [type genre must be enabled]
        self.content_type = 'video/x-flv'           #Mime type of the content to be played
        self.country = ''                           #2 character country id code
        
        self.url_base = 'http://gdata.youtube.com'

         
    def Search(self, search):
        url = 'http://suggestqueries.google.com/complete/search?client=youtube&jsonp=yt&q=' + quote_plus(search)
        data = ba.FetchUrl(url, 0)
        data = re.compile('yt\((.*?)\)$', re.DOTALL + re.IGNORECASE).search(data).group(1)
        json_data = json.loads(data)

        streamlist = list()
        for info in json_data[1]:
            stream = ba.CreateStream()
            stream.SetName(info[0])
            stream.SetId(info[0])
            streamlist.append(stream)

        return streamlist

    def Episode(self, show_name, show_id, page, totalpage):
        url = self.url_base + '/feeds/api/videos?q=' + quote_plus(show_id) + '&start-index=1&max-results=20&format=5&orderby=viewCount'
        data = ba.FetchUrl(url, 0)
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        title = []
        path = []
        thumb = []
        desc = []
        pup = []
        for info in soup.findAll('title'):
            tmp_name = info.contents[0]
            title.append(tmp_name)

        for info in soup.findAll('media:content', {'isdefault' : 'true'}):
            tmp_id = info['url']  + '&fmt=22'
            path.append(tmp_id)

        for info in soup.findAll('media:thumbnail', {'height' : '240'}):
            tmp_thumb = info['url']
            thumb.append(tmp_thumb)
        
        for info in soup.findAll('content'):
            tmp_desc = info.contents[0]
            desc.append(tmp_desc)
        
        for info in soup.findAll('published'):
            tmp_pub = info.contents[0][0:10]
            pup.append(tmp_pub)


        title.pop(0)

        episodelist = list()
        for title_i,path_i,thumb_i,desc_i,pup_i in izip(title,path,thumb,desc,pup):
            episode = ba.CreateEpisode()
            episode.SetName(title_i)
            episode.SetId(path_i)
            episode.SetDescription(desc_i)
            episode.SetThumbnails(thumb_i)
            episode.SetDate(pup_i)
            episode.SetPage(page)
            episode.SetTotalpage(totalpage)
            episodelist.append(episode)

        return episodelist
        
    def Play(self, stream_name, stream_id, subtitle):

        play = ba.CreatePlay()
        play.SetPath(stream_id)
        play.SetDomain('youtube.com')
        play.SetJSactions('')

        return play
   