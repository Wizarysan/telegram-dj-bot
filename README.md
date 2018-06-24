# Telegram DJ Bot :watch::musical_note:
TG bot for posting songs and cover images in particular datetime

### Prerequisites
Python 3, apscheduler, requests

### Usage
In settings.json enter bot token provided by BotFather
Edit or remove proxy if necessary 

It loads songs from playlist.json where

```
    {
        "mode": file or url,
        "channel": channel to send song to (bot must be there, of course),
        "time": Date and time to send file in "YYYY.MM.DD HH:MM" format,
        "file": Audio filename,
        "image": Image filename,
        "caption": Caption can be edited using *Markdown*
    }
```
#### Loading image and song by links:
If mode is set to _'url'_ you must provide "url" with audio link instead of "file"
"image" must be also a link 


### TODO
Creating tasks via the bot itself

(c) example file is from [Camellia](https://soundcloud.com/kamelcamellia/ctcd-012-crystallized-xfaded-demo)
