import sys, os, re
import xbmc
def dirEntries( dir_name, media_type="files", recursive="False" ):
    '''Returns a list of valid XBMC files from a given directory(folder)
       
       Method to call:
       dirEntries( dir_name, media_type, recursive )
            dir_name   - the name of the directory to be searched
            media_type - valid types: video music pictures files programs
            recursive  - Setting to "True" searches Parent and subdirectories, Setting to "False" only search Parent Directory
    '''
    fileList = []
    json_query = '{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "%s", "media": "%s", "recursive": "%s"}, "id": 1}' % ( dir_name, media_type, recursive )
    json_folder_detail = xbmc.executeJSONRPC(json_query)
    file_detail = re.compile( "{(.*?)}", re.DOTALL ).findall(json_folder_detail)
    for f in file_detail:
        match = re.search( '"file" : "(.*?)",', f )
        if match:
            if ( match.group(1).endswith( "/" ) or match.group(1).endswith( "\\" ) ):
                fileList.extend(dirEntries( match.group(1), media_type, recursive ))
            else:
                fileList.append(match.group(1))
        else:
            continue
    return fileList
