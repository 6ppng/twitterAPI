from requests_oauthlib import OAuth1Session
import yaml

KEYS_RATH: str = './downloads/config.yaml'


def get_config(path: str) -> dict:
    with open(KEYS_RATH) as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    return config


def get_keys() -> dict:
    return get_config(KEYS_RATH)['keys']


def post(tweet: str) -> int:
    keys = get_keys()
    url = "https://api.twitter.com/1.1/statuses/update.json"
    params = {"status": tweet}
    twitter = OAuth1Session(
        keys['CK'],
        keys['CS'],
        keys['AT'],
        keys['AS'])

    req = twitter.post(url, params=params)

    return req.status_code


def main() -> None:
    post('neyo')


if __name__ == '__main__':
    main()
