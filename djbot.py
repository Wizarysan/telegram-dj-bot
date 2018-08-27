# -*- coding: utf-8 -*-

import requests
import threading
import json
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger

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
    print(response['result'][0]['message'])
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
        print(payload)

        scheduler.shutdown(wait=False)
        audioScheduler = BackgroundScheduler()
        audioScheduler.add_job(listenAudio, 'interval', seconds=10, args=[settings, playlist, audioScheduler, payload])
        audioScheduler.start()

def listenAudio(settings, playlist, scheduler, payload):
    response = getUpdates(settings)
    print(response)
    fileType = response['result'][0]['message']['audio']['mime_type']
    if fileType == 'audio/mpeg' or fileType == 'audio/flac':
        scheduler.shutdown(wait=False)
        telePost(
            settings,
            'sendMessage',
            data={'chat_id': response['result'][0]['message']['chat']['id'], 'text': 'Give me cover image please:'},
        )
        listenImage(response['result'][0]['message'], settings, payload)
    # schedulePlaylist(settings, demo_playlist, sched)

def createTaskById(message, settings, scheduler, payload):
    print('sched started')
    response = getUpdates(settings)
    print(response)
    if response['result'][0]['message']['photo']:
        print(response['result'][0]['message']['photo'])
        task = {
            "mode": "url",
            "url": message['audio']['file_id'],
            "image": response['result'][0]['message']['photo'][-1]['file_id'],
            "caption": "test Caption",
        }

        #Write task to playlist

        scheduler.shutdown(wait=False)
        telePost(
            settings,
            'sendMessage',
            data={'chat_id': response['result'][0]['message']['chat']['id'], 'text': 'Task created'},
        )
        print(task)


def listenImage(message, settings, payload):
    imageScheduler = BackgroundScheduler()
    imageScheduler.add_job(createTaskById, 'interval', seconds=10, args=[message, settings, imageScheduler, payload])
    imageScheduler.start()

def schedulePlaylist(settings, playlist, scheduler):
    #lstindex = len(playlist)
    for index, item in enumerate(playlist, start=1):
        date_trigger = DateTrigger(datetime.strptime(item['time'], '%Y.%m.%d %H:%M'))
        scheduler.add_job(lambda item: sendPost(settings, item), date_trigger, args=[item])
        print('Job created at ', date_trigger)
        # if index == lstindex:
        #     scheduler.add_job(scheduler.shutdown, 'date', run_date=end_datetime)
    scheduler.start()

def main():
    demo_playlist = json.load(open('playlist.json'))
    settings = json.load(open('settings.json'))

    sched = BackgroundScheduler()

    sched.add_job(listenCreationStart, 'interval', seconds=10, args=[settings, demo_playlist, sched])
    sched.start()
    #listenUpdates(settings, demo_playlist, sched)

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        sched.shutdown()

    print('all jobs are done')


main()
