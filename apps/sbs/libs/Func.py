# function unescape is made by Fredrik Lundh from effbot.org
import mc
import re, htmlentitydefs
from time import time
from BeautifulSoup import BeautifulSoup
import urllib2

HTTP = mc.Http()
HTTP.SetUserAgent("Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10")

config = mc.GetApp().GetLocalConfig()

def GetCached(url, cacheTime=60):
        now = time()
        urltime = config.GetValue("timestamp_"+url).split('.')
        urltime = urltime[0]
        if urltime == "":
                urltime = 0
        expiresAt = int(urltime) + int(cacheTime)
        if time() < expiresAt:
                return config.GetValue("data_"+url)
        data = HTTP.Get(url)
        config.SetValue("timestamp_"+url, str(time()))
        config.SetValue("data_"+url, data)
        return data  

# for those special characters
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def getImagesFromGoogle(keyword):
    url = """http://images.google.com/images?q=%s&hl=nl&safe=off&biw=200&bih=105&gbv=2&tbs=isch:1,isz:m&source=lnt&sa=X&ei=sIWjTN2cGcX_lgecr4WZAw&ved=0CAgQpwU""" % (keyword.replace(' ', '+'))
    opener = urllib2.build_opener()
    request = urllib2.Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.10) Gecko/20100914 Firefox/3.6.10 ( .NET CLR 3.5.30729)')
    data = opener.open(request).read()
    soup = BeautifulSoup(data)
    span = soup.findAll('span', {'class':'rg_ctlv'})[0]
    links = span.findAll('a', href=True)
    link = links[0]
    image = link['href'].split('=')[1].split('&')[0]
    return image
