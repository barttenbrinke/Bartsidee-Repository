import mc, re, os, sys
sys.path.append(os.path.join(mc.GetApp().GetAppDir(), 'libs'))
import ba
from beautifulsoup.BeautifulSoup import BeautifulSoup
from itertools import izip

class Module(object):
    def __init__(self):
        self.name = "Nederland 24"                  #Name of the channel
        self.type = ['list']                        #Choose between 'search', 'list', 'genre'
        self.episode = False                        #True if the list has episodes
        self.filter = []                            #Option to set a filter to the list
        self.genre = []                             #Array to add a genres to the genre section [type genre must be enabled]
        self.content_type = ''        #Mime type of the content to be played
        self.country = 'NL'                         #2 character country id code

        self.channels = [
            ["101 TV", "http://livestreams.omroep.nl/npo/101tv-bb", "video/x-ms-asf", "Weg met suffe en saaie tv! Het is tijd voor 101 TV, het 24-uurs jongerenkanaal van BNN en de Publieke Omroep. Met rauwe en brutale programma's, van en voor jongeren. Boordevol hilarische fragmenten, spannende livegames, bizarre experimenten en nieuws over festivals en gratis concertkaartjes. Kijken dus!"],
            ["Best 24", "http://livestreams.omroep.nl/npo/best24-bb", "video/x-ms-asf","Best 24 brengt hoogtepunten uit zestig jaar televisiehistorie. Het is een feelgoodkanaal met 24 uur per dag de leukste, grappigste en meest spraakmakende programma's uit de Hilversumse schatkamer. Best 24: de schatkamer van de publieke omroep."],
            ["Consumenten 24", "http://livestreams.omroep.nl/npo/consumenten24-bb", "video/x-ms-asf","Op Consumenten 24 ziet u dagelijks het laatste consumentennieuws en kunt u de hele week kijken naar herhalingen van Radar, Kassa, en vele andere consumentenprogramma's. In Vraag en Beantwoord kunt u live uw vraag stellen per telefoon en webcam."],
            ["Cultura 24", "http://livestreams.omroep.nl/npo/cultura24-bb", "video/x-ms-asf","Dit is het 'cultuurkanaal van de Publieke Omroep' met de beste recente en oudere 'kunst en expressie' over verschillende onderwerpen. Klassieke muziek, dans, literatuur, theater, beeldende kunst, film 'Waar cultuur is, is Cultura 24'."],
            ["Familie 24 / Z@ppelin", "http://livestreams.omroep.nl/npo/familie24-bb", "video/x-ms-asf","Z@ppelin24 zendt dagelijks uit van half drie 's nachts tot half negen 's avonds. Familie24 is er op de tussenliggende tijd. Z@ppelin 24 biedt ruimte aan (oude) bekende peuterprogramma's en je kunt er kijken naar nieuwe kleuterseries. Op Familie24 zijn bekende programma's te zien en nieuwe programma's en documentaires die speciaal voor Familie24 zijn gemaakt of aangekocht."],
            ["Geschiedenis 24", "http://livestreams.omroep.nl/npo/geschiedenis24-bb", "video/x-ms-asf","Geschiedenis 24 biedt een actuele, duidende en verdiepende blik op de historie, maar ook een historische blik op de actualiteit. Om de urgentie te vergroten is de programmering thematisch. Ook programma's van Nederland 2 als In Europa, Andere Tijden Sport en De Oorlog zijn gelieerd aan Geschiedenis 24."],
            ["Holland Doc 24", "http://livestreams.omroep.nl/npo/hollanddoc24-bb", "video/x-ms-asf","Holland Doc 24 brengt op verschillende manieren en niveaus documentaires en reportages onder de aandacht. De programmering op Holland Doc 24 is gecentreerd rond wekelijkse thema's, die gerelateerd zijn aan de actualiteit, de programmering van documentairerubrieken, van culturele instellingen en festivals."],
            ["Humor TV 24", "http://livestreams.omroep.nl/npo/humortv24-bb", "video/x-ms-asf","Humor TV 24 is een uitgesproken comedykanaal: een frisse, Nederlandse humorzender met hoogwaardige, grappige, scherpe, jonge, nieuwe, satirische, humoristische programma's."],
            ["Journaal 24", "http://livestreams.omroep.nl/nos/journaal24-bb", "video/x-ms-asf","Via het themakanaal 'Journaal 24' kunnen de live televisieuitzendingen van het NOS Journaal worden gevolgd. De laatste Journaaluitzending wordt herhaald tot de volgende uitzending van het NOS Journaal."],
            ["Politiek 24", "http://livestreams.omroep.nl/nos/politiek24-bb", "video/x-ms-asf","Politiek 24 is het digitale kanaal over de Nederlandse politiek in de breedste zin van het woord."],
            ["Spirit 24", "http://livestreams.omroep.nl/npo/spirit24-bb", "video/x-ms-asf","Spirit 24 is interreligieus en multicultureel en biedt de kijker een breed aanbod van onderwerpen op het gebied van spiritualiteit, levensbeschouwing, zingeving, cultuur en filosofie, gezien vanuit verschillende geloofsrichtingen en invalshoeken. Spirit 24 laat de kijker genieten en brengt op toegankelijke wijze (nieuwe) inzichten!"],
            ["Sterren 24", "http://livestreams.omroep.nl/npo/sterren24-bb", "video/x-ms-asf","Op Sterren 24 zijn de beste Nederlandse artiesten te bewonderen en te beluisteren. Naast clips en uitzendingen uit het rijke TROS-archief is er ruimte voor nieuw materiaal en bieden ze aanstormend Nederlands muziektalent een podium op 24-uurs muziekzender Sterren 24."],
            ["TV Gelderland", "http://ms.stream.garnierprojects.com/tvgelderland", "video/x-ms-asf",""],
            #["RTV Utrecht", "http://192.87.23.20:8081", "video/x-ms-wmv",""],
            ["Omprop Frysln", "mms://mms.omropfryslan.nl/tv", "video/x-ms-wmv",""],
            ["RTV Noord", "mms://rtvlivetv.exception.nl/tvrtvnoord", "video/x-ms-wmv",""],
            ["Omproep Flevoland", "mms://mms.omropfryslan.nl/tv", "video/x-ms-wmv",""],
            ["RTV Rijnmond", "http://www.rijnmond.nl/uploads/LiveStreamTV/rtv_rijnmond_rollover2.asx", "video/x-ms-asx",""],
            ["Omproep Brabant", "http://media.omroepbrabant.com/?wm=static:LiveTV", "video/x-ms-asf",""],
            ["Omroep West", "mms://wm1.ams.cdn.surf.net/surfnetvdox=omroepwest=televisie", "video/x-ms-wmv",""],
            ["RTV Drente", "mms://91.213.69.147/RTVVideo", "video/x-ms-wmv",""],
            #["RTV Oost", "http://www.rtvoost.nl/tvoostlive.asx", "video/x-ms-asx",""],
            ["Omproep Zeeland", "mms://stream1.zeelandnet.nl/omroepzeeland_tv", "video/x-ms-wmv",""],
        ]

    def List(self):
        streamlist = list()
        for item in self.channels:
            stream = ba.CreateStream()
            stream.SetName(item[0])
            stream.SetId(item[0])
            streamlist.append(stream)

        return streamlist

    def Play(self, stream_name, stream_id, subtitle):
        play = ba.CreatePlay()
        for item in self.channels:
            if item[0] == stream_id:
                play.SetPath(item[1])
                play.SetContent_type(item[2])

        return play

   