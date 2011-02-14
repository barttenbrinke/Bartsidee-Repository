# TMF for Boxee

import mc
import re
import base64
import time
import urllib
import string
import tmf_f
from urllib import quote


TMF_BASE_URL                    = "http://www.tmf.nl"
TMF_CONTENT                     = "%s/ajax/?letterResults=%%s" % TMF_BASE_URL
TMF_ARTISTS_QUERY               = "type=artists&static=true&letter=%s&pagina=%d&m=common/alphabetic_list"
TMF_ARTIST_PAGE                 = "%s/artiesten/%%s/" % TMF_BASE_URL
TMF_ARTIST_VIDEOS               = "%s/xml/videoplayer/related.php?id=%%s&action=all" % TMF_BASE_URL


config = mc.GetApp().GetLocalConfig()

def doLoad():
       doAction("feed://index/0", "")

def doAction(action, label, episode="", season="", desc="", thumb=""):
        action = action.split("/", 4)
	mc.ShowDialogWait()
        if action[2] == "play":
                config.SetValue("wantindex", "no")
                player = mc.GetPlayer()
                url = TMF_BASE_URL + '/video/' + action[3] + '/'
                params = urllib.urlencode({'src':  url})
                list_item       = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
                path = 'flash://%s/src=%s&bx-jsactions=%s' % ("tmf.nl", quote(url), quote('http://boxee.bartsidee.nl/apps/js/tmf.js'))
                list_item.SetPath(path)
                list_item.SetReportToServer(True)
                list_item.SetAddToHistory(True)
                list_item.SetLabel(str(desc))
                player.Play(list_item)
		
	if action[2] == "artist":
		list_items 	= mc.ListItems()
		data = tmf_f.getFeed(TMF_ARTIST_VIDEOS % action[3])
		try: 
			items = data.getElementsByTagName("content")[0].getElementsByTagName("image")
			for item in items:
				titel = tmf_f.unescape(item.getElementsByTagName("description")[0].firstChild.wholeText).encode('utf-8')
				videoid = tmf_f.unescape(item.getElementsByTagName("data")[0].firstChild.wholeText).encode('utf-8')
				thumb = tmf_f.unescape(item.getElementsByTagName("path")[0].firstChild.wholeText).encode('utf-8').split("proxy.php?src=", 1)[1]
				videoid = re.search(r'Video\((.+)\);', videoid).group(1)
				if titel.find(" - ") != -1:
					titel = titel.split(" - ", 1)[1]
				list_item 	= mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
				list_item.SetLabel(str(titel))
				list_item.SetThumbnail(str(thumb))
				list_item.SetPath("feed://play/"+videoid)
				list_item.SetDescription(label + " - " + titel)
				list_item.SetProperty("isvideoclip", "jep")
				list_item.SetProperty("titel", label)
				list_items.append(list_item)
			app = mc.GetApp()
			params = mc.Parameters()
			params[""] = ""
			app.ActivateWindow(14002, params)
                        list            = mc.GetWindow(14002).GetList(53)
			list.SetItems(list_items)
		except:
			print "no data?"		

	if action[2] == "index":
		list        	= mc.GetWindow(14000).GetList(53)
		list_items 	= mc.ListItems()
		list_item 	= mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
		list_item.SetLabel("0-9")
		list_item.SetPath("feed://letter/0-9")
		list_items.append(list_item)
		for char in string.ascii_uppercase:
				list_item 	= mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
				list_item.SetLabel(str(char))
				list_item.SetPath("feed://letter/" + str(char))
				list_items.append(list_item)

		list.SetItems(list_items)

	if action[2] == "letter":
		list_items 	= mc.ListItems()
		letter = action[3]
		query = base64.b64encode(TMF_ARTISTS_QUERY % (letter.lower(), 1))
		data = tmf_f.Get(TMF_CONTENT % query)
		numPages = 0
		try: 
			result = re.compile('<div class="cb">(.*?)</div>', re.DOTALL + re.IGNORECASE).search(data).group(1)
			pages = re.compile('<a href(.*?)</a>', re.DOTALL + re.IGNORECASE).findall(result)
		except:
			numPages = 1
		if numPages != 1:
			numPages= len(pages)-1
		
		for i in range(1, numPages+1):
			query = base64.b64encode(TMF_ARTISTS_QUERY % (letter.lower(), i))
			data = tmf_f.Get(TMF_CONTENT % query).decode('latin-1')
			result = re.compile('<div class="cb item"(.*?)\/.item', re.DOTALL + re.IGNORECASE).findall(data)
			for item in result:
				artist = re.compile('<div class="title">.*?<a href=".*?">(.*?)</a>', re.DOTALL + re.IGNORECASE).search(item).group(1).strip()
				desc = re.compile('<div class="text">(.*?)</div>', re.DOTALL + re.IGNORECASE).search(item).group(1).strip()
				link = re.compile('<a href="/artiesten/(.*?)">', re.DOTALL + re.IGNORECASE).search(item).group(1)
				thumb = re.compile('<img src="(.*?)"', re.DOTALL + re.IGNORECASE).search(item).group(1)
				list_item 	= mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
				list_item.SetLabel(str(tmf_f.unescape(artist).encode('utf-8')))
				list_item.SetDescription(str(tmf_f.unescape(desc).encode('utf-8')))
				list_item.SetPath("feed://artist/"+str(link))
				list_item.SetThumbnail(str(thumb))
				list_items.append(list_item)
		app = mc.GetApp()
		params = mc.Parameters()
		params[""] = ""
		app.ActivateWindow(14001, params)
		list            = mc.GetWindow(14001).GetList(53)
		list.SetItems(list_items)

	mc.HideDialogWait()

