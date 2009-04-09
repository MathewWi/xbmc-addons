"""
    Plugin for viewing content from Youtube.com
"""

# main imports
import sys
import xbmc

# plugin constants
__plugin__ = "YouTube"
__author__ = "nuka1195"
__url__ = "http://code.google.com/p/xbmc-addons/"
__svn_url__ = "http://xbmc-addons.googlecode.com/svn/trunk/plugins/video/YouTube"
__version__ = "1.5.1"

xbmc.log( "[PLUGIN] '%s: version %s' initialized!" % ( __plugin__, __version__, ), xbmc.LOGNOTICE )


if ( __name__ == "__main__" ):
    if ( not sys.argv[ 2 ] ):
        from YoutubeAPI import xbmcplugin_categories as plugin
    elif ( "category='presets_videos'" in sys.argv[ 2 ] ):
        from YoutubeAPI import xbmcplugin_categories as plugin
    elif ( "category='presets_users'" in sys.argv[ 2 ] ):
        from YoutubeAPI import xbmcplugin_categories as plugin
    elif ( "category='play_video_by_id'" in sys.argv[ 2 ] ):
        from YoutubeAPI import xbmcplugin_player_by_id as plugin
    elif ( "category='play_video'" in sys.argv[ 2 ] ):
        from YoutubeAPI import xbmcplugin_player as plugin
    elif ( "category='download_video'" in sys.argv[ 2 ] ):
        from YoutubeAPI import xbmcplugin_download as plugin
    else:
        from YoutubeAPI import xbmcplugin_videos as plugin
    plugin.Main()
