from datetime import datetime, timedelta
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


def get_resource(timeline_name: str) -> str:
    if timeline_name == 'home':
        return 'https://api.twitter.com/1.1/statuses/home_timeline.json'
    list_id = get_config()['list_ids'][timeline_name]
    return 'https://api.twitter.com/1.1/lists/statuses.json' + \
        f'?list_id={list_id}'


def get_timeline(timeline_name: str) -> list:

    keys = get_keys()
    url = get_resource(timeline_name)
    params = {'counts': 100}
    with OAuth1Session(
            keys['CK'], keys['CS'], keys['AT'], keys['AS']) as twitter:
        req = twitter.get(url, params=params)

    if req.status_code == 200:
        return json.loads(req.text)

    print(f'error : {req.status_code}')
    return None


def draw_timeline(timeline: list) -> None:

    jp = get_localzone()
    now = datetime.now().astimezone(tz=jp)

    for tweet in timeline[::-1]:

        time = datetime.strptime(
            tweet['created_at'], '%a %b %d %H:%M:%S %z %Y').astimezone(tz=jp)

        pass_time = now - time
        if pass_time < timedelta(hours=1):
            time_view = time.strftime('%M:%S')
        elif pass_time < timedelta(days=1):
            time_view = time.strftime('%H:%M:%S')
        else:
            time_view = time.strftime('%m/%d %H:%M:%S')

        if tweet['text'][:2] == 'RT':
            fav = tweet['retweeted_status']['favorite_count']
        else:
            fav = tweet['favorite_count']

        retweet = tweet["retweet_count"]

        print(tweet['user']['screen_name'][:5], end=' ')
        print(time_view, end=' : ')
        print(tweet['text'].replace('\n', ' '), end='')
        if fav != 0:
            print(f' fav:{fav}', end='')
        if retweet != 0:
            print(f' RT:{retweet}', end='')
        print()


def reload(timeline_name: str = 'home') -> None:
    timeline = get_timeline(timeline_name)
    if timeline is not None:
        draw_timeline(timeline)


def main() -> None:
    reload('friends')


if __name__ == '__main__':
    main()
