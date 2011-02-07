# South Park for Boxee

import mc
import re
import base64
import time
import urllib


URLS = [
  ['Denmark', 'DK', 'http://www.southparkstudios.dk', '%s/guide/season/%%s/', '%s/guide/'],
  ['Finland', 'FI', 'http://www.southparkstudios.fi', '%s/guide/season/%%s/', '%s/guide/'],
  ['Germany', 'DE', 'http://www.southpark.de', '%s/episodenguide/staffel/%%s/', '%s/episodenguide/'],
  ['The Netherlands', 'NL', 'http://www.southpark.nl', '%s/guide/season/%%s/', '%s/guide/'],
  ['Norway', 'NO', 'http://www.southparkstudios.no', '%s/guide/season/%%s/', '%s/guide/'],
  ['Sweden', 'SE', 'http://www.southparkstudios.se', '%s/guide/season/%%s/', '%s/guide/'],
  ['United States', 'US', 'http://www.southparkstudios.com', '%s/guide/season/%%s/', '%s/guide/']]

THUMB_URL 		= 'http://southparkstudios-intl.mtvnimages.com/shared/sps/images/south_park/episode_thumbnails/s%se%s_480.jpg'

HTTP = mc.Http()
HTTP.SetUserAgent("Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)")

config = mc.GetApp().GetLocalConfig()

def doLoad():
        if config.GetValue("wantindex") != "no":
                doAction("feed://index/0", "")
        config.SetValue("wantindex", "yes")

def doAction(action, label, episode="", season="", desc="", thumb=""):
        action = action.split("/", 3)
	mc.ShowDialogWait()
	if action[2] != "index":
		mc.GetWindow(14000).PushState()

        if action[2] == "player":
                config.SetValue("wantindex", "no")
                player          = mc.GetPlayer()
                list_item       = mc.ListItem(mc.ListItem.MEDIA_VIDEO_EPISODE)
		url = getURLs()[0] + "/" + action[3]
		params = urllib.urlencode({'src':  url, 'bx-jsactions': 'http://dir.boxee.tv/apps/helper2/?v=4.0&u=http%3A%2F%2Fwww.southparkstudios.com%2Fepisodes%2F251891%2F'})
                list_item.SetPath("flash://southpark/"+params)
                list_item.SetReportToServer(True)
                list_item.SetLabel(str(label))
                list_item.SetAddToHistory(True)
                list_item.SetTVShowTitle(str("South Park"))
                list_item.SetSeason(int(season))
                list_item.SetEpisode(int(episode))
                list_item.SetDescription(str(desc))
                list_item.SetThumbnail(str(thumb))
                player.Play(list_item)

	
	if action[2] == "season":
		season = action[3]
		data = HTTP.Get(getURLs()[1] % action[3]).decode('utf-8')
		list        	= mc.GetWindow(14000).GetList(51)
		result		= re.compile('<li class="grid_item">(.*?)</li>', re.DOTALL + re.IGNORECASE + re.M).findall(data)
		list_items 	= mc.ListItems()
		if len(result) > 0:
			for e in result:
				try:
					link = re.compile('<div class="more">.*<a href="(.*?)" class="watch_full_episode">', re.DOTALL + re.IGNORECASE).search(e).group(1)
				except:
					link = ""
				title = re.compile('<span class="title eptitle">(.*?)</span>', re.DOTALL + re.IGNORECASE).search(e).group(1)
				epnumber = re.compile('<span class="epnumber">Episode: ([0-9]+)</span>', re.DOTALL + re.IGNORECASE).search(e).group(1)
				desc = re.compile('<span class="epdesc">(.*?)</span>', re.DOTALL + re.IGNORECASE).search(e).group(1)
				numOnly = epnumber.replace(action[3], '', 1)
				numOnly = numOnly.lstrip('0')
				thumb = THUMB_URL % (season.zfill(2), numOnly.zfill(2))
				list_item 	= mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
				list_item.SetEpisode(int(numOnly))
				list_item.SetLabel(str(title.encode('utf-8')))
				list_item.SetSeason(int(action[3]))
				list_item.SetDescription(str(desc.encode('utf-8')))
				list_item.SetTVShowTitle("South Park")
				list_item.SetProviderSource("South Park Studios")
				list_item.SetThumbnail(str(thumb))
				list_item.SetPath("feed://player" + str(link))
				list_items.append(list_item)
		list.SetItems(list_items)
		
	if action[2] == "index":
		data = HTTP.Get(getURLs()[2]).decode('utf-8')
		list        	= mc.GetWindow(14000).GetList(51)
		result		= re.compile('<li>.*?<a href=".*?>([0-9]+)</a>.*?</li>', re.DOTALL + re.IGNORECASE).findall(data)
		list_items 	= mc.ListItems()
		list_item 	= mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
		if len(result) > 0:
			for e in result:
				list_item 	= mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
				list_item.SetLabel("Season " + str(e))
				list_item.SetPath("feed://season/" + str(e))
				list_items.append(list_item)
		try:
			result		= re.compile('<li>.*?span>([0-9]+)</span>.*?</li>', re.DOTALL + re.IGNORECASE).search(data).group(1)
			list_item 	= mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
			list_item.SetLabel("Season " + str(result))
			list_item.SetPath("feed://season/" + str(result))
			list_items.append(list_item)
		except:
			mc.ShowDialogNotification("No seasons found. Please try another region")
		list_item 	= mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
		list_item.SetLabel("Choose region")
		list_item.SetPath("feed://region/1")
		list_items.append(list_item)

		list.SetItems(list_items)


	if action[2] == "region":
		list        	= mc.GetWindow(14000).GetList(51)
		list_items 	= mc.ListItems()
		list_item 	= mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
		for country, geo, base_url, guide_url, seasonguide_url in URLS:
				list_item 	= mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
				list_item.SetLabel(str(country))
				list_item.SetPath("feed://setregion/" + str(geo))
				list_items.append(list_item)

		list.SetItems(list_items)

	if action[2] == "setregion":
	        config.SetValue("region", action[3])
		mc.ShowDialogNotification("Region changed")
		mc.GetWindow(14000).ClearStateStack(False)
                doAction("feed://index/0", "")

	mc.HideDialogWait()

def getURLs():
	region = config.GetValue("region")
	for country, geo, base_url, guide_url, seasonguide_url in URLS:
		if region == geo:
			return [base_url, (guide_url % base_url), (seasonguide_url % base_url)]
  	region = "US"
	for country, geo, base_url, guide_url, seasonguide_url in URLS:
		if region == geo:
			return [base_url, (guide_url % base_url), (seasonguide_url % base_url)]
