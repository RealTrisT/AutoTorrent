def getPropriety(text, tag):
    if text.find(' '+tag+'=\'') != -1:
        begin = text.find(' '+tag+'=\'')+3+len(tag)
        if begin == -1:
            return False
        tempbegin = begin
        end = 0
        while text.find('\'', tempbegin) != -1:
            tempbegin = text.find('\'', tempbegin)+1
            if text[tempbegin-1-1:tempbegin-1] == '\\':
                continue
            else:
                end = tempbegin-1
                break
        if end == 0:
            return False
        return text[begin:end]

def getSettings( configFileDirectory ): #I will probably make something more automated in the future without hardcoded tag names, but with only the 6hrs experience of python I have it's gonna have to wait
    returnObject = {
        'torclient':{
            'location':'', 
            'usage':''}, 
        'uploaderlist':[],
        'showlist':[]
        }
    try:
        configFile = open( configFileDirectory, 'r+')
    except IOError:
        print('could not open file')
        return False
    for line in configFile.readlines():
        if line[:10] == '<torclient':
            returnObject['torclient']['location'] = getPropriety(line, 'location')
            returnObject['torclient']['usage'] = getPropriety(line, 'usage')
        elif line[:9] == '<uploader':
            returnObject['uploaderlist'].append(getPropriety(line, 'name'))
        elif line[:5] == '<show':
            returnObject['showlist'].append({
                    'search_term':getPropriety(line, 'search_term'), 
                    'season':getPropriety(line, 'season'), 
                    'episode':getPropriety(line, 'episode'),
                    'save_directory':getPropriety(line, 'save_directory')
                    })
    configFile.close()
    return returnObject

def setSettings (configFileDirectory, settings):    #same here
    try:
        configFile = open( configFileDirectory, 'w')
    except IOError:
        print('could not open file')
        return False
    configFile.write('<torclient location=\''+settings['torclient']['location']+'\' usage=\''+settings['torclient']['usage']+'\'>\n')
    for uploader in settings['uploaderlist']:
        configFile.write('<uploader name=\''+uploader+'\'>\n')
    for show in settings['showlist']:
        configFile.write ('<show search_term=\''+show['search_term']+'\' season=\''+str(show['season']).zfill(2)+'\' episode=\''+str(show['episode']).zfill(2)+'\' save_directory=\''+show['save_directory']+'\'>\n')