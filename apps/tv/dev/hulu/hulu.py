import mc, re, os, sys
sys.path.append(os.path.join(mc.GetApp().GetAppDir(), 'libs'))
import ba, time
from beautifulsoup.BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from urllib import quote_plus

path = os.path.join(mc.GetApp().GetAppDir(), 'libs')
sys.path.append(path)

import binascii
import md5
import base64
from array import array
from crypto.cipher.aes import AES
import math
import hmac
import operator

import urllib2
import cookielib


xmldeckeys = [
             ['4878B22E76379B55C962B18DDBC188D82299F8F52E3E698D0FAF29A40ED64B21', 'WA7hap7AGUkevuth'],
             ['246DB3463FC56FDBAD60148057CB9055A647C13C02C64A5ED4A68F81AE991BF5', 'vyf8PvpfXZPjc7B1'],
             ['8CE8829F908C2DFAB8B3407A551CB58EBC19B07F535651A37EBC30DEC33F76A2', 'O3r9EAcyEeWlm5yV'],
             ['852AEA267B737642F4AE37F5ADDF7BD93921B65FE0209E47217987468602F337', 'qZRiIfTjIGi3MuJA'],
             ['76A9FDA209D4C9DCDFDDD909623D1937F665D0270F4D3F5CA81AD2731996792F', 'd9af949851afde8c'],
             ['1F0FF021B7A04B96B4AB84CCFD7480DFA7A972C120554A25970F49B6BADD2F4F', 'tqo8cxuvpqc7irjw'],
             ['3484509D6B0B4816A6CFACB117A7F3C842268DF89FCC414F821B291B84B0CA71', 'SUxSFjNUavzKIWSh'],
             ['B7F67F4B985240FAB70FF1911FCBB48170F2C86645C0491F9B45DACFC188113F', 'uBFEvpZ00HobdcEo'],
             ['40A757F83B2348A7B5F7F41790FDFFA02F72FC8FFD844BA6B28FD5DFD8CFC82F', 'NnemTiVU0UA5jVl0']
             ]

subdeckeys = [
             ['4878B22E76379B55C962B18DDBC188D82299F8F52E3E698D0FAF29A40ED64B21', 'WA7hap7AGUkevuth']
             ]

smildeckeys = [
             ['40A757F83B2348A7B5F7F41790FDFFA02F72FC8FFD844BA6B28FD5DFD8CFC82F', 'NnemTiVU0UA5jVl0']
             ]



class Module(object):
    def __init__(self):
        self.name = "Hulu"                   #Name of the channel
        self.type = ['search']                      #Choose between 'search', 'list', 'genre'
        self.episode = True                         #True if the list has episodes
        self.filter = []                            #Option to set a filter to the list
        self.genre = []                             #Array to add a genres to the genre section [type genre must be enabled]
        self.content_type = ''           #Mime type of the content to be played
        self.country = 'US'                         #2 character country id code

        self.COOKIEFILE = os.path.join(mc.GetTempDir(),'hulu-cookies.lwp')
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

        url = self.url_base + "/videos/season_expander?order=desc&page=1&season_number=" + str(pp[intpage]) + "&show_id=" + str(show_id) + "&sort=season&video_type=episode"

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
        #path = self.tinyurl(stream_id)
        #play = ba.CreatePlay()
        #play.SetPath(quote_plus(path))
        #play.SetDomain('bartsidee.nl')
        #play.SetJSactions(quote_plus('http://bartsidee.nl/boxee/apps/js/hulu.js'))

        #grab eid from failsafe url
        html = ba.FetchUrl(stream_id)
        p=re.compile('content_id", (.+?)\);')
        ecid=p.findall(html)[0]
        pid = ecid

        if subtitle: self.checkCaptions(pid)

        #getSMIL
        try:
            #smilURL = "http://s.hulu.com/select.ashx?pid=" + pid + "&auth=" + self.pid_auth(pid) + "&v=713434170&np=1&pp=hulu&dp_id=hulu&cb=499"
            smilURL = 'http://s.hulu.com/select?video_id=' + pid + '&v=850037518&ts=1294866343&np=1&vp=1&pp=hulu&dp_id=hulu&bcs=' + self.content_sig(pid)
            print 'HULU --> SMILURL: ' + smilURL
            smilXML = ba.FetchUrl(smilURL)
            tmp = self.decrypt_SMIL(smilXML)
            smilSoup = BeautifulStoneSoup(tmp, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
            print smilSoup.prettify()
        except:
            print "error retreiving smil"
            return

        #getRTMP
        video=smilSoup.findAll('video')
        streams=[]
        selectedStream = None
        cdn = None
        qtypes=['ask', 'p011', 'p010', 'p008', 'H264 Medium', 'H264 650K', 'H264 400K', 'High', 'Medium','Low']
        #label streams
        qt = 4
        if qt < 0 or qt > 9: qt = 0
        while qt < 9:
            qtext = qtypes[qt]
            for vid in video:
                #if qt == 0:
                streams.append([vid['profile'],vid['cdn'],vid['server'],vid['stream'],vid['token']])
                if qt > 6 and 'H264' in vid['profile']: continue
                if qtext in vid['profile']:
                    if vid['cdn'] == 'akamai':
                        selectedStream = [vid['server'],vid['stream'],vid['token']]
                        print selectedStream
                        cdn = vid['cdn']
                        break

            if qt == 0 or selectedStream != None: break
            qt += 1

        if selectedStream != None:
            #form proper streaming url
            server = selectedStream[0]
            stream = selectedStream[1]
            token = selectedStream[2]

            protocolSplit = server.split("://")
            pathSplit = protocolSplit[1].split("/")
            hostname = pathSplit[0]
            appName = protocolSplit[1].split(hostname + "/")[1]

            if "level3" in cdn:
                appName += "?" + token
                stream = stream[0:len(stream)-4]
                newUrl = server + " app=" + appName

            elif "limelight" in cdn:
                appName += '?' + token
                stream = stream[0:len(stream)-4]
                newUrl = server + '?' + token + " app=" + appName

            elif "akamai" in cdn:
                appName += '?' + token
                newUrl = server + '?' + token
                #newUrl = server + "?_fcs_vhost=" + hostname + "&" + token

            else:
                #xbmcgui.Dialog().ok('Unsupported Content Delivery Network',cdn+' is unsupported at this time')
                return

            print "item url -- > " + newUrl
            print "app name -- > " + appName
            print "playPath -- > " + stream

            #define item
            SWFPlayer = 'http://www.hulu.com/site-player/86070/player.swf'
            #newUrl += " playpath=" + stream + " swfurl=" + SWFPlayer

            #newUrl += " swfvfy=true"
            playPath = stream
            rtmpURL = newUrl
            authPath = ''

            play = ba.CreatePlay()
            play.SetContent_type('video/x-flv')
            play.SetRTMPPath(playPath)
            play.SetRTMPDomain(rtmpURL)
            play.SetRTMPAuth(authPath)
            play.SetRTMPSwf(SWFPlayer)
            print "finish"
            return play

    def tinyurl(self, params):
        url = "http://tinyurl.com/api-create.php?url=" + str(params)
        return ba.FetchUrl(url)

    def GetThumb(self, id):
        url = self.url_base + "/videos/info/" + str(id)
        data = ba.FetchUrl(url,0,True)
        try:
            return re.compile('"thumbnail_url":"(.*?)"', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
        except:
            try:
                return re.compile('"thumbnail_url": "(.*?)"', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
            except:
                return str('')





    #Source from Git
    def decrypt_cid(self, p):
        cidkey = '48555bbbe9f41981df49895f44c83993a09334d02d17e7a76b237d04c084e342'
        v3 = binascii.unhexlify(p)
        print v3
        ecb = AES(binascii.unhexlify(cidkey))
        print ecb
        print ecb.decrypt(v3)
        return ecb.decrypt(v3).split("~")[0]

    def cid2eid(self, p):
        dec_cid = int(p.lstrip('m'), 36)
        xor_cid = dec_cid ^ 3735928559
        m = md5.new()
        m.update(str(xor_cid) + "MAZxpK3WwazfARjIpSXKQ9cmg9nPe5wIOOfKuBIfz7bNdat6gQKHj69ZWNWNVB1")
        value = m.digest()
        return base64.encodestring(value).replace("+", "-").replace("/", "_").replace("=", "")

    def decrypt_pid(self, p):
        cp_strings = [
            '6fe8131ca9b01ba011e9b0f5bc08c1c9ebaf65f039e1592d53a30def7fced26c',
            'd3802c10649503a60619b709d1278ffff84c1856dfd4097541d55c6740442d8b',
            'c402fb2f70c89a0df112c5e38583f9202a96c6de3fa1aa3da6849bb317a983b3',
            'e1a28374f5562768c061f22394a556a75860f132432415d67768e0c112c31495',
            'd3802c10649503a60619b709d1278efef84c1856dfd4097541d55c6740442d8b'
        ]

        v3 = p.split("~")
        v3a = binascii.unhexlify(v3[0])
        v3b = binascii.unhexlify(v3[1])

        ecb = AES(v3b)
        tmp = ecb.decrypt(v3a)

        for v1 in cp_strings[:]:
            ecb = AES(binascii.unhexlify(v1))
            v2 = ecb.decrypt(tmp)
            if (re.match("[0-9A-Za-z_-]{32}", v2)):
                return v2

    def pid_auth(self, pid):
        m=md5.new()
        m.update(str(pid) + "yumUsWUfrAPraRaNe2ru2exAXEfaP6Nugubepreb68REt7daS79fase9haqar9sa")
        return m.hexdigest()

    def content_sig(self, pid):
        hmac_key = 'f6daaa397d51f568dd068709b0ce8e93293e078f7dfc3b40dd8c32d36d2b3ce1'
        parameters = {'video_id' : pid,
                      'v' : '850037518',
                      'ts' : '1294866343',
                      'np' : '1',
                      'vp' : '1',
                      'pp' : 'hulu',
                      'dp_id' : 'hulu'}
        sorted_parameters = sorted(parameters.iteritems(), key=operator.itemgetter(0))
        data = ''
        for item1, item2 in sorted_parameters:
            data += item1 + item2
        sig = hmac.new(hmac_key, data)
        return sig.hexdigest()

    def decrypt_SMIL(self, encsmil):
        encdata = binascii.unhexlify(encsmil)

        for key in smildeckeys[:]:
            smil=""
            out=[0,0,0,0]
            ecb = AES(binascii.unhexlify(key[0]))
            unaes = ecb.decrypt(encdata)

            xorkey = array('i',key[1])

            for i in range(0, len(encdata)/16):
                x = unaes[i*16:i*16+16]
                res = array('i',x)
                for j in range(0,4):
                    out[j] = res[j] ^ xorkey[j]
                x = encdata[i*16:i*16+16]
                xorkey = array('i',x)
                a=array('i',out)
                x=a.tostring()
                smil = smil + x

            if (smil.find("<smil") == 0):
                print key
                i = smil.rfind("</smil>")
                smil = smil[0:i+7]
                return smil

    def decrypt_subs(self, encsubs):
        encdata = binascii.unhexlify(encsubs)

        for key in subdeckeys[:]:
            subs=""
            out=[0,0,0,0]
            ecb = AES(binascii.unhexlify(key[0]))
            unaes = ecb.decrypt(encdata)
            xorkey = array('i',key[1])

            for i in range(0, len(encdata)/16):
                x = unaes[i*16:i*16+16]
                res = array('i',x)
                for j in range(0,4):
                    out[j] = res[j] ^ xorkey[j]
                x = encdata[i*16:i*16+16]
                xorkey = array('i',x)
                a=array('i',out)
                x=a.tostring()
                subs += x

            substart = subs.find("<P")

            if (substart > -1):
                print key
                i = subs.rfind("</P>")
                subs = subs[substart:i+4]
                return subs

    def clean_subs(self, data):
        br = re.compile(r'<br.*?>')
        tag = re.compile(r'<.*?>')
        space = re.compile(r'\s\s\s+')
        sub = br.sub('\n', data)
        sub = tag.sub(' ', sub)
        sub = space.sub(' ', sub)
        return sub

    def convert_time(self, seconds):
        hours = seconds / 3600
        seconds -= 3600*hours
        minutes = seconds / 60
        seconds -= 60*minutes
        return "%02d:%02d:%02d" % (hours, minutes, seconds)

    def convert_subtitles(self, subtitles, output):
        subtitle_data = subtitles
        subtitle_data = subtitle_data.replace("\n","").replace("\r","")
        subtitle_data = BeautifulStoneSoup(subtitle_data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        subtitle_array = []
        srt_output = ''

        print "HULU: --> Converting subtitles to SRT"
        heading = 'Subtitles'
        message = 'Converting subtitles'
        duration = 4000
        #xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )
        lines = subtitle_data.findAll('sync') #split the file into lines
        for line in lines:
            if(line['encrypted'] == 'true'):
                sub = self.decrypt_subs(line.string)
                sub = self.clean_subs(sub)
                sub = unicode(BeautifulStoneSoup(sub,convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0]).encode( "utf-8" )

            else:
                sub = unicode(BeautifulStoneSoup(sub,convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0]).encode( "utf-8" )

            begin_time = int(line['start'])
            seconds = int(math.floor(begin_time/1000))
            milliseconds = int(begin_time - (seconds * 1000))
            timestamp = self.convert_time(seconds)
            timestamp = "%s,%03d" % (timestamp, milliseconds)

            index = len(subtitle_array)-1
            if(index > -1 and subtitle_array[index]['end'] == None):
                millsplit = subtitle_array[index]['start'].split(',')
                itime = millsplit[0].split(':')
                start_seconds = (int(itime[0])*60*60)+(int(itime[1])*60)+int(itime[2])
                end_seconds = start_seconds + 4
                if end_seconds < seconds:
                    endmilliseconds = int(millsplit[1])
                    endtimestamp = self.convert_time(end_seconds)
                    endtimestamp = "%s,%03d" % (endtimestamp, endmilliseconds)
                    subtitle_array[index]['end'] = endtimestamp
                else:
                    subtitle_array[index]['end'] = timestamp

            if sub != '&#160; ':
                sub = sub.replace('&#160;', ' ')
                temp_dict = {'start':timestamp, 'end':None, 'text':sub}
                subtitle_array.append(temp_dict)

        for i, subtitle in enumerate(subtitle_array):
            line = str(i+1)+"\n"+str(subtitle['start'])+" --> "+str(subtitle['end'])+"\n"+str(subtitle['text'])+"\n\n"
            srt_output += line

        file = open(os.path.join(os.getcwd().replace(';', ''),'resources','cache',output+'.srt'), 'w')
        file.write(srt_output)
        file.close()
        print "HULU: --> Successfully converted subtitles to SRT"
        heading = 'Subtitles'
        message = 'Conversion Complete'
        duration = 4000
        #xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )
        return True

    def checkCaptions(self, pid):
        url = 'http://www.hulu.com/captions?content_id='+pid
        html = ba.FetchUrl(url)
        capSoup = BeautifulStoneSoup(html)
        hasSubs = capSoup.find('en')
        heading = 'Subtitles'
        if(hasSubs):
            print "HULU --> Grabbing subtitles..."
            message = 'Grabbing subtitles...'
            duration = 4000
            #xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )
            html=ba.FetchUrl(hasSubs.string)
            ok = self.convert_subtitles(html,pid)
            if ok:
                print "HULU --> Subtitles enabled."
            else:
                print "HULU --> There was an error grabbing the subtitles."
                message = 'Error grabbing subtitles.'
                duration = 4000
                #xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )
        else:
            print "HULU --> No subtitles available."
            message = 'No subtitles available.'
            duration = 4000
            #xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) ) "")

