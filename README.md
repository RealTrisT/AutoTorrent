# AutoTorrent

So this is a python project that, given a config file, will search for shows and their episodes, and set a torrent client to downoad those.

Here is a [video](https://youtu.be/cdxfx8k-CqM) showcasing an early version (hardcoded uploader names and individual download). Possibly another one will come out showing the full thing, along with me adding a batch/powershell script to scheduele running this every few hours or so.

# How it Works

Basically you make a config file such as this one (details on how to make one further down):
![alt text](https://i.imgur.com/uTZKQAh.png)

And it will search piratebay for the episodes. Upon not finding any further episodes, it will go to the next season, and if none are found in the next season, it goes onto the next show.

In order to use it, one's got to make a config file, and start the script with it as a command line argument.



# Config Files

It's simple enough really, you have 3 tags:
- proxy
- torclient
- uploader
- show
  
### proxy

It only has one propriety which is `url`, this is just the part of the url to put before the search, since sometimes proxies go down and different proxies have different search methods (some by get, some by page).
Just put whatever part of the url comes before of the search tem there. For example, `https://thepiratebay.blue/s/?q=`or `https://pirateproxy.pw/search/`.
  
### torclient
torclient has 2 proprieties:
  - location : path to your torrent client install
  - usage : the way to call such client with command line arguments, there are 3 constants that get replaced there:
    - %location : first propriety of this tag
    - %path : save path for your torrent, it will set to that directory `\S(number of the season)`, so, if path is `mySeries\worstComedyShow`, it will put an episode, for example episode 5 of season 3, in `mySeries\worstComedyShow\S03\torrent-file-of-episode-5`
    - %torrent : magnet link, as in `magnet:?xt=urn:` etc..
    
    
### uploader
uploader only has on propriety, which is 'name' : put the name of a whitelisted uploader inside there, and do as many instances of the tag as uploaders you want to white list


### show
oh boy Imma have to write a bit here, and ur gonna have to read
so proprieties:
  - search_term
  - season
  - episode
  - save_directory
  - except[optional]
  
##### search_term
so, the script searches for "value of search_term" S"season, zero padded"E"episode, zero padded"
all it is really is what you'd search if you'd gone to piratebay yourself, so, if you want "shitshow s01e01", search_term would just be "shitshow"

##### season
pretty self explanatory tbh, pad with zeros for a total of 2 characters, if you need an example: season 3 would be "03"

##### episode
same as season, except episode

##### save_directory
path to where your show is, so say you want episode 5 to be in "mySeries\worstComedyShow\S03\torrent-file-of-episode-5", you'd do "mySeries\worstComedyShow". **DO NOT PUT A BACKSLASH IN THE END OF THE PATH, SHIT WILL BREAK, you're warned**

##### except
optional, words that, if found in the torrent title, will skip that torrent entry. For example, you have 2 series with the same name, say "offensive boi" one's from 1992, the other one is from 2010, imagine for instance that the one from 2010 has more seeders, but you want the one from 1992, do except='2010', and unless some head-in-ass uploader forgot to mention which of the 2 it is, you should only download the ones from 1992
You can do multiple separated by `;`s, example: `except='2010;head-in-ass uploader'`

# Lettuce
Sorry, there's actually no lettuce here. Why are you even looking for lettuce on github, makes no sense.

Have a nice one tho.
