import tweepy
import access_credentials
import webbrowser
import re
import csv

auth = tweepy.OAuthHandler(access_credentials.consumer_key, access_credentials.consumer_key_secret)

if not access_credentials.access_token_secret or not access_credentials.access_token:
    try:
        redirect_url = auth.get_authorization_url()
    except tweepy.TweepError as error:
        print('Error! Failed to get request token.\n' + error.reason)

    print(redirect_url)
    webbrowser.open(redirect_url, new=2, autoraise=True)
    verifier = input('Verifier code: ')

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError as error:
        print('Error! Failed to get access token.\n' + error.reason)

    sub = 'access_token = \'' + auth.access_token + '\'\naccess_token_secret = \'' + auth.access_token_secret + '\''

    with open('access_credentials.py', 'r+') as file:
        content = file.read()
        file.seek(0)
        file.write(re.sub(r'access_token = \'\'\naccess_token_secret = \'\'', sub, content))
        file.truncate()

auth.set_access_token(access_credentials.access_token, access_credentials.access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

user = api.me()
print('\nUser: ' + user.name + '\n')

with open('users.csv', newline='') as f:
    reader = csv.reader(f)
    users = list(next(reader))

user_objects = api.lookup_users(screen_names=users)
user_ids = [user.id_str for user in user_objects]


class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        if 'RT @' not in status.text and status.user.id_str in user_ids:
            try:
                api.retweet(status.id)
                print('Successfully retweeted!\nTweet: "' + status.text + '"\nID: ' + str(status.id))
                print('***********************************************')
            except tweepy.TweepError as te:
                    print(te.reason)

    def on_error(self, status_code):
        if status_code == 420:
            print("Error ratelimit: " + str(status_code))
            return False


hashtag = ''

if user.name == '75befreiung':
    hashtag = '#75befreiung'
if user.name == '75liberation':
    hashtag = '#75liberation'

listener = MyStreamListener()
stream = tweepy.Stream(auth, listener)
stream.filter(track=[hashtag], is_async=True)
