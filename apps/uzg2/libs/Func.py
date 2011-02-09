# function unescape is made by Fredrik Lundh from effbot.org
import mc
import re, htmlentitydefs
from time import time

http = mc.Http()
http.SetUserAgent("Mozilla/5.0 (Windows; U; Windows NT 6.1; nl; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13")
http.SetHttpHeader('Accept', 'text/javascript, text/html, application/xml, text/xml, */*')

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
        sub = config.GetValue('sub')
        config.ResetAll()
        config.SetValue('clean', str(time()).split('.')[0])
        config.SetValue('sub', str(sub))