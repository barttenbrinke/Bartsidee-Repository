#===============================================================================
# LICENSE Bartsidee Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/
# or send a letter to Creative Commons, 171 Second Street, Suite 300,
# San Francisco, California 94105, USA.
#===============================================================================

import mc, os, sys, bz2, binascii, ba, xbmc
from time import time, sleep
from operator import itemgetter
import thread
#from printdict import prnDict

class main_obj(object):
    ##############################################################################
    ######   General
    ##############################################################################
    def __init__(self):
        self.module = {}
        self.module_obj = {}
        self.search_db = {}
        self.settings = {}
        self.search_dynamic = []
        self.db_rm_exclude = ['searchdb', 'settings', 'search_history']
        self.Settings()
        self.ImportChannels()
        self.module_path = os.path.join(mc.GetApp().GetAppDir(), 'modules')
        self.debug = False
        ba.CleanDb(259200, self.db_rm_exclude)

    def Settings(self, save=False):
        if save == False:
            if mc.GetApp().GetLocalConfig().GetValue('settings'):
                self.settings = self.GetFromDB('settings')
            else:
                self.settings = {'modules_on': [], 'modules_loaded': [], 'subtitle': False, 'clean' : 1}
        else:
            self.SaveToDB('settings', self.settings)

        #######temp cleanup
        try:
            self.settings['clean']
        except:
            ba.CleanDb(0)
            self.Settings()
            self.Settings(True)
        ########
        print "BARTSIDEE FRAMEWORK: Settings Loaded."

    def SetChannel(self, module):
        self.module_obj[module] = self.module[module].Module()

    def GetFromDB(self, key):
        data = bz2.decompress(binascii.unhexlify(mc.GetApp().GetLocalConfig().GetValue(key)))
        return ba.Deserialize(data)
        print 'BARTSIDEE FRAMEWORK: Retrieved object ' + key +' from database file'

    def SaveToDB(self, key, obj):
        data = ba.Serialize(obj)
        mc.GetApp().GetLocalConfig().SetValue(key, binascii.hexlify(bz2.compress(data)))
        print 'BARTSIDEE FRAMEWORK: Saved object ' + key +' to database file'

    def ImportChannels(self):
        self.module_path = os.path.join(mc.GetApp().GetAppDir(), 'modules')
        sys.path.append(self.module_path)
        self.settings['modules_loaded'] = []
        for dirpath, dirnames, filenames in os.walk(self.module_path):
            for module in dirnames:
                importstring = module + '.' + module
                mod = __import__(importstring)
                components = importstring.split('.')
                for comp in components[1:]:
                    mod = getattr(mod, comp)
                self.module[module] = mod
                self.SetChannel(module)
                self.db_rm_exclude.append('searchdb_'+ module)
                self.settings['modules_loaded'].append(module)

        print "BARTSIDEE FRAMEWORK: Modules imported."

    ##############################################################################
    ######   Module Management
    ##############################################################################
    def List(self, module):
        mc.ShowDialogWait()
        if self.debug:
            streamlist = self.module_obj[module].List()
        else:
            try:
                streamlist = self.module_obj[module].List()
            except:
                print 'A "Stream Load" error occured for the module: ' + module
                streamlist = ba.CreateStream()

        for stream in streamlist:
            label = ba.ConvertASCII(stream.name)
            search_item = ba.SearchData()
            search_item.SetModule(module)
            search_item.SetType(self.module_obj[module].type)
            search_item.SetName(self.module_obj[module].name)
            search_item.SetId(stream.id)
            search_item.SetEpisode(stream.episode)
            self.search_db[label] = search_item

        mc.GetApp().GetLocalConfig().SetValue('searchdb_' + str(module), str(time()).split('.')[0])
 
        print "BARTSIDEE FRAMEWORK: Module " + str(module) + " added to database."
        mc.HideDialogWait()

    def Episode(self, module, stream_name, stream_id, page=1, totalpage=''):
        mc.ShowDialogWait()
        if self.debug:
            episodelist = self.module_obj[module].Episode(stream_name, binascii.unhexlify(stream_id), page, totalpage)
        else:
            try:
                episodelist = self.module_obj[module].Episode(stream_name, binascii.unhexlify(stream_id), page, totalpage)
            except:
                print 'A "Episode Load" error occured for the module: ' + module
                episodelist = ba.CreateEpisode()
                
        if len(episodelist) < 1:
            mc.HideDialogWait()
            return
        
        mc.GetWindow(14446).ClearStateStack(False)
        mc.ActivateWindow(14446)
        list = mc.GetWindow(14446).GetList(51)
        list_items = mc.ListItems()

        for episode in episodelist:
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(ba.ConvertASCII(episode.name))
            list_item.SetThumbnail(str(episode.thumbnails))
            list_item.SetProperty('icon', str(os.path.join(self.module_path, module, module + '.png')))
            list_item.SetProperty('stream_id', str(stream_id))
            list_item.SetProperty('stream_url', str(binascii.hexlify(episode.id)))
            list_item.SetProperty('module_name', str(self.module_obj[module].name))
            list_item.SetProperty('date', str(ba.ConvertASCII(episode.date)))
            list_item.SetProperty('desc', str(ba.ConvertASCII(episode.description)))
            list_item.SetProperty('module', str(module))
            list_item.SetProperty('page', str(episode.page))
            list_item.SetProperty('totalpage', str(episode.totalpage))
            list_items.append(list_item)


        print "BARTSIDEE FRAMEWORK: Fetching episodes for '" + str(stream_name) + "' p." + str(page) + " compleet."
        mc.HideDialogWait()
        list.SetItems(list_items)

    def Genre(self, module, genre, filter='', page=1, totalpage=''):
        mc.ShowDialogWait()
        if self.debug:
            genrelist = self.module_obj[module].Genre(genre, filter, page, totalpage)
        else:
            try:
                genrelist = self.module_obj[module].Genre(genre, filter, page, totalpage)
            except:
                print 'A "Genre Load" error occured for the module: ' + str(module)
                genrelist = ba.CreateEpisode()
        if len(genrelist) < 1:
            return

        list = mc.GetWindow(14445).GetList(53)
        list_items = mc.ListItems()
        
        for item in genrelist:
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(ba.ConvertASCII(item.name))
            list_item.SetThumbnail(str(item.thumbnails))
            list_item.SetProperty('icon', str(os.path.join(self.module_path, module, module + '.png')))
            list_item.SetProperty('stream_id', str(binascii.hexlify(item.id)))
            list_item.SetProperty('module_name', str(self.module_obj[module].name))
            list_item.SetProperty('date', str(item.date))
            list_item.SetProperty('desc', str(ba.ConvertASCII(item.description)))
            list_item.SetProperty('filter', str(item.filter))
            list_item.SetProperty('module', str(module))
            list_item.SetProperty('episode', str(item.episode))
            list_item.SetProperty('genre', str(genre))
            list_item.SetProperty('page', str(item.page))
            list_item.SetProperty('totalpage', str(item.totalpage))
            list_items.append(list_item)


        print "BARTSIDEE FRAMEWORK: Fetching genre for '" +str(module) + ": " + str(genre) + "' p." + str(page) + " compleet."
        mc.HideDialogWait()
        list.SetItems(list_items)

    def Play(self, module, stream_name, stream_id):
        mc.ShowDialogWait()
        if self.debug:
            play = self.module_obj[module].Play(stream_name, binascii.unhexlify(stream_id), self.settings['subtitle'])
        else:
            try:
                play = self.module_obj[module].Play(stream_name, binascii.unhexlify(stream_id), self.settings['subtitle'])
            except:
                return
        if str(play.path) == '':
            return
        
        content_type = self.module_obj[module].content_type
        if len(content_type) < 4:
            content_type = str(play.content_type)

        if content_type == "video/x-flv":
            if play.jsactions == '':
                path = 'flash://' + str(play.domain) + '/src=' + str(play.path)
            else:
                path = 'flash://' + str(play.domain) + '/src=' + str(play.path) + '&bx-jsactions=' + str(play.jsactions)
            player = mc.GetPlayer()
            list_item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
            list_item.SetLabel(str(stream_name))
            list_item.SetTitle(str(stream_name))
            list_item.SetPath(str(path))
            list_item.SetProviderSource(str(module))
            list_item.SetReportToServer(True)
            list_item.SetAddToHistory(True)
        else:
            player = mc.GetPlayer()
            list_item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
            list_item.SetLabel(str(stream_name))
            list_item.SetTitle(str(stream_name))
            list_item.SetPath(str(play.path))
            list_item.SetContentType(str(content_type))
            list_item.SetProviderSource(str(module))
            list_item.SetReportToServer(True)
            list_item.SetAddToHistory(True)

        print "BARTSIDEE FRAMEWORK: Play episode " + str(stream_name) + " started from: " +str(module)
        mc.HideDialogWait()
        player.Play(list_item)

        if self.settings['subtitle']:
            if play.subtitle != '':
                if play.subtitle_type == 'sami':
                    play.subtitle = ba.ConvertSami(play.subtitle)
                sleep(5)
                xbmc.Player().setSubtitles(str(play.subtitle))
                print "BARTSIDEE FRAMEWORK: Subtitle added to " + str(stream_name)

    ##############################################################################
    ######   SEARCH DB
    ##############################################################################
    def Search(self, search, window=14444, id=''):
        search_result = []
        if id == '':
            for label in self.search_db.keys():
                if search.lower() in label.lower():
                    search_item = self.search_db[label]
                    search_result.append((label,search_item))

            for module in self.search_dynamic:
                if module in self.settings['modules_on']:
                    if self.debug:
                        searchlist = self.module_obj[module].Search(search)
                    else:
                        try:
                            searchlist = self.module_obj[module].Search(search)
                        except:
                            print 'A "Dynamic Search" error occured for the module: ' + module
                            searchlist = ba.CreateStream()

                    for item in searchlist:
                        label = ba.ConvertASCII(item.name)
                        search_item = ba.SearchData()
                        search_item.SetModule(module)
                        search_item.SetType(self.module_obj[module].type)
                        search_item.SetName(self.module_obj[module].name)
                        search_item.SetEpisode(item.episode)
                        search_item.SetId(item.id)
                        search_result.append((label,search_item))
        else:
            module = id
            if module not in self.search_dynamic:
                for label in self.search_db.keys():
                    if self.search_db[label].module == module:
                        if search.lower() in label.lower():
                            search_item = self.search_db[label]
                            search_result.append((label,search_item))
            else:
                if self.debug:
                    searchlist = self.module_obj[module].Search(search)
                else:
                    try:
                        searchlist = self.module_obj[module].Search(search)
                    except:
                        print 'A "Dynamic Search" error occured for the module: ' + module
                        searchlist = ba.CreateStream()

                for item in searchlist:
                    label = ba.ConvertASCII(item.name)
                    search_item = ba.SearchData()
                    search_item.SetModule(id)
                    search_item.SetType(self.module_obj[id].type)
                    search_item.SetName(self.module_obj[id].name)
                    search_item.SetEpisode(item.episode)
                    search_item.SetId(item.id)
                    search_result.append((label,search_item))

        search_result.sort(key=itemgetter(0))

        list = mc.GetWindow(window).GetList(51)
        focus = int(list.GetFocusedItem())

        list_items = mc.ListItems()

        for data in search_result:
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(str(data[0]))
            list_item.SetProperty('icon', str(os.path.join(self.module_path, data[1].module, data[1].module + '.png')))
            list_item.SetProperty('stream_id', str(binascii.hexlify(data[1].id)))
            list_item.SetProperty('module', str(data[1].module))
            list_item.SetProperty('type', str(data[1].type))
            list_item.SetProperty('name', str(data[1].name))
            list_item.SetProperty('episode', str(data[1].episode))
            list_items.append(list_item)
        list.SetItems(list_items)

        max = len(list_items) - 1
        if focus > 0 and focus < max:
            list.SetFocusedItem(focus)
        elif focus > max:
            list.SetFocusedItem(max)

    def Search_DB_Update(self, cachetime):
        mc.ShowDialogWait()
        if self.search_db == {}:
            if mc.GetApp().GetLocalConfig().GetValue('searchdb') != '':
                self.search_db = self.GetFromDB('searchdb')
                rebuild = False
            else:
                rebuild = True

        if len(self.settings['modules_on']) < 1 :
            mc.ShowDialogNotification("You can enable modules in the settings section")

        for module in self.module.keys():
            if module in self.settings['modules_on']:
                if not ba.Cache('searchdb_' + str(module), cachetime) or rebuild:
                    self.Search_DB_Add(module)
        mc.HideDialogWait()

    def Search_DB_Add(self, module):
        type = self.module_obj[module].type
        if 'search' in type:
            self.search_dynamic.append(module)
        elif 'list' in type:
            self.Search_DB_Remove(module)
            self.List(module)
            self.SaveToDB('searchdb', self.search_db)
        print "BARTSIDEE FRAMEWORK: Module " + str(module) + " added to the database."

    def Search_DB_Remove(self, module):
        for label in self.search_db.keys():
            search_item = self.search_db[label]
            if search_item.module == module:
                del self.search_db[label]
        self.SaveToDB('searchdb', self.search_db)
        print "BARTSIDEE FRAMEWORK: Module " + str(module) + " removed from database."

    def Search_History(self, index=0, search=''):
        data = bz2.decompress(binascii.unhexlify(mc.GetApp().GetLocalConfig().GetValue('search_history')))
        data = data.split('|')
        if search != '':
            if len(data) == 0:
                data = list()
                data.append(search)
            elif len(data) < 10:
                data.reverse()
                data.append(search)
                data.reverse()
            else:
                data.pop()
                data.reverse()
                data.append(search)
                data.reverse()
            string = ''
            for item in data:
                string = string + '|' + item
            mc.GetApp().GetLocalConfig().SetValue('search_history', binascii.hexlify(bz2.compress(string[1:-1])))
        else:
            if index < len(data):
                return data[int(index)]
            else:
                return str('')


    ##############################################################################
    ######   GUI FUNCTIONS
    ##############################################################################

    def GetModules(self):
        list = mc.GetWindow(14444).GetList(52)
        list_items = mc.ListItems()

        for module in self.module.keys():
            if module in self.settings['modules_on']:
                list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
                list_item.SetLabel(str(module))
                list_item.SetThumbnail(str(os.path.join(self.module_path, module, module + '.png')))
                list_items.append(list_item)
        list.SetItems(list_items)

    def GetSettings(self):
        list = mc.GetWindow(14444).GetList(53)
        list_items = mc.ListItems()

        for module in self.module.keys():
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(str(module))
            list_item.SetProperty('country', str(self.module_obj[module].country))
            if module in self.settings['modules_on']:
                list_item.SetThumbnail(str('gtk-apply.png'))
            else:
                list_item.SetThumbnail(str('gtk-close.png'))
            list_items.append(list_item)
        list.SetItems(list_items)


        list = mc.GetWindow(14444).GetList(54)
        list_items = mc.ListItems()

        options = {"subtitle":"Enable subtitles if available...","clear":"Clear the database"}
        for key in options.keys():
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(options[key])
            list_item.SetProperty('id', key)
            if key == "subtitle":
                if self.settings['subtitle']:
                    list_item.SetThumbnail(str('gtk-apply.png'))
                else:
                    list_item.SetThumbnail(str('gtk-close.png'))
            else:
                list_item.SetThumbnail(str('gtk-close.png'))
            list_items.append(list_item)
        list.SetItems(list_items)

    def GetApp(self, module):
        types = self.module_obj[module].type

        tmp_types = ['home', 'search']
        if 'list' in types: tmp_types.append('list')
        if 'genre' in types: tmp_types.append('genre')

        mc.GetWindow(14445).ClearStateStack(False)
        mc.ActivateWindow(14445)
        list = mc.GetWindow(14445).GetList(54)
        list_items = mc.ListItems()
        for type in tmp_types:
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(str(type))
            list_item.SetThumbnail(str(os.path.join(self.module_path, module, module + '.png')))
            list_item.SetProperty('name', str(self.module_obj[module].name))
            list_item.SetProperty('module', str(module))
            list_items.append(list_item)
        list.SetItems(list_items)
        list.SetFocusedItem(1)

    def GetList(self, module):
        list = mc.GetWindow(14445).GetList(52)
        list_items = mc.ListItems()

        list_result = []
        for label in self.search_db.keys():
            if self.search_db[label].module == module:
                list_item = self.search_db[label]
                list_result.append((label,list_item))
                
        list_result.sort(key=itemgetter(0))

        for data in list_result:
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(str(data[0]))
            list_item.SetProperty('icon', str(os.path.join(self.module_path, data[1].module, data[1].module + '.png')))
            list_item.SetProperty('stream_id', str(binascii.hexlify(data[1].id)))
            list_item.SetProperty('module', str(data[1].module))
            list_item.SetProperty('type', str(data[1].type))
            list_item.SetProperty('name', str(data[1].name))
            list_items.append(list_item)
        list.SetItems(list_items)

    def GetGenre(self, module):
        list = mc.GetWindow(14445).GetList(55)
        list_items = mc.ListItems()

        for genre in self.module_obj[module].genre:
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(str(genre))
            list_item.SetProperty('module', str(module))
            list_items.append(list_item)
        list.SetItems(list_items)

        list = mc.GetWindow(14445).GetList(56)
        list_items = mc.ListItems()

        filters = self.module_obj[module].filter
        if filters != []:
            filters.append('None')
            for filter in filters:
                list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
                list_item.SetLabel(ba.ConvertASCII(filter))
                list_items.append(list_item)
            list.SetItems(list_items)
