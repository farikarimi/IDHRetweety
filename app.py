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

hashtag = ''

if user.name == '75befreiung':
    hashtag = '#75befreiung'
if user.name == '75liberation':
    hashtag = '#75liberation'


class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        global hashtag
        if 'RT @' not in status.text and status.in_reply_to_status_id is None and hashtag in status.text:
            try:
                api.retweet(status.id)
            except tweepy.TweepError as te:
                print(te.reason)

            print('Successfully retweeted!\nTweet: "' + status.text + '"\nID: ' + str(status.id))

    def on_error(self, status_code):
        if status_code == 420:
            return False


listener = MyStreamListener()
stream = tweepy.Stream(auth, listener)
if stream:
    print('Listening to stream...\n')

with open('users.csv', newline='') as f:
    reader = csv.reader(f)
    users = list(next(reader))

user_objects = api.lookup_users(screen_names=users)
user_ids = [user.id_str for user in user_objects]

try:
    stream.filter(follow=user_ids, is_async=True)
except tweepy.TweepError as e:
    print(e.reason)

print('Tracked hashtag: ' + hashtag + '\n')
print(len(user_objects), 'tracked users:')
for user in user_objects:
    print('User:\t', user.screen_name, '\nID:\t\t', user.id_str)
