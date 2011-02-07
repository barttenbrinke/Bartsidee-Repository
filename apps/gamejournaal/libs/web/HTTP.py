#################################
# ikbenjaap Boxee Framework 0.1 #
#################################

import mc
from time import time


HTTP = mc.Http()
HTTP.SetUserAgent("Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)")

config = mc.GetApp().GetLocalConfig()


def Get(url, cacheTime=0):
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