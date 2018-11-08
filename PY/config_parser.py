def getPropriety(text, tag):
    if text.find(' '+tag+'=\'') != -1: #if Propriety exists
        begin = text.find(' '+tag+'=\'')+3+len(tag) #set begin to the beginning of the Propriety's value
        tempbegin = begin
        end = 0
        while text.find('\'', tempbegin) != -1: #while there are apostrophes after the beginning of the Propriety's value
            tempbegin = text.find('\'', tempbegin)+1    #set tempbegin to apostrophe found
            if text[tempbegin-1-1:tempbegin-1] == '\\': #if there's a backslash before the apostrophe, discard
                continue
            else:
                end = tempbegin-1                       #otherwise set it to the end of the propriety
                break
        if end == 0:
            return False
        return text[begin:end]

def getProprietyList(text):
    returnal = {}
    proprietyLocation = 0
    proprietyLocation = text.find(' ', proprietyLocation)     #find first propriety
    while proprietyLocation != -1:                              #while there are spaces outside propriety value (while there are propreties)
        beginindex = text.find('=\'', proprietyLocation)+2      #find the begin of the propriety's value
        
        if beginindex == -1:                    #if we had just found a random space at the end of the line or something, break
            break

        foundEnd = False
        tempend = text.find('\'', beginindex)  #find potential end of propriety value
        while tempend != -1:                    #while there's potential ends of propriety value
            if text[tempend-1:tempend] == '\\': #check if before the apostrophe there's a backslash (which would indicate such apostrophe isn't the end of the propriety's value)
                tempend = text.find('\'', tempend+1)   #find next potential end of propriety value and repeat
                continue
            else:                               #theres no escape backslash, this is the end of the propriety's value
                foundEnd = True
                break
        if foundEnd:                    #all good
            if text[beginindex:tempend].find(';') != -1:        #if it has ';'s, which would mean it's a multi-value value
                returnal[text[proprietyLocation+1:beginindex-2]] = text[beginindex:tempend].split(';')  #set it to an array of multiple values
            else:
                returnal[text[proprietyLocation+1:beginindex-2]] = text[beginindex:tempend] #set dictionary key to it's value
        else:                           #it's all fucked, user is a fuckface who can't follow simple instructions on how to write a config file
            return False
        proprietyLocation = text.find(' ', tempend)   #find next propriety
    return returnal                     #if no tags are found empty dictionaries evaluate to False anyway so all good



def getSettings( configFileDirectory ): 
    returnObject = {}

    try:
        configFile = open( configFileDirectory, 'r+')
    except IOError:
        print('could not open file')
        return False


    for line in configFile.readlines():
        tagbegin = line.find('<')+1
        tagend = line.find(' ', tagbegin)
        if tagbegin == -1 or tagend == -1:  #it's either just a newline or user is fucked in the head kek
            continue
        tag = line[tagbegin:tagend] #get tag name
        if tag not in returnObject: #if tag is a key in the return object, create a key with a tag's name and assign an empty list to it (to contain however many instances of that tag there may be)
            returnObject[tag] = []
        returnObject[tag].append(getProprietyList(line)) #push a dictionary containing the proprieties of the tag into the list

    configFile.close()
    return returnObject



def setSettings (configFileDirectory, settings):
    try:
        configFile = open( configFileDirectory, 'w')
    except IOError:
        print('could not open file')
        return False

    for key, value in settings.items():
        if not value:
            continue
        for tagEntry in value:
            if not tagEntry:
                continue
            configFile.write('<' + key)
            for subkey, subvalue in tagEntry.items():
                if isinstance(subvalue, str):
                    configFile.write(' ' + subkey + '=\'' + subvalue + '\'')
                else:
                    configFile.write(' ' + subkey + '=\'')
                    for index, subvalueEntry in enumerate(subvalue):
                        if index:
                            configFile.write(';')
                        configFile.write(subvalueEntry)
                    configFile.write('\'')
            configFile.write('>\n')
    configFile.close()
