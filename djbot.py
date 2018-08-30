# -*- coding: utf-8 -*-

import requests
import threading
import json
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

commonTrigger = IntervalTrigger(seconds=10)

def setInterval(func,time):
    e = threading.Event()
    while not e.wait(time):
        func()

def telePost(settings, method, data, files=None):
    return requests.post(
        '{url_base}{token}/{method}'.format(method=method, **settings),
        data=data,
        proxies=settings['proxies'],
        files=files
    )

def sendFile(settings, item):
    telePost(
        settings,
        'sendPhoto',
        data={'chat_id': item['channel']},
        files={'photo': open('images/{0}'.format(item['image']), 'rb')}
    )
    return telePost(
        settings,
        'sendAudio',
        data={
            'chat_id':    item['channel'],
            'parse_mode': 'Markdown',
            'caption':    item['caption']
        },
        files={'audio': open('music/{0}'.format(item['file']), 'rb')}
    )


def sendUrl(settings, item):
    telePost(
        settings,
        'sendPhoto',
        data={
            'chat_id': item['channel'],
            'photo':   item['image']
        }
    )
    return telePost(
        settings,
        'sendAudio',
        data={
            'chat_id':    item['channel'],
            'parse_mode': 'Markdown',
            'caption':    item['caption'],
            'audio':      item['url']
        }
    )

def sendPost(settings, item):
    if item['mode'] == 'file':
        r = sendFile(settings, item)
    elif item['mode'] == 'url':
        r = sendUrl(settings, item)
    else:
        raise ValueError('Unknown mode: {}'.format(item['mode']))
    print(r.text)
    return r.text

def getUpdates(settings):
    testing_upd = requests.get(
        '{url_base}{token}/getUpdates?offset=-1&limit=1'.format(**settings),
        proxies=settings['proxies']
    )
    return testing_upd.json()

def listenCreationStart(settings, playlist, scheduler):
    response = getUpdates(settings)
    messageText = response['result'][0]['message']['text']

    if 'start' in messageText:
        telePost(
            settings,
            'sendMessage',
            data={'chat_id': response['result'][0]['message']['chat']['id'], 'text': 'Playlist started'},
        )
        scheduler.shutdown(wait=False)
        schedulePlaylist(settings, playlist)

    if 'add' in messageText:
        telePost(
            settings,
            'sendMessage',
            data={'chat_id': response['result'][0]['message']['chat']['id'], 'text': 'Give me audio please:'},
        )

        messageList = messageText.split()
        payload = {
            'time': messageList[1] + ' ' + messageList[2],
            'channel': messageList[3]
        }

        scheduler.shutdown(wait=False)
        audioScheduler = BackgroundScheduler()
        audioScheduler.add_job(listenAudio, trigger=commonTrigger, args=[settings, playlist, audioScheduler, payload])
        audioScheduler.start()

def listenAudio(settings, playlist, scheduler, payload):
    response = getUpdates(settings)
    fileType = response['result'][0]['message']['audio']['mime_type']
    if fileType == 'audio/mpeg' or fileType == 'audio/flac':
        scheduler.shutdown(wait=False)
        telePost(
            settings,
            'sendMessage',
            data={'chat_id': response['result'][0]['message']['chat']['id'], 'text': 'Give me cover image please:'},
        )
        listenImage(response['result'][0]['message'], settings, playlist, payload)

def createTaskById(message, settings, scheduler, playlist, payload):
    print('sched started')
    response = getUpdates(settings)
    if response['result'][0]['message']['photo']:
        task = {
            "mode": "url",
            "time": payload['time'],
            "channel": payload['channel'],
            "url": message['audio']['file_id'],
            "image": response['result'][0]['message']['photo'][-1]['file_id'],
            "caption": response['result'][0]['message']['caption'],
        }
        playlist.append(task)
        with open('playlist.json', 'w') as outfile:
            json.dump(playlist, outfile, indent=4)

        scheduler.shutdown(wait=False)
        telePost(
            settings,
            'sendMessage',
            data={'chat_id': response['result'][0]['message']['chat']['id'], 'text': 'Task created'},
        )
        main()

def listenImage(message, settings, playlist, payload):
    imageScheduler = BackgroundScheduler()
    imageScheduler.add_job(createTaskById, trigger=commonTrigger, args=[message, settings, imageScheduler, playlist, payload])
    imageScheduler.start()

def schedulePlaylist(settings, playlist):
    playlistScheduler = BackgroundScheduler()
    for index, item in enumerate(playlist, start=1):
        date_trigger = DateTrigger(datetime.strptime(item['time'], '%Y.%m.%d %H:%M'))
        playlistScheduler.add_job(lambda item: sendPost(settings, item), date_trigger, args=[item])
        print('Job created at ', date_trigger)
    playlistScheduler.start()

def main():
    demo_playlist = json.load(open('playlist.json'))
    settings = json.load(open('settings.json'))

    sched = BackgroundScheduler()

    sched.add_job(listenCreationStart, trigger=commonTrigger, args=[settings, demo_playlist, sched])
    sched.start()

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        sched.shutdown()

    print('all jobs are done')


main()
