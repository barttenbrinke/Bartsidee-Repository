# Uitzending gemist for Boxee made by jaaps (from ikbenjaap.com)
# Using code from UZG-Plex (http://github.com/mahoek/plex-uzg)

import mc
import re
import uzgf
import base64
import time

# URL AND REGEX
ROOT_URI 		= "http://www.uitzendinggemist.nl/"
DAY_URI 		= ROOT_URI + "index.php/selectie?searchitem=dag&dag="
ZENDER_URI 		= ROOT_URI + "index.php/selectie?searchitem=net_zender&net_zender="
ZOEK_URI		= ROOT_URI + "index.php/search?search_filter=titel&sq="
PLAYER_URI 		= "http://player.omroep.nl/"
PLAYER_INIT_FILE 	= PLAYER_URI + "js/initialization.js.php"
PLAYER_META 		= PLAYER_URI + "xml/metaplayer.xml.php"
REGEX_PAGE_ITEM 	= r"""<a class="title" href="/index.php/serie(\?serID=\d+&amp;md5=[^\"]+)">([^<]+)</a>"""
REGEX_PAGE_PAGES 	= r"""class="populair_top_pagina_nr">(\d+)</(a|strong)>"""
REGEX_PAGE_ITEM2 	= r"""<a href="http://player.omroep.nl/(\?aflID=\d+)"[^>]+><img .*? alt="bekijk uitzending: ([^\"]+)" />"""
REGEX_ITEM_SECURITY 	= r"""var securityCode = '([0-9a-f]+)'"""
REGEX_ITEM_INFO 	= r"""<b class="btitle">[^<]+</b>\s+<p style="margin-top:5px;">(.*?)(\s+<)"""
REGEX_ITEM_THUMB 	= r"""<td height="100"[^>]+>\s+<img src="(.*?)" .*? style="float:left;margin:0px 5px 0px 0px;" />"""
REGEX_STREAM_URI 	= r"""<stream[^>]+compressie_kwaliteit=.bb.[^>]+compressie_formaat=.wmv.[^>]*>([^<]*)</stream>"""
REGEX_STREAM_DIRECT 	= r"""<Ref href[^"]+"([^"]+)\""""
REGEX_SEARCH_ITEM 	= r"""<a class="title" href="/index.php/search(\?serID=\d+&amp;md5=[^&]+)&sq=[^\"]+">([^<]+)</a>"""

#MEDIA_PATH		= mc.GetApp().GetAppMediaDir()
#print MEDIA_PATH
# ? doesn't work?

# Create HTTP for stream fetching
HTTP2 = mc.Http()
# Set user-agent (Windows Media Player)
HTTP2.SetUserAgent("Windows-Media-Player/10.00.00.3646")

# get App Config
config = mc.GetApp().GetLocalConfig()

# load index on app start
def doLoad():
	if config.GetValue("wantindex") != "no":
		data = uzgf.GetCached(ROOT_URI, 1)
		doAction("feed://index/0", "")
	config.SetValue("wantindex", "yes")


# do an Action based on path
# ex: doAction("feed://zender/1", "Zender 1")
# action should always start with feed://
def doAction(action, label, title = "", subtitle = ""):
	# show loading dialog
	mc.ShowDialogWait()
	# get cookies and set them
	action = action.split("/")
	print action
	# push state for back button but not when on the index
	if action[2] != "index":
		mc.GetWindow(14000).PushState()

	if action[2] == "zoek":
		# get search query
		query = mc.ShowDialogKeyboard("Zoekterm:", "", False)
		subtitle = query
		# make url for search
		url = ZOEK_URI +query.replace(" ","%20")
		data = uzgf.GetCached(url).decode('latin-1')
		data = data.replace("<span class=\"highlight\">", "").replace("</span>", "")
		# create and fill the list with items from Shows
		list        = mc.GetWindow(14000).GetList(51)
		list_items  = mc.ListItems() 
		result = re.compile(REGEX_PAGE_PAGES, re.DOTALL + re.IGNORECASE).findall(data)
		# more pages?
		if len(result) > 0:
			for e in result:
				url2 = url + '&pgNum=' + str(e[0])
				list_items = Shows(list_items, uzgf.GetCached(url2).decode('latin-1'), REGEX_SEARCH_ITEM, "Zoeken", subtitle)
		else:
			list_items = Shows(list_items, data, REGEX_SEARCH_ITEM, "Zoeken", subtitle)
		try:
			list.SetItems(list_items)
		except:
			# no results?
			list_items  = mc.ListItems() 
			list_item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
			# set everything in the list item
			list_item.SetLabel("Geen resultaten")
			list_item.SetDescription("Probeer een andere (langere) zoekterm")
			# set the path for doAction
			list_item.SetPath("feed://zoek/")
			list_item.SetThumbnail("")
			# add the item to the list items container
			list_item.SetProperty("title", "Zoeken")
			list_item.SetProperty("subtitle", subtitle)
			list_items.append(list_item)
			list.SetItems(list_items)
 
			
	if action[2] == "dag":
		# create url for day
		url = DAY_URI +action[3]
		data = uzgf.GetCached(url, 600).decode('latin-1')
		data = data.replace("<span class=\"highlight\">", "").replace("</span>", "")
		# create and fill the list with items from Shows
		list        = mc.GetWindow(14000).GetList(51)
		list_items  = mc.ListItems() 
		result = re.compile(REGEX_PAGE_PAGES, re.DOTALL + re.IGNORECASE).findall(data)
		# more pages?
		if len(result) > 0:
			for e in result:
				url2 = url + '&pgNum=' + str(e[0])
				list_items = Shows(list_items, uzgf.GetCached(url2, 600).decode('latin-1'), REGEX_PAGE_ITEM, label, "")
		else:
				list_items = Shows(list_items, data, REGEX_PAGE_ITEM, label, "")
		list.SetItems(list_items)

	if action[2] == "zender":
		# create url for zender
		url = ZENDER_URI +action[3]
		data = uzgf.GetCached(url, 3600).decode('latin-1')
		data = data.replace("<span class=\"highlight\">", "").replace("</span>", "")
		# create and fill the list with items from Shows
		list        = mc.GetWindow(14000).GetList(51)
		list_items  = mc.ListItems() 
		result = re.compile(REGEX_PAGE_PAGES, re.DOTALL + re.IGNORECASE).findall(data)
		# more pages?
		if len(result) > 0:
			for e in result:
				url2 = url + '&pgNum=' + str(e[0])
				list_items = Shows(list_items, uzgf.GetCached(url2, 3600).decode('latin-1'), REGEX_PAGE_ITEM, title, label)
		else:
				list_items = Shows(list_items, data, REGEX_PAGE_ITEM, title, subtitle)
		list.SetItems(list_items)

	if action[2] == "shows":
		# create url for show
		url = ROOT_URI + "index.php/serie" + base64.b64decode(action[3])
		data = uzgf.GetCached(url, 600).decode('latin-1')
		print data.encode('utf-8')
		results = re.compile(REGEX_PAGE_ITEM2, re.DOTALL + re.IGNORECASE + re.M).findall(data)
		if len(results) < 1:
			data = uzgf.GetCached(ROOT_URI, 1)
			time.sleep(2)
			data = uzgf.GetCached(url, 1).decode('latin-1')
		# create and fill the list with items from ShowItems
		list        = mc.GetWindow(14000).GetList(51)
		list_items  = mc.ListItems()
		list_items = ShowItems(list_items, data, REGEX_PAGE_ITEM2, subtitle, label)
		list.SetItems(list_items)

	if action[2] == "play":
		# we don't want to render the index again when we get back from playing the video
		config.SetValue("wantindex", "no")
		# we got an item to play. lets call getStreamUrl to get the url and send it to the player
		url = getStreamUrl(action[3])	
		player		= mc.GetPlayer()
		# make a list item for the player
		list_item 	= mc.ListItem(mc.ListItem.MEDIA_VIDEO_EPISODE)
		# set url
		list_item.SetPath(str(url))
		# report to server
		list_item.SetReportToServer(True)
		# set label
		list_item.SetLabel(str(label))
		# we want to add it to our history
		list_item.SetAddToHistory(True)
		# set title from label_2
		list_item.SetTVShowTitle(str(config.GetValue("label_2")))
		# set description from xml feed
		list_item.SetDescription("Video from Uitzending Gemist (dutch)")
		# and play it
		player.Play(list_item)
		
	if action[2] == "zenders":
		# we should set some labels
		config.SetValue("label_1", "Kies een zender")
		config.SetValue("label_2", "")
		list        = mc.GetWindow(14000).GetList(51)
		list_items  = mc.ListItems()
		list_item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
		# set everything in the list item
		list_item.SetLabel("Nederland 1")
		list_item.SetDescription("Bekijk programma's van Nederland 1")
		# set the path for doAction
		list_item.SetPath("feed://zender/1")
		list_item.SetThumbnail("http://www.bartsidee.nl/boxee/apps/uzg/thumbs/ned1.png")
		list_item.SetProperty("title", "Zenders")
		list_item.SetProperty("subtitle", "Kies een zender")
		# add the item to the list items container
		list_items.append(list_item)

		list_item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
		# set everything in the list item
		list_item.SetLabel("Nederland 2")
		list_item.SetDescription("Bekijk programma's van Nederland 2")
		# set the path for doAction
		list_item.SetPath("feed://zender/2")
		list_item.SetThumbnail("http://www.bartsidee.nl/boxee/apps/uzg/thumbs/ned2.png")
		list_item.SetProperty("title", "Zenders")
		list_item.SetProperty("subtitle", "Kies een zender")
		# add the item to the list items container
		list_items.append(list_item)


		list_item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
		# set everything in the list item
		list_item.SetLabel("Nederland 3")
		list_item.SetDescription("Bekijk programma's van Nederland 3")
		# set the path for doAction
		list_item.SetPath("feed://zender/3")
		list_item.SetThumbnail("http://www.bartsidee.nl/boxee/apps/uzg/thumbs/ned3.png")
		list_item.SetProperty("title", "Zenders")
		list_item.SetProperty("subtitle", "Kies een zender")
		# add the item to the list items container
		list_items.append(list_item)


		# add all the items to the list control
		list.SetItems(list_items)

	if action[2] == "index":
		list        = mc.GetWindow(14000).GetList(51)
		list_items  = mc.ListItems()
		list_item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
		# set everything in the list item
		list_item.SetLabel("Zenders")
		list_item.SetDescription("Bekijk per zender")
		# set the path for doAction
		list_item.SetPath("feed://zenders/")
		list_item.SetProperty("title", "Uitzending Gemist")
		list_item.SetProperty("subtitle", "Maak je keuze")
		list_item.SetThumbnail("ned1.png")
		# add the item to the list items container
		list_items.append(list_item)
		list_item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
		# set everything in the list item
		list_item.SetLabel("Vandaag")
		list_item.SetDescription("Bekijk programma's van vandaag")
		# set the path for doAction
		list_item.SetPath("feed://dag/vandaag")
		list_item.SetThumbnail("")
		# add the item to the list items container
		list_item.SetProperty("title", "Uitzending Gemist")
		list_item.SetProperty("subtitle", "Maak je keuze")
		list_items.append(list_item)
		list_item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
		# set everything in the list item
		list_item.SetLabel("Gisteren")
		list_item.SetDescription("Bekijk programma's van gisteren")
		# set the path for doAction
		list_item.SetPath("feed://dag/gisteren")
		list_item.SetThumbnail("")
		# add the item to the list items container
		list_item.SetProperty("title", "Uitzending Gemist")
		list_item.SetProperty("subtitle", "Maak je keuze")

		list_items.append(list_item)
		list_item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
		# set everything in the list item
		list_item.SetLabel("Zoeken")
		list_item.SetDescription("Zoek naar programma's")
		# set the path for doAction
		list_item.SetPath("feed://zoek/")
		list_item.SetThumbnail("")
		# add the item to the list items container
		list_item.SetProperty("title", "Uitzending Gemist")
		list_item.SetProperty("subtitle", "Maak je keuze")

		list_items.append(list_item)

		list.SetItems(list_items)

	# we should be done! hide the wait dialog
	mc.HideDialogWait()
	
 
def Shows(list_items, data, regex, title, subtitle):
  # Get show for zender
  results = re.compile(regex, re.DOTALL + re.IGNORECASE + re.M).findall(data)
  if len(results) > 0:
    for result in results:
			list_item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
			# set everything in the list item
			list_item.SetProperty("title", title)
			list_item.SetProperty("subtitle", subtitle)
			list_item.SetLabel(str(uzgf.unescape(result[1]).encode('utf-8')))
			list_item.SetDescription("Bekijk uitzendingen van " + str(uzgf.unescape(result[1]).encode('utf-8')))
			# set the path for doAction
			list_item.SetPath("feed://shows/"+base64.b64encode(result[0], "_;"))
			# add the item to the list items container
			list_items.append(list_item)
    return list_items
    
def getStreamUrl(path):
  # get url for mms stream
  temp = uzgf.GetCached("%s%s" % (PLAYER_URI, base64.b64decode(path)), 1)
  site = uzgf.GetCached("%s%s" % (PLAYER_INIT_FILE, base64.b64decode(path)), 1)
  code = re.search(REGEX_ITEM_SECURITY, site).group(1)
  url = "%s%s&md5=%s" % (PLAYER_META, base64.b64decode(path), code)
  item_url = re.search(REGEX_STREAM_URI, uzgf.GetCached(url, 1)).group(1)
  return re.search(REGEX_STREAM_DIRECT, HTTP2.Get(item_url)).group(1)
  
  
def ShowItems(list_items, data, regex, title, label):
  if title == "":
	title = label
	label = ""
  # get show info
  info = re.compile(REGEX_ITEM_INFO, re.DOTALL + re.IGNORECASE + re.M).search(data)
  # get show thumb
  thumb = re.compile(REGEX_ITEM_THUMB, re.DOTALL + re.IGNORECASE + re.M).search(data)
  # get items
  results = re.compile(regex, re.DOTALL + re.IGNORECASE + re.M).findall(data)
  	
  # specify thumb
  try:
    if thumb.group(1):
    	thumbUri = thumb.group(1)
  except:
    thumbUri = ''
    
  # loop through items
  for result in results:
			list_item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
			# set label
			list_item.SetLabel(str(uzgf.unescape(result[1]).encode('utf-8').replace("()", "(onbekende datum)")))
			# set description
			list_item.SetDescription(str(uzgf.unescape(info.group(1).replace("\n", " ").strip()).encode('utf-8')))
			# set thumb
			list_item.SetThumbnail(str(thumbUri.encode('utf-8')))
			# set the path for doAction
			list_item.SetPath("feed://play/"+base64.b64encode(result[0], "_;"))
			list_item.SetProperty("title", title)
			list_item.SetProperty("subtitle", label)
			# add the item to the list items container
			list_items.append(list_item)
  # return it
  return list_items
	




