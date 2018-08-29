# Telegram DJ Bot :watch::musical_note:
TG bot for posting songs and cover images in particular date and time

### Prerequisites
Python 3, apscheduler, requests

### Usage

In settings.json enter bot token provided by BotFather
Edit or remove proxy if necessary

Run djbot.exe from dist folder
Open your bot in Telegram and send message
**add YYYY.MM.DD HH:MM @channel**
For example:
_add 2018.08.28 13:38 @wiztest_

Then you will be asked for sound file, drag and drop it to bot
After successful uploading you will be asked for cover image, drop it to as photo
and **add some caption** (it's necessary for now) describing your post
Caption uses Markdown language

When you finish adding your songs write **start** to schedule your playlist
You always can view and edit playlist directly:

#### Edit playlist directly:

Bot loads songs from playlist.json where

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

#### Loading image and song with links:
If mode is set to _'url'_ you must provide "url" with audio link instead of "file"
"image" must be also a link 


(c) example file from [Camellia](https://soundcloud.com/kamelcamellia/ctcd-012-crystallized-xfaded-demo)
