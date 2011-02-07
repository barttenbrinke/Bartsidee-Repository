# -*- coding: utf-8 -*-
#################################
# ikbenjaap Boxee Framework 0.1 #
#################################

import mc

targetcontrol = ""
targetwindow = ""
dir = ""

def CreateDir(control = 51, window = 14000):
	global targetcontrol, targetwindow, dir, targetsubtitle
	mc.ShowDialogWait()
	targetcontrol  	= control
	targetwindow   	= window
	dir 		= mc.ListItems()
	
def AddToDir(label = "", desc = "", link = "", thumb = "", properties = {}, type = mc.ListItem.MEDIA_VIDEO_CLIP):
	list_item 	= mc.ListItem(type)
	list_item.SetLabel(str(label.encode('utf-8','ignore')))
	list_item.SetThumbnail(str(thumb.encode('utf-8','ignore')))
	list_item.SetDescription(str(desc.encode('utf-8','ignore')))
	for naam, value in properties.items():
		list_item.SetProperty(str(naam.encode('utf-8','ignore')), str(value.encode('utf-8','ignore')))
	list_item.SetPath(str(link.encode('utf-8','ignore')))
	dir.append(list_item)

def PushDir():
	app = mc.GetApp()
	params = mc.Parameters()
	params["noreload"] = "1"
	app.ActivateWindow(targetwindow, params)
	list = mc.GetWindow(targetwindow).GetList(targetcontrol)
	list.SetItems(dir)
	mc.HideDialogWait()
