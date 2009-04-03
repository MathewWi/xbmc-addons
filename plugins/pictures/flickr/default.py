"""
    Plugin for viewing content from flickr.com
"""

# main imports
import sys
import xbmc

# plugin constants
__plugin__ = "flickr"
__author__ = "nuka1195"
__url__ = "http://code.google.com/p/xbmc-addons/"
__svn_url__ = "http://xbmc-addons.googlecode.com/svn/trunk/plugins/pictures/flickr"
__version__ = "1.5.1"

xbmc.log( "[PLUGIN] '%s: version %s' initialized!" % ( __plugin__, __version__, ), xbmc.LOGNOTICE )


if ( __name__ == "__main__" ):
    if ( not sys.argv[ 2 ] ):
        from FlickrAPI import xbmcplugin_categories as plugin
    elif ( "category='presets_photos'" in sys.argv[ 2 ] ):
        from FlickrAPI import xbmcplugin_categories as plugin
    elif ( "category='presets_groups'" in sys.argv[ 2 ] ):
        from FlickrAPI import xbmcplugin_categories as plugin
    elif ( "category='presets_users'" in sys.argv[ 2 ] ):
        from FlickrAPI import xbmcplugin_categories as plugin
    elif ( "authorize=True" in sys.argv[ 2 ] ):
        from FlickrAPI import xbmcplugin_categories as plugin
    else:
        from FlickrAPI import xbmcplugin_pictures as plugin
    plugin.Main()
