import mc, re, os, sys
sys.path.append(os.path.join(mc.GetApp().GetAppDir(), 'libs'))
import ba
from beautifulsoup.BeautifulSoup import BeautifulSoup
import simplejson as json
from urllib import quote_plus


class Module(object):
    def __init__(self):
        self.name = "TVNZ Ondemand"             #Name of the channel
        self.type = ['list']           #Choose between 'search', 'list', 'genre'
        self.episode = True                     #True if the list has episodes
        self.filter = []                        #Option to set a filter to the list
        self.genre = {}                         #Array to add a genres to the genre section [type genre must be enabled]
        self.content_type = ''                  #Mime type of the content to be played
        self.country = 'NZ'                     #2 character country id code
        
        self.url_base = 'http://tvnz.co.nz'
        
    def List(self):
        url = self.url_base + '/content/ta_ent_video_shows_group/ta_ent_programme_result_module_skin.xinc'
        data = ba.FetchUrl(url)
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        streamlist = list()
        for info in soup.findAll('a'):
            if info['href'] != '#':
                stream = ba.CreateStream()
                stream.SetName(info['title'])
                stream.SetId(info['href'])
                streamlist.append(stream)

        return streamlist
    
    def Episode(self, stream_name, stream_id, page, totalpage):

        url = self.url_base + stream_id
        data = ba.FetchUrl(url, 3600)
        soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

        episodelist = list()
        if data < 20:
            mc.ShowDialogNotification("No episode found for " + str(stream_name))
            return episodelist

        try:
            episodes = soup.findAll( 'div', {'id' : 'slidefullepisodes'})[0]
        except:
            return episodelist


        for info in episodes.findAll('li'):
            detail = info.findAll('a')[2]
            title = info.findAll('a')[1]
            #airtime = info.find('div', {'class' : 'time'})
            #print airtime.contents[0]
            thumb = info.findAll('img')[1]
            episodenr = info.find('strong')
            link = title['href'].split('-')
            linkid = link.pop()

            episode = ba.CreateEpisode()
            episode.SetName(title['title'])
            episode.SetId(linkid)
            episode.SetDescription(detail['title'])
            episode.SetThumbnails(thumb['src'])
            episode.SetDate(episodenr.contents[0])
            episode.SetPage(page)
            episode.SetTotalpage(totalpage)
            episodelist.append(episode)

        return episodelist
        
    def Play(self, stream_name, stream_id, subtitle):
        url = self.url_base + '/content/'+stream_id+'/ta_ent_smil_skin.smil'
        data = ba.FetchUrl(url)
 

        return play

   