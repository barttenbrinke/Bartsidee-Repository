import mc, re, os, sys
sys.path.append(os.path.join(mc.GetApp().GetAppDir(), 'libs'))
import ba

import simplejson as json
from beautifulsoup.BeautifulSoup import BeautifulSoup
from urllib import quote_plus, unquote
from itertools import izip


class Module(object):
    def __init__(self):
        self.name = "CBC"                       #Name of the channel
        self.type = ['search']                      #Choose between 'search', 'list', 'genre'
        self.episode = False                         #True if the list has episodes
        self.filter = []                            #Option to set a filter to the list
        self.genre = []                             #Array to add a genres to the genre section [type genre must be enabled]
        self.content_type = 'video/x-flv'           #Mime type of the content to be played
        self.country = 'CA'                           #2 character country id code
        

         
    def Search(self, search):
        url = 'http://www.cbc.ca/search/cbc?json=true&sitesearch=www.cbc.ca/video/watch&q=' + quote_plus(search)
        data = ba.FetchUrl(url, 0)
        json_data = json.loads(data)

        streamlist = list()
        print json_data
        if json_data['searchResults']['numOfResults'] == "":
            return streamlist

        for info in json_data['searchResults']['items']:
            title = unquote(info['title']).replace('&amp;','&').replace('&lt;','<').replace('&gt;','>').replace('&quot;','"').replace('&#39;',"'")
            if title != "CBC.ca Player":
                stream = ba.CreateStream()
                stream.SetName(''.join(BeautifulSoup(title).findAll(text=True)))
                stream.SetId(info['urlEncoded'])
                streamlist.append(stream)

        return streamlist
        
    def Play(self, stream_name, stream_id, subtitle):

        url = "http://tarek.org/cbc/index.php?id="+ stream_id[-10:]
        print str(url)

        play = ba.CreatePlay()
        play.SetPath(url)
        play.SetDomain('www.cbc.ca')
        play.SetJSactions('http://www.bartsidee.nl/boxee/apps/cbc.js')

        return play