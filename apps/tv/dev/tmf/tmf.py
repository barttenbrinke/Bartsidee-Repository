import mc, re, os, sys
sys.path.append(os.path.join(mc.GetApp().GetAppDir(), 'libs'))
import ba, md5, time, base64
from beautifulsoup.BeautifulSoup import BeautifulSoup
from urllib import quote

class Module(object):
    def __init__(self):
        self.name = "TMF Music"                   #Name of the channel
        self.type = ['search']                      #Choose between 'search', 'list', 'genre'
        self.episode = False                         #True if the list has episodes
        self.filter = []                            #Option to set a filter to the list
        self.genre = []                             #Array to add a genres to the genre section [type genre must be enabled]
        self.content_type = 'video/x-flv'           #Mime type of the content to be played
        self.country = 'NL'                         #2 character country id code
        
        self.url_base = 'http://www.tmf.nl'

    def Search(self, search):
        url = self.url_base + '/script/common/ajax_zoek.php'
        params = 'keyword='+ quote(search)
        data = ba.FetchUrl(url, 0, False, params)

        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        streamlist = list()
        for info in soup.findAll('li'):
            title = re.compile('---(.*?)$', re.DOTALL + re.IGNORECASE).search(str(info.span.contents[0])[4:]).group(1)
            id = re.compile('---(.*?)---', re.DOTALL + re.IGNORECASE).search(str(info.span.contents[0])).group(1)
            stream = ba.CreateStream()
            stream.SetName(title)
            stream.SetId(id)
            streamlist.append(stream)
        return streamlist

    def Play(self, stream_name, stream_id, subtitle):
        url = 'http://www.tmf.nl/xml/videoplayer/mediaGen.php?id='+stream_id
        data = ba.FetchUrl(url)
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        bitrate = []
        for info in soup.findAll('rendition', {'bitrate':True}):
            bitrate.append(int(info['bitrate']))
        bitrate.sort()
        max = str(bitrate[-1])

        rendition = soup.find('rendition', {'bitrate':max})
        path = rendition.src.contents[0]
        print path
        rtmplist = path.split('ondemand/')
        filepath = rtmplist[1].split('.flv')
        print filepath

        play = ba.CreatePlay()
        playPath =  filepath[0]
        rtmpURL = rtmplist[0] + 'ondemand'
        authPath = ''

        play.SetRTMPPath(playPath)
        play.SetRTMPDomain(rtmpURL)
        play.SetRTMPAuth(authPath)
        return play
