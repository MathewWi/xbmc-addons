#############################################################################
#
# Navi-X Playlist browser
# v2.7 by rodejo (rodejo16@gmail.com)
#
# -v1.01  (2007/04/01) first release
# -v1.2   (2007/05/10)
# -v1.21  (2007/05/20)
# -v1.22  (2007/05/26)
# -v1.3   (2007/06/15)
# -v1.31  (2007/06/30)
# -v1.4   (2007/07/04)
# -v1.4.1 (2007/07/21)
# -v1.5   (2007/09/14)
# -v1.5.1 (2007/09/17)
# -v1.5.2 (2007/09/22)
# -v1.6   (2007/09/29)
# -v1.6.1 (2007/10/19)
# -v1.7 beta (2007/11/14)
# -v1.7   (2007/11/xx)
# -v1.7.1 (2007/12/15)
# -v1.7.2 (2007/12/20)
# -v1.8 (2007/12/31)
# -v1.9 (2008/02/10)
# -v1.9.1 (2008/02/10)
# -v1.9.2 (2008/02/23)
# -v1.9.3 (2008/06/20)
# -v2.0   (2008/07/21)
# -v2.1   (2008/08/08)
# -v2.2   (2008/08/31)
# -v2.3   (2008/10/18)
# -v2.4   (2008/12/04)
# -v2.5   (2009/01/24)
# -v2.6   (2009/03/21)
# -v2.7   (2009/04/11)
#
# Changelog (v2.7)
# -Added new playlist item called 'processor'. Points to a playlist item processing server.
# -Youtube fix
# -Added PLX playlist multiline comment tag (""").
#
# Changelog (v2.6)
# -Added parental control.
# -Update Apple movie trailer. List shows new releases.
# -Solved problem with download + shutdown
#
# Changelog (v2.5)
# -Solved a problem in the script/plugin installer.
# -Added release date attribute for playlist item.
# -Improved thumb image loader (separate thread).
# -background downloading support.
# -Solved minor problems.
#
# Changelog (v2.4)
# -improved Shoutcast playlist loading.
# -improved PLX loading. Support both LF and CRLF.
# -Support new media type called 'plugin'. (plugin file needs to be a ZIP file).
# -Support description= field for every media item in PLX file.
# -Youtube fix.
#
# Changelog (v2.3)
# -Added new playlist "description=" element.
# -Youtube parser added playlist support.
# -Youtube parser fix.
# -Youtube long video name display.
# -Improved caching for a better user experience.
# -Apple movie trailer parser fix.
# -Other minor improvements.
#
# Changelog (v2.2)
# -Improved RSS reader to support image elements in XML file.
# -Y-button starts image slide show.
# -Youtube: Minor bug fixed HTML parser.
# -Apple movie trailers: Changed the sorting order to "release date".
# -Stability improvements.
#
# Changelog (v2.1)
# -Added a new type called 'download'. This type can be used to download
#  any type of file from a webserver to the XBOX (e.g a plugin rar file).
# -Improved text viewer: Added setting of text viewer background image
# -Improved RSS parser. Fix some problems and added thumb images.
# -Improved Youtube: Next page is now added to the existing page.
# -Minor problems solved.
# 
# Changelog (v2.0)
# - Youtube: Switched to high resolution mode. Also downloaded possible.
# - Added search history. Remembers last searches.
# - Updated context menu options (Play... and View...).
# - Added view mode option in menu: Ascencding/Descencing
# - Play using menu accessible via Y-button.
# - New playlist option called 'playmode. Example: 
#   playmode=autonext #plays all entries in playlist
#
#############################################################################

from string import *
import sys, os.path
import urllib
import re, random, string
import xbmc, xbmcgui
import re, os, time, datetime, traceback
import shutil
import zipfile
import copy
#import threading

sys.path.append(os.path.join(os.getcwd().replace(";",""),'src'))
from libs2 import *
from settings import *
from CPlayList import *
from CFileLoader import *
from CDownLoader import *
from CPlayer import *
from CDialogBrowse import *
from CTextView import *
from CInstaller import *
from skin import *
from CBackgroundLoader import *

try: Emulating = xbmcgui.Emulating
except: Emulating = False

RootDir = os.getcwd()
if RootDir[-1]==';': RootDir=RootDir[0:-1]
if RootDir[-1]!='\\': RootDir=RootDir+'\\'
imageDir = RootDir + "\\images\\"
cacheDir = RootDir + "\\cache\\"
imageCacheDir = RootDir + "\\cache\\imageview\\"
scriptDir = "Q:\\scripts\\"
myDownloadsDir = RootDir + "My Downloads\\"
initDir = RootDir + "\\init\\"
myPlaylistsDir = RootDir + "My Playlists\\"
srcDir = RootDir + "\\src\\"

######################################################################
# Description: Main Window class
######################################################################
class MainWindow(xbmcgui.Window):
        def __init__(self):
            if Emulating: xbmcgui.Window.__init__(self)
            if not Emulating:
                self.setCoordinateResolution(PAL_4x3)

            self.delFiles(cacheDir) #clear the cache first

            #Create default DIRs if not existing.
            if not os.path.exists(cacheDir): 
                os.mkdir(cacheDir) 
            if not os.path.exists(myDownloadsDir): 
                os.mkdir(myDownloadsDir)

            #load the screen widget elements from another file.
            load_skin(self)

            #Create playlist object contains the parsed playlist data. The self.list control displays
            #the content of this list
            self.playlist = CPlayList()
            #Create favorite object contains the parsed favorite data. The self.favorites control displays
            #the content of this list
            self.favoritelist = CPlayList()
            #fill the playlist with favorite data
            result = self.favoritelist.load_plx(favorite_file)
            if result != 0:
                shutil.copyfile(initDir+favorite_file, RootDir+favorite_file)
                self.favoritelist.load_plx(favorite_file)

            self.downloadslist = CPlayList()
            #fill the playlist with downloads data
            result = self.downloadslist.load_plx(downloads_complete)
            if result != 0:
                shutil.copyfile(initDir+downloads_complete, RootDir+downloads_complete)
                self.downloadslist.load_plx(downloads_complete)

            self.downloadqueue = CPlayList()
            #fill the playlist with downloads data
            result = self.downloadqueue.load_plx(downloads_queue)
            if result != 0:
                shutil.copyfile(initDir+downloads_queue, RootDir+downloads_queue)
                self.downloadqueue.load_plx(downloads_queue)
                
            self.parentlist = CPlayList()
            #fill the playlist with downloads data
            result = self.parentlist.load_plx(parent_list)
            if result != 0:
                shutil.copyfile(initDir+parent_list, RootDir+parent_list)
                self.parentlist.load_plx(parent_list)                
                          
            #check if My Playlists exists, otherwise copy it from the init dir
            if not os.path.exists(myPlaylistsDir + "My Playlists.plx"): 
                shutil.copyfile(initDir+"My Playlists.plx", myPlaylistsDir+"My Playlists.plx")

            #check if My Playlists exists, otherwise copy it from the init dir
            if not os.path.exists(myPlaylistsDir + "My Playlists.plx"): 
                shutil.copyfile(initDir+"My Playlists.plx", myPlaylistsDir+"My Playlists.plx")
            
            #check if My skin file exists, otherwise copy it from the init dir
#            if not os.path.exists(srcDir + "skin.py"): 
#                shutil.copyfile(initDir+"skin.py", srcDir+"skin.py")

            #Create the downloader object
            #self.downloader = CDownLoader(self.downloadqueue, self.downloadslist)
            
            #Next a number of class private variables
            self.home=home_URL
            self.dwnlddir=myDownloadsDir
            self.History = [] #contains the browse history
            self.history_count = 0 #number of entries in history array
            self.background = 0 #background image
            self.userthumb = '' #user thumb image at bottom left of screen
            self.state_busy = 0 # key handling busy state
            self.state2_busy = 0 # logo update busy state
            self.URL='http://'
            self.type=''
            self.player_core=xbmc.PLAYER_CORE_AUTO #default
            self.pl_focus = self.playlist
            self.downlshutdown = False # shutdown after download flag
            self.mediaitem = 0
            #self.logo_visible = False # true if logo shall be displayed
            self.thumb_visible = False # true if thumb shall be displayed
            self.vieworder = 'ascending' #ascending
            self.SearchHistory = [] #contains the search history
            self.background = '' #current background image
            self.password = "" #parental control password.
            self.access = False #parental control access.
            
            self.loader = CFileLoader() #create file loader instance
            
            #read the non volatile settings from the settings.dat file
            self.onReadSettings()
            
            #read the search history from the search.dat file
            self.onReadSearchHistory()
 
            #check if the home playlist points to the old website. If true then update the home URL.
            if self.home == home_URL_old:
                self.home = home_URL
                        
            #thumb update task
            self.bkgndloadertask = CBackgroundLoader(window=self)
            self.bkgndloadertask.start()
            
            #background download task
            self.downloader = CDownLoader(window=self, playlist_src=self.downloadqueue, playlist_dst=self.downloadslist)
            self.downloader.start()
    
            #parse the home URL
            result = self.ParsePlaylist(URL=self.home)
            if result != 0: #failed
                self.ParsePlaylist(URL=home_URL_mirror) #mirror site

#            xbmc.executebuiltin("xbmc.ActivateWindow(VideoOverlay)")
                    
            #end of function

        ######################################################################
        # Description: Handles key events.
        # Parameters : action=user action
        # Return     : -
        ######################################################################
        def onAction(self, action):
            self.state_action = 1
                     
            if action == ACTION_PREVIOUS_MENU:
                self.setInfoText("Shutting Down Navi-X...") 
                self.onSaveSettings()
                self.delFiles(cacheDir) #clear the cache first
                self.bkgndloadertask.kill()
                self.bkgndloadertask.join(10) #timeout after 10 seconds.
                self.downloader.kill()
                self.downloader.join(10) #timeout after 10 seconds.
                
                self.close() #exit
                
            if self.state_busy == 0:
                if action == ACTION_SELECT_ITEM:
                    #main list
                    if self.getFocus() == self.list:
                        #if self.URL == favorite_file:
                        if self.pl_focus == self.favoritelist:
                            self.onSelectFavorites()
                        elif (self.URL == downloads_file) or (self.URL == downloads_queue) or \
                              (self.URL == downloads_complete) or (self.URL == parent_list):
                            self.onSelectDownloads()
                        else:
                            pos = self.list.getSelectedPosition()
                            if pos >= 0:
                                self.SelectItem(self.playlist, pos)
                    #home button
                    elif self.getFocus() == self.button_home:
                        self.pl_focus = self.playlist
                        self.ParsePlaylist(URL=self.home)
                    #favorite button
                    elif self.getFocus() == self.button_favorites:
                        self.onOpenFavorites()
                    #downloads button
                    elif self.getFocus() == self.button_downloads:
                        self.onOpenDownloads()
                    #URL button
                    elif self.getFocus() == self.button_url:
                        self.onSelectURL()
                    elif self.getFocus() == self.button_about:
                        self.OpenTextFile('readme.txt')
                elif action == ACTION_PARENT_DIR:
                    if self.state_busy == 0:        
                        if self.pl_focus == self.favoritelist:
                            self.onCloseFavorites()
                        elif (self.URL == downloads_queue) or (self.URL == downloads_complete) or (self.URL == parent_list):    
                            self.onCloseDownloads()
                        else:
                            #main list
                            if self.history_count > 0:
                                previous = self.History[len(self.History)-1]
                                result = self.ParsePlaylist(mediaitem=previous.mediaitem, start_index=previous.index, proxy="ENABLED")
                                if result == 0: #success
                                    flush = self.History.pop()
                                    self.history_count = self.history_count - 1
                elif action == ACTION_YBUTTON:
                    self.onPlayUsing()
                elif action == ACTION_MOVE_RIGHT:
                    if self.getFocus() == self.list:
                        self.onShowDescription()
                    else:                   
                        self.setFocus(self.list)
                elif self.ChkContextMenu(action) == True: #White
                    if self.URL == favorite_file:
                        self.selectBoxFavoriteList()
                    elif  (self.URL == downloads_file) or (self.URL == downloads_queue) or \
                           (self.URL == downloads_complete) or (self.URL == parent_list):
                        self.selectBoxDownloadsList()
                    else:
                        self.selectBoxMainList()
                
                #update index number    
                pos = self.list.getSelectedPosition()
                self.listpos.setLabel(str(pos+1) + '/' + str(self.list.size()))
                              
            #end of function
             
    
        ######################################################################
        # Description: Checks if one of the context menu keys is pressed.
        # Parameters : action=handle to UI control
        # Return     : True if valid context menu key is pressed.
        ######################################################################
        def ChkContextMenu(self, action):
            result = False
               
            #Support for different remote controls.
        
            if action == 261:
                result = True
            elif action == ACTION_CONTEXT_MENU:
                result = True
            elif action == ACTION_CONTEXT_MENU2:
                result = True
            
            return result

        ######################################################################
        # Description: Handles UI events.
        # Parameters : control=handle to UI control
        # Return     : -
        ######################################################################
        def onControl(self, control):
            #Nothing to do for now.
            if control == self.list:
                self.setFocus(self.list)
                                                          
        ######################################################################
        # Description: Parse playlist file. Playlist file can be a:
        #              -PLX file;
        #              -RSS v2.0 file (e.g. podcasts);
        #              -RSS daily Flick file (XML1.0);
        #              -html Youtube file;
        # Parameters : URL (optional) =URL of the playlist file.
        #              mediaitem (optional)=Playlist mediaitem containing 
        #              playlist info. Replaces URL parameter.
        #              start_index (optional) = cursor position after loading 
        #              playlist.
        #              reload (optional)= indicates if the playlist shall be 
        #              reloaded or only displayed.
        # Return     : 0 on success, -1 if failed.
        ######################################################################
        def ParsePlaylist(self, URL='', mediaitem=CMediaItem(), start_index=0, reload=True, proxy="CACHING"):
            #avoid recursive call of this function by setting state to busy.
            self.state_busy = 1

            #The application contains 4 CPlayList objects:
            #(1)main list, 
            #(2)favorites,
            #(3)download queue
            #(4)download completed list
            #Parameter 'self.pl_focus' points to the playlist in focus (1-4).
            playlist = self.pl_focus

            #The application contains one xbmcgui list control which displays 
            #the playlist in focus. 
            listcontrol = self.list

            listcontrol.setVisible(0)
            self.list2tb.setVisible(0)
            
            self.loading.setVisible(1)
            
            type = mediaitem.type
            if reload == True:
                #load the playlist
                if type == 'rss':
                    result = playlist.load_rss_20(URL, mediaitem, proxy)
                elif type == 'rss_flickr_daily':
                    result = playlist.load_rss_flickr_daily(URL, mediaitem, proxy)
                elif type == 'html_youtube':
                    result = playlist.load_html_youtube(URL, mediaitem, proxy)
                elif type == 'xml_shoutcast':
                    result = playlist.load_xml_shoutcast(URL, mediaitem, proxy)
                elif type == 'xml_applemovie':
                    result = playlist.load_xml_applemovie(URL, mediaitem, proxy)
                elif type == 'directory':
                    result = playlist.load_dir(URL, mediaitem, proxy)
                else: #assume playlist file
                    result = playlist.load_plx(URL, mediaitem, proxy)
                
                if result == -1: #error
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "This playlist requires a newer Navi-X version")
                elif result == -2: #error
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "The requested file could not be opened.")
                
                if result != 0: #failure
                    self.loading.setVisible(0)
                    listcontrol.setVisible(1)
                    self.setFocus(listcontrol)
                    self.state_busy = 0            
                    return -1
            
            #succesful
            playlist.save(RootDir + 'source.plx')
            
            self.vieworder = 'ascending' #ascending by default
        
            if start_index == 0: 
                start_index = playlist.start_index
        
            self.URL = playlist.URL
            self.type = type
            if URL != '':
                mediaitem.URL = URL
            self.mediaitem = mediaitem
                        
            #display the new URL on top of the screen
            if len(playlist.title) > 0:
                title = playlist.title + ' - (' + playlist.URL + ')'
            else:
                title = playlist.URL
            self.urllbl.setLabel(title)

            #set the background image
            m = self.playlist.background
            if m != self.background:
                if m == 'default': #default BG image
                    self.bg.setImage(imageDir + "background.png")
                    self.background = m
                elif m != 'previous': #URL to image located elsewhere
                    ext = getFileExtension(m)
                    loader = CFileLoader2() #file loader
                    loader.load(m, cacheDir + "background." + ext, timeout=2, proxy="ENABLED", content_type='image')
                    if loader.state == 0:
                        self.bg.setImage(loader.localfile)
                    self.background = m
                                 
            #loading was successful
            listcontrol.reset() #clear the list control view
            
            if playlist.description != "":
                self.list = self.list2
                listcontrol = self.list2
            else:
                self.list = self.list1
                listcontrol = self.list1

            self.list2tb.controlDown(self.list)
            
            #fill the main list
            i=0
            today=datetime.date.today()
            for m in playlist.list:         
                if int(m.version) <= int(plxVersion):
                    thumb = self.getPlEntryThumb(m.type)
                    
                    #check if playlist item is on located in the blacklist
#                    if self.access == False:
                    for n in self.parentlist.list:
                        if n.URL == m.URL:
                            if self.access == False:
                                thumb = imageDir+'lock-icon.png'
                            else:
                                thumb = imageDir+'unlock-icon.png'
                            break
                        
                    
                    label2=''
                    if m.date != '':
                        #entry_date = datetime.date(int(m.date[:4]), int(m.date[5:7]), int(m.date[8:]))
                        l=m.date.split('-')
                        entry_date = datetime.date(int(l[0]), int(l[1]), int(l[2]))
                        days_past = (today-entry_date).days
                        if days_past <= 10:
                            if days_past <= 0:
                                label2 = 'NEW today'
                            elif days_past == 1:
                                label2 = 'NEW yesterday'
                            else:
                                label2 = 'NEW ('+ str(days_past) + ' days ago)'
                    
                    if m.description != '':
                        label2 = label2 + ' >'
                        
                    
                    #item = xbmcgui.ListItem(m.name, label2 ,"", thumb)
                    item = xbmcgui.ListItem(unicode(m.name, "utf-8" ), label2 ,"", thumb)
                    listcontrol.addItem(item)                    
                    i=i+1
 
            #fill the main list description text box
#            if playlist.description != "":
#                self.list2tb.reset()
#                self.list2tb.setText(playlist.description)
                
            listcontrol.selectItem(start_index)
            self.loading.setVisible(0)
            listcontrol.setVisible(1)
            
            self.setFocus(listcontrol)

            pos = self.list.getSelectedPosition()
            self.listpos.setLabel(str(pos+1) + '/' + str(self.list.size()))
                 
            if playlist.description != '':
                self.list2tb.reset()
                self.list2tb.setText(playlist.description)
                self.list2tb.setVisible(1)      
           
            self.state_busy = 0
            
            return 0 #success

        ######################################################################
        # Description: Gets the playlist entry thumb image for different types
        # Parameters : type = playlist entry type
        # Return     : thumb image (local) file name
        ######################################################################
        def getPlEntryThumb(self, type):
            if type == 'rss_flickr_daily':
                return imageDir+'icon_rss.png'
            elif type == 'xml_applemovie':
                return imageDir+'icon_playlist.png'
            elif type == 'html_youtube':
                return imageDir+'icon_playlist.png'
            elif type == 'search_youtube':
                return imageDir+'icon_search.png'
            elif type == 'xml_shoutcast':
                return imageDir+'icon_playlist.png'
            elif type == 'search_shoutcast':
                return imageDir+'icon_search.png'
            elif type == 'directory':
                return imageDir+'icon_playlist.png'
            elif type[0:6] == 'script':
                return imageDir+'icon_script.png'               
            elif type[0:6] == 'plugin':
                return imageDir+'icon_script.png'
                
            return imageDir+'icon_'+str(type)+'.png'
                
        ######################################################################
        # Description: Handles the selection of an item in the list.
        # Parameters : playlist(optional)=the source playlist;
        #              pos(optional)=media item position in the playlist;
        #              append(optional)=true is playlist must be added to 
        #              history list;
        #              URL(optional)=link to media file;
        # Return     : -
        ######################################################################
        def SelectItem(self, playlist=0, pos=0, append=True, iURL=''):
            if iURL != '':
                mediaitem=CMediaItem()
                mediaitem.URL = iURL
                ext = getFileExtension(iURL)
                if ext == 'plx':
                    mediaitem.type = 'playlist'
                elif ext == 'xml':
                    mediaitem.type = 'rss'
                elif ext == 'jpg' or ext == 'png' or ext == 'gif':
                    mediaitem.type = 'image'
                elif ext == 'txt':
                    mediaitem.type == 'text'
                elif ext == 'zip':
                    mediaitem.type == 'script'
                else:
                    mediaitem.type = 'video' #same as audio
            else:
                if playlist.size() == 0:
                    #playlist is empty
                    return
               
                mediaitem = playlist.list[pos]
            
            #check if playlist item is on located in the blacklist
            if self.access == False:
                for m in self.parentlist.list:
                    if m.URL == mediaitem.URL:
                        if self.verifyPassword() == False:
                            return                    
            
            self.state_busy = 1                
            
            type = mediaitem.type
            if type == 'playlist' or type == 'favorite' or type == 'rss' or \
               type == 'rss_flickr_daily' or type == 'directory' or \
               type == 'html_youtube' or type == 'xml_shoutcast' or \
               type == 'xml_applemovie':
                #add new URL to the history array
                tmp = CHistorytem() #new history item
                tmp.index = self.list.getSelectedPosition()
                tmp.mediaitem = self.mediaitem

                #exception case: Do not add Youtube pages to history list
                if self.mediaitem.type == 'html_youtube':
                    append = False
            
                self.pl_focus = self.playlist #switch back to main list
                result = self.ParsePlaylist(mediaitem=mediaitem)
                
                if result == 0 and append == True: #successful
                    self.History.append(tmp)
                    self.history_count = self.history_count + 1

            elif type == 'video' or type == 'audio' or type == 'html':
#these lines are used for debugging only
#                self.onDownload()
#                self.state_busy = 0
#                self.selectBoxMainList()
#                self.state_busy = 0                
#                return
                
                self.setInfoText("Loading... ") #loading text

                if (playlist != 0) and (playlist.playmode == 'autonext'):
                    size = playlist.size()
                    if playlist.player == 'mplayer':
                        MyPlayer = CPlayer(xbmc.PLAYER_CORE_MPLAYER, function=self.myPlayerChanged)
                    elif playlist.player == 'dvdplayer':
                        MyPlayer = CPlayer(xbmc.PLAYER_CORE_DVDPLAYER, function=self.myPlayerChanged)
                    else:
                        MyPlayer = CPlayer(self.player_core, function=self.myPlayerChanged)                
                    result = MyPlayer.play(playlist, pos, size-1)
                else:
                    if mediaitem.player == 'mplayer':
                        MyPlayer = CPlayer(xbmc.PLAYER_CORE_MPLAYER, function=self.myPlayerChanged)
                    elif mediaitem.player == 'dvdplayer':
                        MyPlayer = CPlayer(xbmc.PLAYER_CORE_DVDPLAYER, function=self.myPlayerChanged)
                    else:
                        MyPlayer = CPlayer(self.player_core, function=self.myPlayerChanged)
#####################Start modification Navi-Xtreme
#todo: move to separate class                   
                    if mediaitem.processor != '':
                        self.setInfoText("Processor: getting filter...")
                        (URL,filt)=get_HTML(mediaitem.processor+'?url='+urllib.quote_plus(mediaitem.URL)).splitlines()
                        self.setInfoText("Processor: scraping...")
                        htm=get_HTML(URL)
                        p=re.compile(filt)
                        match=p.search(htm)
                        if match:
                            tgt=mediaitem.processor
                            sep='?'
                            for i in range(1,len(match.groups())+1):
                                val=urllib.quote_plus(match.group(i))
                                tgt=tgt+sep+'v'+str(i)+'='+val
                                sep='&'
                            self.setInfoText("Processor: processing...")
                            arr=get_HTML(tgt).splitlines()
                            mediaitem.URL=arr[0]
                            if len(arr)>1:
                                mediaitem.swfplayer=arr[1]
                                mediaitem.playpath=arr[2]
                            mediaitem.processor=''
                        self.setInfoText("Loading... ")
#####################End modification Navi-Xtreme                      
                        
                    result = MyPlayer.play_URL(mediaitem.URL)
                
                self.setInfoText(visible=0)
                
                if result != 0:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "Could not open file.")
            elif type == 'image':
                self.viewImage(playlist, pos, 0, mediaitem.URL) #single file show
            elif type == 'text':
                self.OpenTextFile(mediaitem=mediaitem)
            elif type[0:6] == 'script' or type[0:6] == 'plugin':
                self.InstallApp(mediaitem=mediaitem)
#                self.InstallScript(mediaitem.URL)
            elif type == 'download':
                self.onDownload()
            elif type == 'search_youtube' or type == 'search_shoutcast':
                self.PlaylistSearch(mediaitem, append)
#            elif type == 'html':
#                #at this moment we do nothing with HTML files
                pass
            else:
                dialog = xbmcgui.Dialog()
                dialog.ok("Playlist format error", '"' + type + '"' + " is not a valid type.")
                
            self.state_busy = 0

        ######################################################################
        # Description: Player changed info can be catched here
        # Parameters : action=user key action
        # Return     : -
        ######################################################################
        def myPlayerChanged(self, state):
            #At this moment nothing to handle.
            pass

        ######################################################################
        # Description: view HTML page.
        # Parameters : URL: URL to the page.
        # Return     : -
        ######################################################################
        def viewHTML(self, URL):
            #At this moment we do not support HTML display.
            dialog = xbmcgui.Dialog()
            dialog.ok("HTML is not supported.")

        ######################################################################
        # Description: Handles the player selection menu which allows the user
        #              to select the player core to use for playback.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onPlayUsing(self):
            pos = self.list.getSelectedPosition()
            if pos < 0: #invalid position
                return
                
            mediaitem = self.pl_focus.list[pos]
            URL = self.pl_focus.list[pos].URL
            autonext = False

            #check if the cursor is on a image
            if mediaitem.type == 'image':
                self.viewImage(self.pl_focus, pos, 1) #slide show show
                return
            
            #not on an image, check if video or audio file
            if (mediaitem.type != 'video') and (mediaitem.type != 'audio'):
                dialog = xbmcgui.Dialog()
                dialog.ok("Error", "Not a video, audio or image file.")
                return

            possibleChoices = ["Default Player", \
                               "Default Player (Auto Next)", \
                               "DVD Player", \
                               "DVD Player (Auto Next)", \
                               "MPlayer", \
                               "MPlayer (Auto Next)", \
                               "Cancel"]
            dialog = xbmcgui.Dialog()
            choice = dialog.select("Play...", possibleChoices)
            
            if (choice != -1) and (choice < 6): #if not cancel
                result = 0            
                if (choice == 0) or (choice == 1):
                    if mediaitem.player == 'mplayer':
                        MyPlayer = CPlayer(xbmc.PLAYER_CORE_MPLAYER, function=self.myPlayerChanged)
                    elif mediaitem.player == 'dvdplayer':
                        MyPlayer = CPlayer(xbmc.PLAYER_CORE_DVDPLAYER, function=self.myPlayerChanged)
                    else:
                        MyPlayer = CPlayer(self.player_core, function=self.myPlayerChanged)                
                elif (choice == 2) or (choice == 3):
                    MyPlayer = CPlayer(xbmc.PLAYER_CORE_DVDPLAYER, function=self.myPlayerChanged)
                elif (choice == 4) or (choice == 5):
                    MyPlayer = CPlayer(xbmc.PLAYER_CORE_MPLAYER, function=self.myPlayerChanged)

                if (choice == 1) or (choice == 3) or (choice == 5):
                    autonext = True

                self.setInfoText("Loading...") 
                if autonext == False:
                    result = MyPlayer.play_URL(URL) 
                else:
                    size = self.pl_focus.size()
                    #play from current position to end of list.
                    result = MyPlayer.play(self.pl_focus, pos, size-1)                    
                self.setInfoText(visible=0)
                
                if result != 0:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "Could not play file.")

        ######################################################################
        # Description: Handles the view selection menu.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onView(self):
            possibleChoices = ["Ascending (default)", \
                               "Descending",\
                               "Cancel"]
            dialog = xbmcgui.Dialog()
            choice = dialog.select("View...", possibleChoices)
            
            if (choice == 0) and (self.vieworder != 'ascending'): #Ascending
                self.ParsePlaylist(mediaitem=self.mediaitem)
                self.vieworder = 'ascending'
            elif (choice == 1) and (self.vieworder != 'descending'): #Descending
                size = self.pl_focus.size()
                for i in range(size/2):
                    item = self.pl_focus.list[i]
                    self.pl_focus.list[i] = self.pl_focus.list[size-1-i]
                    self.pl_focus.list[size-1-i] = item
                self.ParsePlaylist(mediaitem=self.mediaitem, reload=False) #display download list
                self.vieworder = 'descending'
            
        ######################################################################
        # Description: Handles display of a text file.
        # Parameters : URL=URL to the text file.
        # Return     : -
        ######################################################################
        def OpenTextFile( self, URL='', mediaitem=CMediaItem()):
            self.setInfoText("Loading...") #loading text on
                    
            if (mediaitem.background == 'default') and (self.pl_focus.background != 'default'):
                mediaitem = copy.copy(mediaitem)
                mediaitem.background = self.pl_focus.background
            
#            Trace(URL + " " + self.pl_focus.background)
            
            textwnd = CTextView()
            result = textwnd.OpenDocument(URL, mediaitem)
            self.setInfoText(visible=0) #loading text off            

            if result == 0:
                textwnd.doModal()
            else:
                dialog = xbmcgui.Dialog()
                dialog.ok("Error", "Could not open file.")
                
        ######################################################################
        # Description: Handles image slideshow.
        # Parameters : playlist=the source playlist
        #              pos=media item position in the playlist
        #              mode=view mode (0=slideshow, 1=recursive slideshow)
        #              URL(optional) = URL to image
        # Return     : -
        ######################################################################
        def viewImage(self, playlist, pos, mode, iURL=''):
            self.setInfoText("Loading...")
            #clear the imageview cache
            self.delFiles(imageCacheDir)

            if not os.path.exists(imageCacheDir): 
                os.mkdir(imageCacheDir) 

            if mode == 0: #single file show
                localfile= imageCacheDir + '0.'
                if iURL != '':
                    URL = iURL
                else:    
                    URL = playlist.list[pos].URL
                ext = getFileExtension(URL)

                if URL[:4] == 'http':
                    self.loader.load(URL, localfile + ext, proxy="DISABLED")
                    if self.loader.state == 0:
                        xbmc.executebuiltin('xbmc.slideshow(' + imageCacheDir + ')')
                    else:
                        dialog = xbmcgui.Dialog()
                        dialog.ok("Error", "Unable to open image.")
                else:
                    #local file
                    shutil.copyfile(URL, localfile + ext)
                    xbmc.executebuiltin('xbmc.slideshow(' + imageCacheDir + ')')
            
            elif mode == 1: #recursive slideshow
                #in case of slideshow store default image
                count=0
                for i in range(self.list.size()):
                    if playlist.list[i].type == 'image':
                        localfile=imageCacheDir+'%d.'%(count)
                        URL = playlist.list[i].URL
                        ext = getFileExtension(URL)
                        shutil.copyfile(imageDir+'imageview.png', localfile + ext)
                        count = count + 1
                if count > 0:
                    count = 0
                    index = pos
                    for i in range(self.list.size()):
                        if count == 2:
                            xbmc.executebuiltin('xbmc.recursiveslideshow(' + imageCacheDir + ')')
                            self.state_action = 0
                        elif (count > 2) and (self.state_action == 1):
                            break
                            
                        if playlist.list[index].type == 'image':
                            localfile=imageCacheDir+'%d.'%(count)
                            URL = playlist.list[index].URL
                            ext = getFileExtension(URL)
                            self.loader.load(URL, localfile + ext, proxy="DISABLED")
                            if self.loader.state == 0:
                                count = count + 1
                        index = (index + 1) % self.list.size()

                    if self.list.size() < 3:
                        #start the slideshow after the first two files. load the remaining files
                        #in the background
                        xbmc.executebuiltin('xbmc.recursiveslideshow(' + imageCacheDir + ')')
                if count == 0:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "No images in playlist.")
            
            self.setInfoText(visible=0)
            
        ######################################################################
        # Description: Handles Installation of Applications
        # Parameters : URL=URL to the script ZIP file.
        # Return     : -
        ######################################################################
        def InstallApp( self, URL='', mediaitem=CMediaItem()):
            dialog = xbmcgui.Dialog()
            if mediaitem.type[0:6] == 'script':
                index=mediaitem.type.find(":")
                if index != -1:
                    type = mediaitem.type[index+1:]
                else:
                    type = ''
                if dialog.yesno("Message", "Install Script?") == False:
                    return
                self.setInfoText("Installing...")
                installer = CInstaller()
                result = installer.InstallScript(URL, mediaitem)

            elif mediaitem.type[0:6] == 'plugin':
                index=mediaitem.type.find(":")
                if index != -1:
                    type = mediaitem.type[index+1:] + " "
                else:
                    type = ''
                if dialog.yesno("Message", "Install " + type + "Plugin?") == False:
                    return
                self.setInfoText("Installing...")
                installer = CInstaller()
                result = installer.InstallPlugin(URL, mediaitem)
            else:
                result = -1 #failure
            
            self.setInfoText(visible=0)
            
            if result == 0:
                dialog.ok(" Installer", "Installation successful.")
                if type == 'navi-x':
                    dialog.ok(" Installer", "Please restart Navi-X.")
            elif result == -1:
                dialog.ok(" Installer", "Installation aborted.")
            elif result == -3:
                dialog.ok(" Installer", "Invalid ZIP file.")
            else:
                dialog.ok(" Installer", "Installation failed.")
                
        ######################################################################
        # Description: Handle selection of playlist search item (e.g. Youtube)
        # Parameters : item=CMediaItem
        #              append(optional)=true is playlist must be added to 
        #              history list;
        # Return     : -
        ######################################################################
        def PlaylistSearch(self, item, append):
            possibleChoices = []
            possibleChoices.append("New Search")
            for m in self.SearchHistory:
                possibleChoices.append(m)
            possibleChoices.append("Cancel")                
            dialog = xbmcgui.Dialog()
            choice = dialog.select("Search", possibleChoices)

            if (choice == -1) or (choice == (len(possibleChoices)-1)):
                return #canceled

            if choice > 0:
                string = self.SearchHistory[choice-1]
            else:  #New search
                string = ''
            
            keyboard = xbmc.Keyboard(string, 'Search')
            keyboard.doModal()
            if (keyboard.isConfirmed() == False):
                return #canceled
            searchstring = keyboard.getText()
            if len(searchstring) == 0:
                return  #empty string search, cancel
            
            #if search string is different then we add it to the history list.
            if searchstring != string:
                self.SearchHistory.insert(0,searchstring)
                if len(self.SearchHistory) > 8: #maximum 8 items
                    self.SearchHistory.pop()
                self.onSaveSearchHistory()
        
            #youtube search
            if item.type == 'search_youtube':
                fn = searchstring.replace(' ','+')
                if item.URL != '':
                    URL = item.URL
                else:
                    URL = 'http://www.youtube.com/results?search_query='
                URL = URL + fn
                  
                #ask the end user how to sort
                possibleChoices = ["Relevance", "Date Added", "View Count", "Rating"]
                dialog = xbmcgui.Dialog()
                choice = dialog.select("Sort by", possibleChoices)

                #validate the selected item
                if choice == 1: #Date Added
                    URL = URL + '&search_sort=video_date_uploaded'
                elif choice == 2: #View Count
                    URL = URL + '&search_sort=video_view_count'
                elif choice == 3: #Rating
                    URL = URL + '&search_sort=video_avg_rating'
               
                mediaitem=CMediaItem()
                mediaitem.URL = URL
                mediaitem.type = 'html_youtube'
                mediaitem.name = 'search results: ' + searchstring
                mediaitem.player = item.player

                #create history item
                tmp = CHistorytem()
                tmp.index = self.list.getSelectedPosition()
                tmp.mediaitem = self.mediaitem

                self.pl_focus = self.playlist
                result = self.ParsePlaylist(mediaitem=mediaitem)
                
                if result == 0 and append == True: #successful
                    self.History.append(tmp)
                    self.history_count = self.history_count + 1
            elif item.type == 'search_shoutcast':
                    fn=searchstring
                    URL = 'http://www.shoutcast.com/sbin/newxml.phtml?search='
                    URL = URL + fn
        
                    mediaitem=CMediaItem()
                    mediaitem.URL = URL
                    mediaitem.type = 'xml_shoutcast'
                    mediaitem.name = 'search results: ' + searchstring
                    mediaitem.player = item.player

                    #create history item
                    tmp = CHistorytem()
                    tmp.index = self.list.getSelectedPosition()
                    tmp.mediaitem = self.mediaitem

                    self.pl_focus = self.playlist
                    result = self.ParsePlaylist(mediaitem=mediaitem)
                
                    if result == 0 and append == True: #successful
                        self.History.append(tmp)
                        self.history_count = self.history_count + 1
            elif item.type == 'search_flickr':
                    fn = searchstring.replace(' ','+')
                    URL = 'http://www.flickr.com/search/?q='
                    URL = URL + fn
        
                    mediaitem=CMediaItem()
                    mediaitem.URL = URL
                    mediaitem.type = 'html_flickr'
                    mediaitem.name = 'search results: ' + searchstring
                    mediaitem.player = item.player

                    #create history item
                    tmp = CHistorytem()
                    tmp.index = self.list.getSelectedPosition()
                    tmp.mediaitem = self.mediaitem

                    self.pl_focus = self.playlist
                    result = self.ParsePlaylist(mediaitem=mediaitem)
                
                    if result == 0 and append == True: #successful
                        self.History.append(tmp)
                        self.history_count = self.history_count + 1

        ######################################################################
        # Description: Handles selection of 'Browse' button.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onSelectURL(self):
            browsewnd = CDialogBrowse()
            browsewnd.SetFile('', self.URL, 1)
            browsewnd.doModal()
            
            if browsewnd.state != 0:
                return
        
            self.pl_focus = self.playlist
        
            self.URL = browsewnd.dir + browsewnd.filename
            
            self.SelectItem(iURL=self.URL)
            
            
        ######################################################################
        # Description: Handles selection of 'Favorite' button.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onOpenFavorites(self):
            #Select the favorite playlist.
            self.pl_focus = self.favoritelist
              
            #Show the favorite list
            self.ParsePlaylist(reload=False) #display favorite list

        ######################################################################
        # Description: Handles selection within favorite list.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onSelectFavorites(self):
            if self.favoritelist.size() == 0:
                #playlist is empty
                return
            
            pos = self.list.getSelectedPosition()
            self.SelectItem(self.favoritelist, pos, append=False)

        ######################################################################
        # Description: Handles closing of the favorite list.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onCloseFavorites(self):
            #Select the main playlist.
            self.pl_focus = self.playlist
        
            self.ParsePlaylist(reload=False) #display main list

        ######################################################################
        # Description: Handles context menu within favorite list
        # Parameters : -
        # Return     : -
        ######################################################################
        def selectBoxFavoriteList(self):
            possibleChoices = ["Play...", \
                               "Move Item Up", \
                               "Move Item Down", \
                               "Remove Item", \
                               "Rename", \
                               "Set Playlist as Home", \
                               "Cancel"]
            dialog = xbmcgui.Dialog()
            choice = dialog.select("Select", possibleChoices)

            if self.favoritelist.size() == 0:
                #playlist is empty
                return
            
            #validate the selected item
            if choice == 0: #Play...
                self.onPlayUsing()
            elif choice == 1: #Move Item Up
                pos = self.list.getSelectedPosition()
                if pos > 0:
                    item = self.favoritelist.list[pos-1]
                    self.favoritelist.list[pos-1] = self.favoritelist.list[pos]
                    self.favoritelist.list[pos] = item
                    self.favoritelist.save(RootDir + favorite_file)
                    self.ParsePlaylist(reload=False) #display download list
                    self.list.selectItem(pos-1)
            elif choice == 2: #Move Item Down
                pos = self.list.getSelectedPosition()
                if pos < (self.list.size())-1:
                    item = self.favoritelist.list[pos+1]
                    self.favoritelist.list[pos+1] = self.favoritelist.list[pos]
                    self.favoritelist.list[pos] = item
                    self.favoritelist.save(RootDir + favorite_file)
                    self.ParsePlaylist(reload=False) #display download list
                    self.list.selectItem(pos+1)
            elif choice == 3: #Remove Item
                pos = self.list.getSelectedPosition()
                self.favoritelist.remove(pos)
                self.favoritelist.save(RootDir + favorite_file)
                self.ParsePlaylist(reload=False) #display favorite list
            elif choice == 4: #Rename
                pos = self.list.getSelectedPosition()
                item = self.favoritelist.list[pos]
                keyboard = xbmc.Keyboard(item.name, 'Rename')
                keyboard.doModal()
                if (keyboard.isConfirmed() == True):
                    item.name = keyboard.getText()
                    self.favoritelist.save(RootDir + favorite_file)
                    self.ParsePlaylist(reload=False) #display favorite list
            elif choice == 5: #Set playlist as home
                if dialog.yesno("Message", "Overwrite current Home playlist?") == False:
                    return
                self.home = self.URL
            
        ######################################################################
        # Description: Handles selection of the 'downloads' button.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onOpenDownloads(self):
            #select main playlist
            self.pl_focus = self.playlist
            self.SelectItem(iURL=downloads_file)
         
        ######################################################################
        # Description: Handles selection within download list.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onSelectDownloads(self):
            if self.URL == downloads_file:
                pos = self.list.getSelectedPosition()
                if pos >= 0:
                    if pos == 0:
                        #Select the DL queue playlist.
                        self.pl_focus = self.downloadqueue
                        #fill and show the download queue
                        self.ParsePlaylist(reload=False) #display download list
                    elif pos == 1:
                        #Select the download list playlist.
                        self.pl_focus = self.downloadslist
                        #fill and show the downloads list
                        self.ParsePlaylist(reload=False) #display download list
                    elif pos == 2:
                        #first check password
                        if self.access == True:
                            #Select the parent list playlist.
                            self.pl_focus = self.parentlist
                            #fill and show the downloads list
                            self.ParsePlaylist(reload=False) #display download list
                        else:
                            if (self.password == '') or (self.verifyPassword() == True):
                                self.access = True #access granted
                                #Select the parent list playlist.
                                self.pl_focus = self.parentlist
                                #fill and show the downloads list
                                self.ParsePlaylist(reload=False) #display download list
            elif self.URL == downloads_queue: #download queue
                if self.downloadqueue.size() == 0:
                    #playlist is empty
                    return
            
                pos = self.list.getSelectedPosition()          
                self.SelectItem(self.downloadqueue, pos, append=False)
            elif self.URL == downloads_complete: #download completed
                if self.downloadslist.size() == 0:
                    #playlist is empty
                    return
             
                pos = self.list.getSelectedPosition()
                self.SelectItem(self.downloadslist, pos, append=False)
            
            else: #parent list playlists
                if self.parentlist.size() == 0:
                    #playlist is empty
                    return      
                                
                pos = self.list.getSelectedPosition()
                self.SelectItem(self.parentlist, pos, append=False)
            
        ######################################################################
        # Description: Handles closing of the downloads list.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onCloseDownloads(self):
            #select main playlist
            self.pl_focus = self.playlist
            
            self.ParsePlaylist(reload=False) #display main list

        ######################################################################
        # Description: Handles context menu within download list
        # Parameters : -
        # Return     : -
        ######################################################################
        def selectBoxDownloadsList(self):
            if self.URL == downloads_file:
                return #no menu
            elif self.URL == downloads_queue:
                possibleChoices = ["Download Queue", \
                                   "Download Queue + Shutdown", \
                                   "Stop Downloading", \
                                   "Move Item Up", \
                                   "Move Item Down", \
                                   "Remove Item", \
                                   "Clear List", \
                                   "Cancel"]
                dialog = xbmcgui.Dialog()
                choice = dialog.select("Select", possibleChoices)
            
                if self.downloadqueue.size() == 0:
                    #playlist is empty
                    return
            
                #validate the selected item
                if choice == 0 or choice == 1: #Download Queue / Shutdown
                    self.downlshutdown = False #Reset flag
                    if choice == 1: #Download Queue + Shutdown
                        self.downlshutdown = True #Set flag
                    
                    #Download all files in the queue (background)
                    self.downloader.download_start(self.downlshutdown)
                elif choice == 2: #Stop Downloading
                    self.downloader.download_stop()                   
                elif choice == 3: #Move Item Up
                    pos = self.list.getSelectedPosition()
                    if pos > 0:
                        item = self.downloadqueue.list[pos-1]
                        self.downloadqueue.list[pos-1] = self.downloadqueue.list[pos]
                        self.downloadqueue.list[pos] = item
                        self.downloadqueue.save(RootDir + downloads_queue)
                        self.ParsePlaylist(reload=False) #display download list
                        self.list.selectItem(pos-1)
                elif choice == 4: #Move Item Down
                    pos = self.list.getSelectedPosition()
                    if pos < (self.list.size())-1:
                        item = self.downloadqueue.list[pos+1]
                        self.downloadqueue.list[pos+1] = self.downloadqueue.list[pos]
                        self.downloadqueue.list[pos] = item
                        self.downloadqueue.save(RootDir + downloads_queue)
                        self.ParsePlaylist(reload=False) #display download list
                        self.list.selectItem(pos+1)                        
                elif choice == 5: #Remove
                    pos = self.list.getSelectedPosition()
                    self.downloadqueue.remove(pos)
                    self.downloadqueue.save(RootDir + downloads_queue)
                    self.ParsePlaylist(reload=False) #display download list
                elif choice == 6: #Clear List
                    self.downloadqueue.clear()
                    self.downloadqueue.save(RootDir + downloads_queue)
                    self.ParsePlaylist(reload=False) #display download list
            elif self.URL == downloads_complete: #download completed
                possibleChoices = ["Play...", "Remove Item", "Clear List", "Delete Item", "Cancel"]
                dialog = xbmcgui.Dialog()
                choice = dialog.select("Select", possibleChoices)
            
                if self.downloadslist.size() == 0:
                    #playlist is empty
                    return
            
                #validate the selected item
                if choice == 0: #Play...
                    self.onPlayUsing()
                elif choice == 1: #Remove
                    pos = self.list.getSelectedPosition()
                    self.downloadslist.remove(pos)
                    self.downloadslist.save(RootDir + downloads_complete)
                    self.ParsePlaylist(reload=False) #display download list
                elif choice == 2: #Clear List
                    self.downloadslist.clear()
                    self.downloadslist.save(RootDir + downloads_complete)
                    self.ParsePlaylist(reload=False) #display download list
                elif choice == 3: #Delete
                    pos = self.list.getSelectedPosition()            
                    URL = self.downloadslist.list[pos].URL
                    dialog = xbmcgui.Dialog()                 
                    if dialog.yesno("Message", "Delete file from disk?", URL) == True:
                        if os.path.exists(URL):
                            try:        
                                os.remove(URL)
                            except IOError:
                                pass
                            
                        self.downloadslist.remove(pos)
                        self.downloadslist.save(RootDir + downloads_complete)
                        self.ParsePlaylist(reload=False) #display download list
            else: #parent list
                #first check password before opening list
                possibleChoices = ["Set Password", "Remove Item", "Clear List", "Cancel"]
                dialog = xbmcgui.Dialog()
                choice = dialog.select("Select", possibleChoices)
            
                if (choice > 0) and (self.parentlist.size() == 0):
                    #playlist is empty
                    return
            
                #validate the selected item
                if choice == 0: #Set password
                    keyboard = xbmc.Keyboard(self.password, 'Set Password')
                    keyboard.doModal()
                    if (keyboard.isConfirmed() == True):
                        self.password = keyboard.getText()
                        self.onSaveSettings()
                        self.access = False
                        dialog = xbmcgui.Dialog()
                        dialog.ok("Message", "Password changed.")
                        self.ParsePlaylist(reload=False) #refresh
                elif choice == 1: #Remove
                    pos = self.list.getSelectedPosition()
                    self.parentlist.remove(pos)
                    self.parentlist.save(RootDir + parent_list)
                    self.ParsePlaylist(reload=False) #display download list
                elif choice == 2: #Clear List
                    self.parentlist.clear()
                    self.parentlist.save(RootDir + parent_list)
                    self.ParsePlaylist(reload=False) #refresh

        ######################################################################
        # Description: Handle download context menu in main list.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onDownload(self):
            self.state_busy = 1 #busy
            
            #first check if URL is a remote location
            pos = self.list.getSelectedPosition()
            entry = copy.copy(self.pl_focus.list[pos])

            #if the entry has no thumb then use the logo
            if (entry.thumb == "default") and (self.pl_focus.logo != "none"):
                entry.thumb = self.pl_focus.logo
            
            if entry.URL[:4] != 'http':
                dialog = xbmcgui.Dialog()
                dialog.ok("Error", "Cannot download file.")                    
                self.state_busy = 0 #busy
                return

            possibleChoices = ["Download", "Download + Shutdown", "Cancel"]
            dialog = xbmcgui.Dialog()
            choice = dialog.select("Download...", possibleChoices)
                       
            if (choice != -1) and (choice < 2):
                self.downlshutdown = False #Reset flag
                if choice == 1:
                    self.downlshutdown = True #Set flag
                   
                #select destination location for the file.
                self.downloader.browse(entry, self.dwnlddir)

                if self.downloader.state == 0:
                    #update download dir setting
                    self.dwnlddir = self.downloader.dir
                    
                    #Get playlist entry
                    #Set the download location field.
                    entry.DLloc = self.downloader.localfile
                
                    self.downloader.add_queue(entry)
                        
                    self.downloader.download_start(self.downlshutdown)
              
                elif self.downloader.state == -1:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "Could not locate file.")
                    
            self.state_busy = 0 #not busy            

    
        ######################################################################
        # Description: Handles selection of the 'black' button in the main list.
        #              This will open a selection window.
        # Parameters : -
        # Return     : -
        ######################################################################
        def selectBoxMainList(self):
            possibleChoices = ["Download...", \
                                "Play...", \
                                "View...", \
                                "Image Slideshow", \
                                "Add Selected Item to Favorites", \
                                "Add Playlist to Favorites", \
                                "Set Playlist as Home", \
                                "View Playlist Source", \
                                "Parental Control Block Selected Item", \
                                "Cancel"]
            dialog = xbmcgui.Dialog()
            choice = dialog.select("Select", possibleChoices)
            
            if choice == 0: #Download
                self.onDownload()
            elif choice == 1: #play...
                self.onPlayUsing()
            elif choice == 2: #view...
                self.onView()
            elif choice == 3: #Slideshow
                pos = self.list.getSelectedPosition()            
                self.viewImage(self.playlist, pos, 1) #slide show show
            elif choice == 4: #Add selected file to Favorites
                pos = self.list.getSelectedPosition()
                tmp = CMediaItem() #create new item
                tmp.type = self.playlist.list[pos].type
                keyboard = xbmc.Keyboard(self.playlist.list[pos].name, 'Add to Favorites')
                keyboard.doModal()
                if (keyboard.isConfirmed() == True):
                    tmp.name = keyboard.getText()
                else:
                    tmp.name = self.playlist.list[pos].name
                tmp.thumb = self.playlist.list[pos].thumb
                if tmp.thumb == 'default' and self.playlist.logo != 'none':
                    tmp.thumb = self.playlist.logo
                tmp.URL = self.playlist.list[pos].URL
                tmp.player = self.playlist.list[pos].player
                self.favoritelist.add(tmp)
                self.favoritelist.save(RootDir + favorite_file)
            elif choice == 5: #Add playlist to Favorites
                tmp = CMediaItem() #create new item
                tmp.type = self.mediaitem.type
                keyboard = xbmc.Keyboard(self.playlist.title, 'Add to Favorites')
                keyboard.doModal()
                if (keyboard.isConfirmed() == True):
                    tmp.name = keyboard.getText()
                else:
                    tmp.name = self.playlist.title
                if self.playlist.logo != 'none':
                    tmp.thumb = self.playlist.logo
                tmp.URL = self.URL
                tmp.player = self.mediaitem.player
                tmp.background = self.mediaitem.background
                self.favoritelist.add(tmp)
                self.favoritelist.save(RootDir + favorite_file)
            elif choice == 6: #Set Playlist as Home
                if dialog.yesno("Message", "Overwrite current Home playlist?") == False:
                    return
                self.home = self.URL
 #               self.onSaveSettings()
            elif choice == 7: #View playlist source
                self.OpenTextFile(RootDir + "source.plx")
            elif choice == 8: #Block selected playlist
                pos = self.list.getSelectedPosition()
                tmp = CMediaItem() #create new item
                tmp.type = self.playlist.list[pos].type
#                keyboard = xbmc.Keyboard(self.playlist.list[pos].name, 'Block playlist')
#                keyboard.doModal()
#                if (keyboard.isConfirmed() == True):
#                    tmp.name = keyboard.getText()
#                else:
                tmp.name = self.playlist.list[pos].name
                tmp.thumb = self.playlist.list[pos].thumb
                if tmp.thumb == 'default' and self.playlist.logo != 'none':
                    tmp.thumb = self.playlist.logo
                tmp.URL = self.playlist.list[pos].URL
                tmp.player = self.playlist.list[pos].player
                self.parentlist.add(tmp)
                self.parentlist.save(RootDir + parent_list)
                self.ParsePlaylist(reload=False) #refresh

        ######################################################################
        # Description: Parental Control verify password.
        # Parameters : -
        # Return     : -
        ######################################################################
        def verifyPassword(self):       
            keyboard = xbmc.Keyboard("", 'Enter Password')
            keyboard.doModal()
            if (keyboard.isConfirmed() == True):
                if self.password == keyboard.getText():
                    self.access = True #access granted
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Message", "Navi-X Unlocked.")
                    return True
                else:
                      dialog = xbmcgui.Dialog()
                      dialog.ok("Error", "Wrong password. Access denied.")
            return False

        ######################################################################
        # Description: Read the home URL from disk. Called at program init. 
        # Parameters : -
        # Return     : -
        ######################################################################
        def onReadSettings(self):
            try:
                f=open(RootDir + 'settings.dat', 'r')
                data = f.read()
                data = data.split('\n')
                home=data[0]
                self.home=home
                self.dwnlddir=data[1]
                self.password=data[2]
                f.close()
            except IOError:
                return

        ######################################################################
        # Description: Saves the home URL to disk. Called at program exit. 
        # Parameters : -
        # Return     : -
        ######################################################################
        def onSaveSettings(self):
            f=open(RootDir + 'settings.dat', 'w')
            f.write(self.home + '\n')
            f.write(self.dwnlddir + '\n')
            f.write(self.password + '\n')
            f.close()

        ######################################################################
        # Description: Read the home URL from disk. Called at program init. 
        # Parameters : -
        # Return     : -
        ######################################################################
        def onReadSearchHistory(self):
            try:
                f=open(RootDir + 'search.dat', 'r')
                data = f.read()
                data = data.split('\n')
                for m in data:
                    if len(m) > 0:
                        self.SearchHistory.append(m)
                f.close()
            except IOError:
                return

        ######################################################################
        # Description: Saves the home URL to disk. Called at program exit. 
        # Parameters : -
        # Return     : -
        ######################################################################
        def onSaveSearchHistory(self):
            try:
                f=open(RootDir + 'search.dat', 'w')
                for m in self.SearchHistory:
                    f.write(m + '\n')
                f.close()
            except IOError:
                return

        ######################################################################
        # Description: Deletes all files in a given folder and sub-folders.
        #              Note that the sub-folders itself are not deleted.
        # Parameters : folder=path to local folder
        # Return     : -
        ######################################################################
        def delFiles(self, folder):
            try:        
                for root, dirs, files in os.walk(folder , topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
            except IOError:
                return
                    

        ######################################################################
        # Description: Controls the info text label on the left bottom side
        #              of the screen.
        # Parameters : folder=path to local folder
        # Return     : -
        ######################################################################
        def setInfoText(self, text='', visible=1):
            if visible == 1:
                self.infotekst.setLabel(text)
                self.infotekst.setVisible(1)
            else:
                self.infotekst.setVisible(0)
                
        ######################################################################
        # Description: Controls the info text label on the left bottom side
        #              of the screen.
        # Parameters : folder=path to local folder
        # Return     : -
        ######################################################################                        
        def onShowDescription(self):      
            pos = self.list.getSelectedPosition()
            if pos < 0: #invalid position
                return
                
            mediaitem = self.pl_focus.list[pos]
            if mediaitem.description != '':
                #description = re.sub("&lt; */? *\w+ */?\ *&gt;", "", mediaitem.description)
                            
                description = re.sub("&lt;.*&gt;", "", mediaitem.description)              
                description = re.sub(r'<[^>]*?>', '', description) 
 
                try:
                    f=open(cacheDir + 'description.dat', 'w')
                    f.write(description + '\n')
                    #f.write('ronald \n')
                    #f.write(mediaitem.description + '\n')
                    
                    f.close()
                except IOError:
                    return
            
                self.OpenTextFile(cacheDir + 'description.dat', mediaitem)
                

win = MainWindow()
win.doModal()
del win
