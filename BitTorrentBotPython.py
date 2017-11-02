from urllib.parse import quote
from os import system, listdir
from config_parser import getSettings, setSettings
import sys
import requests

fail_next_get_count = 3 #default amount of episodes its gonna search for before changing season if one is not found

def get_ep_info(showname, showseason, showep, uploader_list):
    showinfo = showname+' s'+str(showseason).zfill(2)+'e'+str(showep).zfill(2)

    r = requests.get('https://pirateproxy.cam/search/'+quote(showinfo, safe=''))
    while r.status_code != 200:
        print("Piratebay responded with status", str(r.status_code)+", retrying..")
        r = requests.get('https://pirateproxy.cam/search/'+quote(showinfo, safe=''))


    if r.text.find('No hits. Try adding an asterisk in you search phrase.') != -1:
        print('No results found for the "' + showinfo + '" entry')
        return False
        return


    variable_first = 0
    is_downloading = False
    while(r.text.find('<td>\n<div class="detName">', variable_first) != -1):
        res720or1080 = False
        uploaderName = ''
        magnetlink = ''
        variable_first = r.text.find('<td>\n<div class="detName">', variable_first)+1
        if r.text[variable_first:r.text.find(' class="detLink" title', variable_first)].find('720') == -1 and r.text[variable_first:r.text.find(' class="detLink" title', variable_first)].find('1080') == -1:
            res720or1080 = False
        else:
            res720or1080 = True
        uploaderName = r.text[r.text.find('<a class="detDesc" href="/user/', variable_first)+31:r.text.find('/" title="Browse ', variable_first)]
        magnetlink = r.text[r.text.find('</div>\n<a href="', variable_first)+16:r.text.find('" title="Download this torrent using magnet">', variable_first)]
        if (uploaderName in uploader_list) and (res720or1080 == True):
            return {'uploader':uploaderName, 'magnetlink':magnetlink, 'search_term':showname, 'season':showseason, 'episode':showep}
    if is_downloading == False:
        print("No Valid Entries Were Found For \"" + showinfo+ '"')
        return False
    
def get_ep_info_checknext(show, lookAfterCount, uploader_list):
    show['episode'] = int(show['episode'])
    show['season'] = int(show['season'])
    gotShowInfo = False
    for i in range(0, lookAfterCount):
        showinforn = get_ep_info(show['search_term'], show['season'], show['episode']+i, uploader_list)
        if showinforn == False:
            continue
        else:
            return showinforn
    return False

def download_ep(magnetlink, path, showseason, executeLocation, usage):
    final_string = usage.replace('"%location"', executeLocation).replace('%path', path+'\\S'+str(showseason).zfill(2)).replace('%torrent', magnetlink)
    system(final_string)
    return True

def folderHasEp(path, ep):
    try:
        for file in listdir(path):
            if file.lower().find('e'+str(ep).zfill(2)) != -1:
                return True
    except (NotADirectoryError, FileNotFoundError):
        return False
    return False

def main():
    if len(sys.argv) < 2:
        print('No Startup Args With Cfg File')
        return 0
    settings = getSettings(sys.argv[1].replace('"', ''))
    if settings == False:
        return 0
    if len(sys.argv) > 2:
        fail_next_get_count = int(sys.argv[2])

    
    for index, show in enumerate(settings['showlist']):
        lastWorkingEp = show['episode'] = int(show['episode'])
        lastWorkingSe = show['season'] = int(show['season'])
        seasonSwitch = False
        while True:
            if folderHasEp(show['save_directory']+'\\S'+str(show['season']).zfill(2), show['episode']) == True:
                print(show['search_term']+' s'+str(show['season']).zfill(2)+'e'+str(show['episode']).zfill(2) + ' Already Present.')#log--------------
                show['episode'] += 1
                continue
            showinfor = get_ep_info_checknext(show, fail_next_get_count, settings['uploaderlist'])
            if showinfor == False:
                if seasonSwitch == True:
                    settings['showlist'][index]['episode'] = str(lastWorkingEp).zfill(2)
                    settings['showlist'][index]['season'] = str(lastWorkingSe).zfill(2)
                    print('-----------Finalized Search For ' + show['search_term'] + ' With a Last Valid Tor Of: s' + str(lastWorkingSe).zfill(2)+'e'+str(lastWorkingEp).zfill(2) + '------------')#log--------------
                    break;
                show['season'] += 1
                show['episode'] = 1
                seasonSwitch = True
                continue
            else:
                print('Fetching '+show['search_term']+' s'+str(showinfor['season']).zfill(2)+'e'+str(showinfor['episode']).zfill(2)+' from '+showinfor['uploader'])#log--------------
                download_ep(showinfor['magnetlink'], show['save_directory'], show['season'], settings['torclient']['location'], settings['torclient']['usage'])
                lastWorkingEp = showinfor['episode']
                lastWorkingSe = showinfor['season']
                show['episode'] = showinfor['episode']+1
                seasonSwitch = False
       
    setSettings(sys.argv[1].replace('"', ''), settings)
    input("finished, enter to end it all")


if __name__ == "__main__":
    sys.exit(int(main() or 0))
