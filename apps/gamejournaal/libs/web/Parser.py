#################################
# ikbenjaap Boxee Framework 0.1 #
#################################
import HTTP
from elementsoup import ElementSoup



def GetElement(url, cacheTime=0):
		data = HTTP.Get(url, cacheTime)
		return ElementSoup.parse(data)
