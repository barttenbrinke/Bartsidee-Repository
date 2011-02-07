# TMF Functions
# function unescape is made by Fredrik Lundh from effbot.org
import mc
import re, htmlentitydefs
from time import time
from xml.dom import minidom

HTTP = mc.Http()
HTTP.SetUserAgent("Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)")

config = mc.GetApp().GetLocalConfig()

def getFeed(url):
	try: 
        	feed = Get(url)
       		return minidom.parseString(feed)
	except:
		return ""

def getNode(nodes):
        rc = ""
        for node in nodes:
                if node.nodeType == node.TEXT_NODE:
                        rc = rc + node.data
        return rc



def Get(url, cacheTime=3600):
        now = time()
        print now
        urltime = config.GetValue("timestamp_"+url).split('.')
        urltime = urltime[0]
        if urltime == "":
                urltime = 0
        expiresAt = int(urltime) + int(cacheTime)
        if time() < expiresAt:
                print "got cache"
                return config.GetValue("data_"+url)
        print "havent got cache"
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

