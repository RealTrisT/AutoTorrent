from urllib.parse import quote
from os import system, listdir
from config_parser import getSettings, setSettings
import sys
import requests

#   Return Values
##      -2 <=> maxattempts was exceeded
##      -1 <=> piratebay found no results for the search provided
##       0 <=> results were found but none met the criteria
#   Params
##      maxAttempts -> 0 for infinite, more for a limit
def get_ep_info(ep, uploader_list, searchUrl, maxAttempts = None, supressStatusCodeFailiure = None):
    if maxAttempts is None:                 #|------------------------------------------|
        maxAttempts = 0                     #|                                          |
    else:                                   #|           Python Is Fucking              |  .jpg
        maxAttempts += 1                    #|                Cancer                    |
    if supressStatusCodeFailiure is None:   #|                                          |
        supressStatusCodeFailiure = True    #|------------------------------------------|


    showinfo = ep['search_term']+' s'+str(ep['season']).zfill(2)+'e'+str(ep['episode']).zfill(2)

    r = requests.get(searchUrl+quote(showinfo, safe=''))
    while r.status_code != 200 and maxAttempts != 1:
        if not supressStatusCodeFailiure:
            print("Piratebay responded with status", str(r.status_code)+", retrying..")
        r = requests.get('https://pirateproxy.cam/search/'+quote(showinfo, safe=''))
        if maxAttempts != 0:
            maxAttempts -= 1
    if maxAttempts == 1:
        return -2


    if r.text.find('No hits. Try adding an asterisk in you search phrase.') != -1:
        #print('No results found for the "' + showinfo + '" entry')
        return -1


    variable_first = 0
    is_downloading = False
    while(r.text.find('<td>\n<div class="detName">', variable_first) != -1):
        res720or1080 = False
        uploaderName = ''
        magnetlink = ''
        variable_first = r.text.find('<td>\n<div class="detName">', variable_first)+1
        enderoni = r.text.find(' class="detLink" title', variable_first)
        if 'except' in ep:
            if isinstance(ep['except'], str):
                if r.text[variable_first:enderoni].find(ep['except']) != -1:
                    continue
            else:
                infilter = False
                for exception in ep['except']:
                    if r.text[variable_first:enderoni].find(exception) != -1:
                        infilter = True
                        break
                if infilter:
                    continue
        if r.text[variable_first:enderoni].find('720') == -1 and r.text[variable_first:enderoni].find('1080') == -1:
            res720or1080 = False
        else:
            res720or1080 = True
        uploaderName = r.text[r.text.find('<a class="detDesc" href="/user/', variable_first)+31:r.text.find('/" title="Browse ', variable_first)]
        magnetlink = r.text[r.text.find('</div>\n<a href="', variable_first)+16:r.text.find('" title="Download this torrent using magnet">', variable_first)]
        if (uploaderName in uploader_list) and (res720or1080 == True):
            return {'uploader':uploaderName, 'magnetlink':magnetlink, 'search_term':ep['search_term'], 'season':ep['season'], 'episode':ep['episode']}
    if is_downloading == False:
        #print("No Valid Entries Were Found For \"" + showinfo+ '"')
        return 0
    
def get_ep_info_checknext(show, lookAfterCount, uploader_list, searchUrl):
    show['episode'] = int(show['episode'])
    show['season'] = int(show['season'])
    gotShowInfo = False
    for i in range(0, lookAfterCount):
        showinforn = get_ep_info(show, uploader_list, searchUrl)
        if showinforn == 0:
            show['episode'] += 1
            continue
        elif showinforn == -1:
            return False
        elif showinforn == -2:
            return -1
        else:
            return showinforn
    return False

def download_ep(magnetlink, path, season, executeLocation, usage):
    final_string = usage.replace('"%location"', executeLocation).replace('%path', path+'\\S'+str(season).zfill(2)).replace('%torrent', magnetlink)
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
    #print(str(settings))

    fail_next_get_count = 3
    if len(sys.argv) > 2:
        fail_next_get_count = int(sys.argv[2])

    uploaderlist = []
    for uploadername in settings['uploader']:
        uploaderlist.append(uploadername['name'])
    for index, show in enumerate(settings['show']):
        alreadyExisting = 0
        skippedUnmetCriteria = 0
        downloaded = 0

        lastWorkingEp = show['episode'] = int(show['episode'])
        lastWorkingSe = show['season'] = int(show['season'])
        seasonSwitch = False
        while True:
            if (folderHasEp(show['save_directory']+'\\S'+str(show['season']).zfill(2), show['episode']) == True):
                print(show['search_term']+' s'+str(show['season']).zfill(2)+'e'+str(show['episode']).zfill(2) + ' Already Present.')#log--------------
                lastWorkingEp = show['episode']
                lastWorkingSe = show['season']
                show['episode'] += 1
                seasonSwitch = False
                alreadyExisting += 1
                continue
            showinfor = get_ep_info_checknext(show, fail_next_get_count, uploaderlist, settings['proxy'][0]['url'])
            if showinfor == -1:
                input('Exceeded Max Tries To Fech Page, Press Enter To Exit')
                return
            elif showinfor == False:
                if seasonSwitch == True:
                    settings['show'][index]['episode'] = str(lastWorkingEp).zfill(2)
                    settings['show'][index]['season'] = str(lastWorkingSe).zfill(2)
                    print('-----Finalized Search For ' + show['search_term'] + ' With a Last Valid Tor Of: s' + str(lastWorkingSe).zfill(2)+'e'+str(lastWorkingEp).zfill(2) + '-----'+
                          '\n-----> '+str(downloaded)+' downloaded, '+str(alreadyExisting) + ' already existed, ' + str(skippedUnmetCriteria) + ' skipped due to unmet criteria\n')#log--------------
                    break;
                show['season'] += 1
                show['episode'] = 1
                seasonSwitch = True
                continue
            else:
                skippedUnmetCriteria+=showinfor['episode']-show['episode']
                print('Fetching '+show['search_term']+' s'+str(showinfor['season']).zfill(2)+'e'+str(showinfor['episode']).zfill(2)+' from '+showinfor['uploader'])#log--------------
                download_ep(showinfor['magnetlink'], show['save_directory'], show['season'], settings['torclient'][0]['location'], settings['torclient'][0]['usage'])
                lastWorkingEp = showinfor['episode']
                lastWorkingSe = showinfor['season']
                show['episode'] = showinfor['episode']+1
                downloaded+=1
                seasonSwitch = False
       
    setSettings(sys.argv[1].replace('"', ''), settings)
    input("finished, enter to end it all")


if __name__ == "__main__":
    sys.exit(int(main() or 0))
