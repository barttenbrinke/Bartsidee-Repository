import mc, re, os, sys
sys.path.append(os.path.join(mc.GetApp().GetAppDir(), 'libs'))
import ba
from urllib import quote_plus
from urllib2 import *
import csv

class Module(object):
    def __init__(self):
        self.name = "Navi-X"                        #Name of the channel
        self.type = ['search', 'genre']             #Choose between 'search', 'list', 'genre'
        self.episode = False                         #True if the list has episodes
        self.filter = []                            #Option to set a filter to the list
        self.genrelist = {'Top 24h':'day', 'Top Week':'week', 'Newest':'new', 'Updated':'update'}
        self.genre = self.genrelist.keys()           #Array to add a genres to the genre section [type genre must be enabled]
        self.content_type = ''                      #Mime type of the content to be played
        self.country = ''                           #2 character country id code
        
        self.url_base = 'http://navix.turner3d.net'
        self.support = {'video': 'V: ', 'audio': 'A: ', 'playlist':'P: '}

    def Search(self, search):
        url = self.url_base + '/playlist/search/' + quote_plus(search)
        data = self.ParsePlaylist(url, 60)

        streamlist = list()
        if len(data) < 1:
            return streamlist
        
        for item in data:
            if ("type" and "URL") in item.keys():
                if item['type'] in self.support.keys():
                    stream = ba.CreateStream()
                    stream.SetName(self.support[item['type']] + re.sub("(\[.*?\])", '', item['name']))
                    if item['type'] == 'playlist':
                        stream.SetId(item['URL'])
                        stream.SetEpisode("True")
                    else:
                        try: stream.SetId(item['URL'] + '|' + item['processor'])
                        except: stream.SetId(item['URL'])
                    streamlist.append(stream)

        return streamlist
    
    def Episode(self, stream_name, stream_id, page, totalpage):
        data = self.ParsePlaylist(stream_id)

        episodelist = list()
        if len(data) < 1:
            mc.ShowDialogNotification("1. No episode found for " + str(stream_name))
            return episodelist

        for item in data:
            if ("type" and "URL" and "thumb") in item.keys():
                keys = self.support.keys()
                if item['type'] in keys:
                    episode = ba.CreateEpisode()
                    episode.SetName(self.support[item['type']] + re.sub("(\[.*?\])", '', item['name']))
                    episode.SetThumbnails(item['thumb'])
                    try: episode.SetDescription(item['description'])
                    except: """"""
                    if item['type'] == 'playlist':
                        episode.SetEpisode("True")
                        episode.SetId(item['URL'])
                    else:
                        try: episode.SetId(item['URL'] + '|' + item['processor'])
                        except: episode.SetId(item['URL'])
                    episode.SetPage(page)
                    episode.SetTotalpage(totalpage)
                    episodelist.append(episode)

        if len(episodelist) < 1 :
            mc.ShowDialogNotification("No nested playlists supported: " + str(stream_name))
            return

        return episodelist

    def Genre(self, genre, filter, page, totalpage):
        url = self.url_base + '/playlist/' + self.genrelist[genre] + '.plx?page=' + str(page)
        data = self.ParsePlaylist(url)

        genrelist = list()
        if len(data) < 1:
            mc.ShowDialogNotification("No data found for " + str(genre))
            return episodelist

        totalpage = 10

        for item in data:
            if ("type" and "URL") in item.keys():
                if item['type'] in self.support.keys():
                    genreitem = ba.CreateEpisode()
                    genreitem.SetName(self.support[item['type']] + re.sub("(\[.*?\])", '', item['name']))
                    if item['type'] == 'playlist':
                        genreitem.SetEpisode("True")
                        genreitem.SetId(item['URL'])
                    else:
                        try: genreitem.SetId(item['URL'] + '|' + item['processor'])
                        except: genreitem.SetId(item['URL'])
                    genreitem.SetPage(page)
                    genreitem.SetTotalpage(totalpage)
                    genrelist.append(genreitem)

        if len(genrelist) < 1 :
            mc.ShowDialogNotification("No data found for " + str(genre)[3:])
        #genrelist.pop()

        return genrelist

    def Play(self, stream_name, stream_id, subtitle):
        path = self.GetPath(stream_id)
        play = ba.CreatePlay()
        if 'youtube.com' in path:
            play.SetPath(path)
            play.SetDomain('youtube.com')
            play.SetJSactions('')
            play.SetContent_type('video/x-flv')
        elif 'http' in path:
            play.SetPath(path)
        elif 'mms' in path:
            play.SetPath(path)
        elif 'rtmp' in path:
            play.SetPath(path)
        else:
            mc.ShowDialogNotification("Data format currently not supported")
            play.SetPath('')
        return play

    def ParsePlaylist(self, url, max=False):
        data = csv.reader(urlopen(url), delimiter="=", quoting=csv.QUOTE_NONE, quotechar='|')
        if max != 0: number = max
        else: number = 10000

        item = {}
        datalist = []
        for i, line in enumerate(data):
            if i < number:
                if line == [] or line == ['#']:
                    if item: datalist.append(item)
                    item = {}
                else:
                    if len(line) == 2:
                        item[line[0]] = line[1]
                    elif len(line) == 3:
                        item[line[0]] = line[1] + '=' + line[2]
                    elif len(line) > 3:
                        total = len(line) -2
                        item[line[0]] = line[1]
                        for i in range(2,total):
                            item[line[0]] = item[line[0]] + '=' + line[i]
            else:
                break
        return datalist

    def ParseProcessor(self, url):
        data = csv.reader(urlopen(url), delimiter="'", quoting=csv.QUOTE_NONE, quotechar='|')

        datalist = {}
        keys = []
        for i, line in enumerate(data):
            if line:
                if len(line) == 1:
                    datalist[i] = line[0]
                if len(line) == 2:
                    if line[0] not in keys:
                        datalist[line[0]] = line[1]
                        keys.append(line[0])
        return datalist

    def GetPath(self, stream_id):
        if len(stream_id.split('|')) > 1:
            urlpart = stream_id.split('|')
            url = urlpart[1] + '?url=' + urlpart[0]
            data = self.ParseProcessor(url)
            keys = data.keys()

            if len(data) < 2:
                return

            try:
                if data[0] == 'v2':
                    id = 1
            except:
                """"""

            try:
                if 'http' in data[0]:
                    id = 2
            except:
                """"""

            if id == 1:
                id_url = ''
                id_cookie = ''
                id_regex = ''
                id_postdata = ''

                if 's_url=' in keys: id_url = data['s_url=']
                if 's_cookie=' in keys: id_cookie = data['s_cookie=']
                if 'regex=' in keys: id_regex = data['regex=']
                if 's_postdata=' in keys: id_postdata = data['s_postdata=']
                if not id_url: id_url = urlpart[0]

                data = ba.FetchUrl(str(id_url), 0, False, str(id_postdata), str(id_cookie))

                try:
                    path = re.compile(str(id_regex), re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
                except:
                    path = ""


            elif id == 2:
                id_url = data[0]
                id_regex = data[1]
                data = ba.FetchUrl(str(id_url))

                try:
                    path = re.compile(str(id_regex), re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
                except:
                    path = ""

            else:
                path = ""
        else:
            path = stream_id

        return path