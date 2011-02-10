#===============================================================================
# LICENSE Bartsidee Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/
# or send a letter to Creative Commons, 171 Second Street, Suite 300,
# San Francisco, California 94105, USA.
#===============================================================================
import mc, bz2, binascii, os
from time import time
from django import encoding
import cPickle as pickle
from beautifulsoup.BeautifulSoup import BeautifulSoup

#===============================================================================
# Global Variables
#===============================================================================
http = mc.Http()
http.SetUserAgent("Mozilla/5.0 (Windows; U; Windows NT 6.1; nl; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13")
http.SetHttpHeader('Accept', 'text/javascript, text/html, application/xml, text/xml, */*')

config = mc.GetApp().GetLocalConfig()

#===============================================================================
# Function to Retrieve and Cache a Http request
# Input:
# url - reqest url
# cacheTime - amount of time to keep the http result in the cache (seconds)
# xhr - make a xhr ajax request (boolean)
# params - parameters to POST if empty a GET request is executed
#===============================================================================
def FetchUrl(url, cacheTime=0, xhr=False, params="", cookie=""):
    dbid = "cache_" + url
    if Cache(dbid+'{0}', cacheTime): return bz2.decompress(binascii.unhexlify(config.GetValue(dbid+'{1}')))
    if xhr: http.SetHttpHeader('X-Requested-With', 'XMLHttpRequest')
    if cookie: http.SetHttpHeader('Cookie', cookie)
    if params: data = http.Post(url, params)
    else: data = http.Get(url)

    if cacheTime != 0:
        config.Reset(dbid)
        config.Reset(dbid)
        config.PushBackValue(dbid, str(time()).split('.')[0])
        config.PushBackValue(dbid, binascii.hexlify(bz2.compress(data)))
    return data

#===============================================================================
# Function to determine if a cache is expired, returns a boolean
# Input:
# var - user agent variable as string
#===============================================================================
def UserAgent(var):
    http.SetUserAgent(var)

#===============================================================================
# Function to determine if a cache is expired, returns a boolean
# Input:
# dbid - variable ame id in database to check
# cacheTime - amount of time to keep the variable in the cache (seconds)
#===============================================================================
def Cache(dbid, cacheTime):
    if cacheTime == 0: return False
    urltime = config.GetValue(dbid)
    if urltime == "": urltime = 0
    expiresAt = int(urltime) + int(cacheTime)
    if time() < expiresAt:
        return True
    else:
        return False

#===============================================================================
# Function to clean the app database: speeds it up and saves storage space
# Input:
# interval - amount of time before a new cleanup (seconds)
# save - array containing the variable names to exclude from deleting
#===============================================================================
def CleanDb(interval, save=[]):
    latest = config.GetValue('clean')
    if latest == "": latest = 0
    expiresAt = int(latest) + int(interval)
    if time() > expiresAt:
        var_save = []
        for i in range(len(save)):
            var_save.append(config.GetValue(save[i]))
        config.ResetAll()
        config.SetValue('clean', str(time()).split('.')[0])
        for i in range(len(save)):
            config.SetValue(str(save[i]), str(var_save[i]))

#===============================================================================
# Function to convert special characters to regular unicode characters (python 2.4)
# Input:
# string - string to check
# codec - codec to encodie the string in
#===============================================================================
def ConvertASCII(x):
    return encoding.smart_str(x, encoding='ascii', errors='ignore')

#===============================================================================
# Serialize an objetc/array/dictonary into a string
# Input:
# obj - object/dictonary element
#===============================================================================
def Serialize(obj):
    return pickle.dumps(obj)
    #return marshal.dumps(obj)

#===============================================================================
# Deserialize a string into an object/array/dictonary
# Input:
# obj - object/dictonary element
#===============================================================================
def Deserialize(obj):
    return pickle.loads(obj)
    #return marshal.loads(zstr)


#===============================================================================
# Get SAMI subtitle from string and converts it a tmp srt file, returning the path
# Input:
# data - string containing sami subtitle data
#===============================================================================
def ConvertSami(samiurl):
    data = FetchUrl(samiurl, 0)
    soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
    i = 1
    sync = ''
    temp = ''
    for info in soup.findAll("sync"):
        if info.find(attrs={"class" : "ENUSCC"}):
            sync += str(i) + '\n'
            temp = info.find(attrs={"class" : "ENUSCC"}).contents[0]
            timemsec = str(info['start'])[-3:]
            timesec = int(str(info['start']))/1000
            hour = timesec / 3600
            minute = (timesec - (hour*3600)) / 60
            sec = timesec - (hour*3600) - (minute*60)
            srttime = str(hour) + ':' + str(minute) + ':' + str(sec) + ',' + str(timemsec)
            sync += str(srttime)
            i += 1
        else:
            timemsec = str(info['start'])[-3:]
            timesec = int(str(info['start']))/1000
            hour = timesec / 3600
            minute = (timesec - (hour*3600)) / 60
            sec = timesec - (hour*3600) - (minute*60)
            srttime = str(hour) + ':' + str(minute) + ':' + str(sec) + ',' + str(timemsec)
            sync += ' --> ' + str(srttime) + '\n'
            sync += str(temp) + '\n' + '\n'
        tmpPath = mc.GetTempDir()
        subFilePath = tmpPath+os.sep+'subcache.srt'
        f = open(subFilePath, "w")
        f.write(sync)
        f.close()
    return subFilePath

#===============================================================================
# Get SAMI subtitle from string and converts it a tmp srt file, returning the path
# Input:
# data - string containing sami subtitle data
#===============================================================================
def ConvertFlashXML(path):
    data = FetchUrl(path)
    soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
    i = 1
    add = 1
    sync = ''
    tmp = False
    for info in soup.findAll("p"):
        sync += str(i) + '\n'

        timesec1 = str(info['begin'])
        timesec1 = timesec1.split('.')
        timesec2 = str(info['end'])
        timesec2 = timesec2.split('.')

        for tt in [timesec1,timesec2]:
            if not tmp: tmp = True
            else: tmp = False
            hour = (int(tt[0])+add) / 3600
            minute = ((int(tt[0])+add) - (hour*3600)) / 60
            sec = (int(tt[0])+add) - (hour*3600) - (minute*60)
            sync += str(hour) + ':' + str(minute) + ':' + str(sec) + ',' + str(tt[1])

            if tmp: sync += ' --> '
            else: sync += '\n'

        sync += ConvertASCII(info.renderContents()).replace('\n','').replace('\t','').replace('<br />','\n')
        sync += '\n' + '\n'
        i += 1

    tmpPath = mc.GetTempDir()
    subFilePath = tmpPath+os.sep+'subcache.srt'
    f = open(subFilePath, "w")
    f.write(sync)
    f.close()
    return subFilePath




#===============================================================================
# Variable Objects
#===============================================================================
class CreateStream:
    def __init__(self):
        self.name = ''
        self.id = ''
        self.episode = ''

    def SetName(self, var=''):
        self.name = var

    def SetId(self, var=''):
        self.id = var

    def SetEpisode(self, var=''):
        self.episode = var

class CreateEpisode:
    def __init__(self):
        self.name = ''
        self.id = ''
        self.description = ''
        self.thumbnails = ''
        self.date = ''
        self.filter = ''
        self.page = ''
        self.totalpage = ''
        self.episode = ''

    def SetName(self, var=''):
        self.name = var

    def SetId(self, var=''):
        self.id = var

    def SetDescription(self, var=''):
        self.description = var

    def SetThumbnails(self, var=''):
        self.thumbnails = var

    def SetDate(self, var=''):
        self.date = var

    def SetFilter(self, var=''):
        self.filter = var

    def SetPage(self, var=''):
        self.page = var

    def SetTotalpage(self, var=''):
        self.totalpage = var

    def SetEpisode(self, var=''):
        self.episode = var

class CreatePlay:
    def __init__(self):
        self.path = ''
        self.subtitle = ''
        self.subtitle_type = ''
        self.domain = ''
        self.jsactions = ''
        self.content_type = ''
        self.rtmpurl = ''
        self.rtmpdomain = ''
        self.rtmpauth = ''

    def SetPath(self, var=''):
        self.path = var

    def SetDomain(self, var=''):
        self.domain = var

    def SetJSactions(self, var=''):
        self.jsactions = var
        
    def SetSubtitle(self, var=''):
        self.subtitle = var

    def SetSubtitle_type(self, var=''):
        self.subtitle_type = var

    def SetContent_type(self, var=''):
        self.content_type = var

    def SetRTMPPath(self, var=''):
        self.rtmppath = var

    def SetRTMPDomain(self, var=''):
        self.rtmpdomain = var

    def SetRTMPAuth(self, var=''):
        self.rtmpauth = var

class SearchData:
    def __init__(self):
        self.module = {}
        self.type = ''
        self.name = ''
        self.id = ''
        self.label = ''
        self.episode = ''

    def SetModule(self, var=''):
        self.module = var

    def SetType(self, var=''):
        self.type = var

    def SetLabel(self, var=''):
        self.label = var

    def SetName(self, var=''):
        self.name = var

    def SetId(self, var=''):
        self.id = var
        
    def SetEpisode(self, var=''):
        self.episode = var
