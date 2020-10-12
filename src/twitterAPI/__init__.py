from datetime import datetime, timedelta
from tzlocal import get_localzone
import json
import os
from requests_oauthlib import OAuth1Session
import yaml

CONFIG_RATH: str = os.path.dirname() + '/config/config.yaml'
RESOURCE_PATH: str = os.path.dirname() + '/resources.yaml'


def _get_config() -> dict:
    with open(CONFIG_RATH) as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    return config


def _get_resources() -> dict:
    with open(RESOURCE_PATH) as f:
        resource = yaml.load(f, Loader=yaml.SafeLoader)
    return resource


def post(tweet: str) -> None:
    keys = _get_config()['keys']
    url = _get_resources()['post']
    params = {"status": tweet}
    with OAuth1Session(
            keys['CK'], keys['CS'], keys['AT'], keys['AS']) as twitter:
        req = twitter.post(url, params=params)

    if req.status_code != 200:
        print(f'error : {req.status_code}')


def get_timeline(target: str, param: str) -> list:

    keys = _get_config()['keys']
    url = _get_resources()['tl'][target]

    params = {
        'counts': 5
    }

    if target == 'list':
        try:
            list_id = _get_config()['list_ids'][param]
        except KeyError:
            raise KeyError(f'リスト「{param}」のIDが設定されていません')
        params.update({'list_id': list_id})
    elif target == 'user':
        params.update({'screen_name': param})
    elif target == 'search':
        params.update({'q': param})

    with OAuth1Session(
            keys['CK'], keys['CS'], keys['AT'], keys['AS']) as twitter:
        req = twitter.get(url, params=params)

    if req.status_code == 200:
        return json.loads(req.text)

    print(f'error : {req.status_code}')
    return None


def _draw_timeline(timeline: list) -> None:

    jp = get_localzone()
    now = datetime.now().astimezone(tz=jp)

    for tweet in timeline[::-1]:

        time = datetime.strptime(
            tweet['created_at'], '%a %b %d %H:%M:%S %z %Y').astimezone(tz=jp)

        pass_time = now - time
        pass_sec = int(pass_time.total_seconds())
        pass_min = pass_sec // 60
        pass_hour = pass_min // 60
        pass_days = pass_hour // 24
        pass_hour %= 24
        pass_min %= 60
        pass_sec %= 60

        if pass_time < timedelta(minutes=1):
            time_view = 'now'
            pass_view = f'{pass_sec}"'
        elif pass_time < timedelta(hours=1):
            time_view = time.strftime('%H:%M')
            pass_view = f'{pass_min}\'{pass_sec}"'
        elif pass_time < timedelta(days=1):
            time_view = time.strftime('%H:%M')
            pass_view = f'{pass_hour}°{pass_min}\''
        else:
            time_view = time.strftime('%m/%d %H:%M')
            pass_view = f'{pass_days}d{pass_hour}°'

        fav = tweet['favorite_count']
        retweet = tweet["retweet_count"]

        print(tweet['user']['screen_name'], end=' ')
        print(f'{time_view} ({pass_view})', end=' ')
        if tweet['text'][:2] == 'RT':
            print('RT>>')
            _draw_timeline([tweet['retweeted_status']])
        else:
            if retweet != 0:
                print(f'RT:{retweet}', end=' ')
            if fav != 0:
                print(f'fav:{fav}', end=' ')
            print(':')
            print(tweet['text'].replace('\n', ' '), end=2 * '\n')


def load(target: str = 'home', param: str = None) -> None:
    timeline = get_timeline(target, param)
    if timeline is not None:
        if target == 'search':
            timeline = timeline['statuses']
        _draw_timeline(timeline)


def main() -> None:
    load()


if __name__ == '__main__':
    main()
