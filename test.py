from requests_oauthlib import OAuth1Session
import yaml

KEYS_RATH: str = './config/config.yaml'
URL = "https://api.twitter.com/1.1/statuses/update.json"


def get_config() -> dict:
    with open(KEYS_RATH) as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    return config


def get_keys() -> dict:
    return get_config()['keys']


def post(tweet: str) -> int:
    keys = get_keys()
    params = {"status": tweet}
    with OAuth1Session(
            keys['CK'],
            keys['CS'],
            keys['AT'],
            keys['AS']) as twitter:
        req = twitter.post(URL, params=params)

    return req.status_code


def main() -> None:
    res = post('test')

    if res != 200:
        print(f'error : {res}')


if __name__ == '__main__':
    main()
