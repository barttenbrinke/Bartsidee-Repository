# function unescape is made by Fredrik Lundh from effbot.org
import mc
import re, htmlentitydefs
from time import time

http = mc.Http()
http.SetUserAgent("Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10")

config = mc.GetApp().GetLocalConfig()

def FetchUrl(url, cacheTime=60, xhr=False, params="",):
    if cacheTime != 0:
        dbid = "cache_" + url
        urltime = config.GetValue(dbid+'{0}')
        if urltime == "": urltime = 0
        expiresAt = int(urltime) + int(cacheTime)
        if time() < expiresAt:
                return config.GetValue(dbid+'{1}')

    if xhr == True:
        http.SetHttpHeader('X-Requested-With', 'XMLHttpRequest')
    if params == "":
        data = http.Get(url)
    else:
        data = http.Post(url, params)

    if cacheTime != 0:
        config.Reset(dbid)
        config.Reset(dbid)
        config.PushBackValue(dbid, str(time()).split('.')[0])
        config.PushBackValue(dbid, data)
    return data

def CleanDb(interval):
    latest = config.GetValue('clean')
    if latest == "": latest = 0
    expiresAt = int(latest) + int(interval)
    if time() > expiresAt:
        config.ResetAll()
        config.SetValue('clean', str(time()).split('.')[0])

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

