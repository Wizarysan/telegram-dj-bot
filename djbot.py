# -*- coding: utf-8 -*-

import requests
import json
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger


def send_file(settings, item):
    requests.post(
        '{0}{1}/sendPhoto?chat_id={2}'.format(
            settings['url_base'], settings['token'], item['channel']
        ),
        proxies=settings['proxies'],
        files={'photo': open('images/{0}'.format(item['image']), 'rb')}
    )
    r = requests.post(
        '{0}{1}/sendAudio?chat_id={2}&parse_mode=Markdown&caption={3}'.format(
            settings['url_base'], settings['token'], item['channel'], item['caption']
        ),
        proxies=settings['proxies'],
        files={'audio': open('music/{0}'.format(item['file']), 'rb')}
    )
    print(r.text)
    return r.text


def send_url(settings, item):
    requests.post(
        '{0}{1}/sendPhoto?chat_id={2}&photo={3}'.format(
            settings['url_base'], settings['token'], item['channel'], item['image']
        ),
        proxies=settings['proxies']
    )
    r = requests.post(
        '{0}{1}/sendAudio?chat_id={2}&parse_mode=Markdown&caption={3}&audio={4}'.format(
            settings['url_base'], settings['token'], item['channel'], item['caption'], item['url']
        ),
        proxies=settings['proxies']
    )
    print(r.text)
    return r.text


def sendPost(settings, item):
    if(item['mode'] == 'file'):
        return send_file(settings, item)
    else:
        return send_file(settings, item)


def schedulePlaylist(settings, playlist, scheduler):
    #lstindex = len(playlist)
    for index, item in enumerate(playlist, start=1):
        date_trigger = DateTrigger(datetime.strptime(item['time'], '%Y.%m.%d %H:%M'))
        scheduler.add_job(lambda item: sendPost(settings, item), date_trigger, kwargs=item)
        print('Job created at ', date_trigger)
        # if index == lstindex:
        #     scheduler.add_job(scheduler.shutdown, 'date', run_date=end_datetime)
    scheduler.start()


def main():
    demo_playlist = json.load(open('playlist.json', 'r'))
    settings = json.load(open('settings.json', 'r'))

    sched = BackgroundScheduler()

    schedulePlaylist(settings, demo_playlist, sched)

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        sched.shutdown()

    print('all jobs are done')


main()
