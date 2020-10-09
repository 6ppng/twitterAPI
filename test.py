from datetime import datetime
from tzlocal import get_localzone
import json
from requests_oauthlib import OAuth1Session
import yaml

KEYS_RATH: str = './config/config.yaml'


def get_config() -> dict:
    with open(KEYS_RATH) as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    return config


def get_keys() -> dict:
    return get_config()['keys']


def post(tweet: str) -> None:
    keys = get_keys()
    url = "https://api.twitter.com/1.1/statuses/update.json"
    params = {"status": tweet}
    with OAuth1Session(
            keys['CK'], keys['CS'], keys['AT'], keys['AS']) as twitter:
        req = twitter.post(url, params=params)

    if req.status_code != 200:
        print(f'error : {req.status_code}')


def get_resource(timeline: str) -> str:
    if timeline == 'home':
        return 'https://api.twitter.com/1.1/statuses/home_timeline.json'
    list_id = get_config()['list_ids'][timeline]
    return 'https://api.twitter.com/1.1/lists/statuses.json' + \
        f'?list_id={list_id}'


def reload_timeline(timeline: str = 'home') -> None:
    keys = get_keys()
    url = get_resource(timeline)
    params = {'counts': 100}
    with OAuth1Session(
            keys['CK'], keys['CS'], keys['AT'], keys['AS']) as twitter:
        req = twitter.get(url, params=params)

    if req.status_code == 200:
        timeline = json.loads(req.text)
        for tweet in timeline[::-1]:
            time = datetime.strptime(
                tweet['created_at'], '%a %b %d %I:%M:%S %z %Y')
            time = time.astimezone(tz=get_localzone())
            print(tweet['user']['screen_name'], end=' :: ')
            print(time.strftime('%H:%M:%S'))
            print(tweet['text'])
            print('___')
    else:
        print(f'error : {req.status_code}')


def main() -> None:
    reload_timeline()


if __name__ == '__main__':
    main()
