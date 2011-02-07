import time
from urllib import quote
from web import Parser
from boxee import Dir

BASE_URL			= "http://www.gamer.nl"
GAMER_MAIN_URL		= "%s/videos?q=gamejournaal" % BASE_URL
GAMER_MAIN_XPATH	= './/div[@class="kolom rechts"]//div/ul/li[div]'


def init():
	element = Parser.GetElement(GAMER_MAIN_URL, 3600)

	Dir.CreateDir()

	for item in element.findall(GAMER_MAIN_XPATH):
		datum = item.find(".//span[@class='info']").text.split(" ")[0]
		week = time.strftime("%W (%Y)", time.strptime(datum, "%d-%m-%Y"))

		desc = ""
		try:
			desctotaal = item.findall(".//p")
			for descpart in desctotaal:
				desc = desc + descpart.text.strip()
		except:
			desc = ""

		if desc != "":
			properties = {'titel' : "Week "+week, 'subtitel' : desc}
		else:
			properties = {'titel' : "Week "+week, 'subtitel' : item.find(".//a[@title]").attrib["title"].replace("Gamejournaal: " , "").strip()}
			desc = item.find(".//a[@title]").attrib["title"].replace("Gamejournaal: " , "").strip()

		#		Label					Desc		URL							Thumb					Properties
		Dir.AddToDir(	"Gamejournaal week " + week,		desc,		'flash://%s/src=%s&bx-jsactions=%s' % ("gamer.nl", quote(BASE_URL+str(item.find(".//a[@title]").attrib["href"])), quote('http://boxee.ikbenjaap.com/gamer.js')), 	item.find(".//img").attrib["src"], 	properties)

	Dir.PushDir()
