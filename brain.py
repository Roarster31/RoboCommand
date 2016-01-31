import time
import requests
from tweepy import OAuthHandler
import tweepy
json_data = ""
dataCheck = False
import say_something as TALK
import SocketManager
import brain_api as AIBot
consumer_key = '1MUDOQv80dafJg6sMrjr3YRol'
consumer_secret = 'uizOJFjZ8nGmgvCbPLupeQiE5fhjNYFDeqXlNXif7CtJyjIM6H'
access_token = '4864903228-PVG0k3kFy8ojtLMFhUIewkpjUybpPJo1WBVDFdD'
access_secret = '3l7rIzf7bp0twTHHvJm6hKQeW2cY8Z8xBBZQHmJhWVUs0'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)




# Gets tweets to @ArmHackathonBot
from tweepy import Stream
from tweepy.streaming import StreamListener, json
class MyListener(StreamListener):
    globals()
    def on_data(self, dataTwitter):
        global dataCheck
        text = json.loads(dataTwitter)['text'].replace("@ArmHackathonBot ", "")
        isTalkToSteve = "#TalkToSteve" in text
        text = text.replace("#PublicOpinion", "")
        text = text.replace("#TalkToSteve", "")
        name = json.loads(dataTwitter)['user']['name']
        nameTwitter = json.loads(dataTwitter)['user']['screen_name']
        #get data
        if isTalkToSteve:
            AIBot.query(text)
        else:
            processTweet(text,name,nameTwitter)
        dataCheck = True
        return True

    def on_error(self, status):
        print(status)
        if status == 420 :
            return False
        time.sleep(0.5)
        return True

def begin_streaming():
    twitter_stream = Stream(auth, MyListener())
    twitter_stream.filter(track=['@ArmHackathonBot','#PublicOpinion','#TalkToSteve'], async=True)

# Search twitter
def searchTwitter(info):
    query = info
    max_tweets = 500
    searched_tweets = []
    last_id = -1
    while len(searched_tweets) < max_tweets:
        count = max_tweets - len(searched_tweets)
        try:
            new_tweets = api.search(q=query, count=count, max_id=str(last_id - 1), lang='en')
            if not new_tweets:
                break
            searched_tweets.extend(new_tweets)
            last_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            # depending on TweepError.code, one may want to retry or wait
            # to keep things simple, we will give up on an error
            break
    list_tweets = []
    for tweet in searched_tweets:
        text = tweet.text.replace("RT", "")
        list_tweets.append(text)
    return list_tweets





# Convert sentiment api output to single + or - value
def convertSentiment(data):
    total = 0
    for i in data :
        if i['result'] == 'Positive':
                total = total + 1
        elif i['result'] == 'Negative':
                total = total - 2
    return total

# Input txt list, returns sentiment values as a Json List
def sendRecieveMeaningCloud(tweets):
    url = 'http://sentiment.vivekn.com/api/batch/'
    data = tweets
    r = requests.post(url, data=json.dumps(data))
    return r

# input list of tweets, output single value.
def sentimentValue(tweets):
    r = sendRecieveMeaningCloud(tweets)
    data = json.loads(r.content)
    sentiment = convertSentiment(data)
    return sentiment

def formJSON(sentimentValue,text, name, nameTwitter):
    data = {}
    data['sentimentValue'] = sentimentValue
    data['text'] = text
    data['name'] = name
    data['nameTwitter'] = nameTwitter
    return json.dumps(data)

def processTweet(text, name, nameTwitter):
    value = sentimentValue(searchTwitter(text))

    emotion = "unhappy" if (value < 0) else "happy"
    adjective = "negative" if (value < 0) else "positive"

    TALK.say_message("!%s I have just received a tweet. It appears that on the subject of %s, the public's perception is %s" % (emotion, text, adjective))

    # json_data = formJSON(value,text,name,nameTwitter)

def searchTwitterForValue(text):
    value = sentimentValue(searchTwitter(text))

    emotion = "unhappy" if (value < 0) else "happy"
    adjective = "negative" if (value < 0) else "positive"

    TALK.say_message("!%s It appears that the public's perception of your question is %s" % (emotion, adjective))


    return value

def newData():
    global json_data
    global dataCheck
    if dataCheck :
        dataCheck = False
        return json_data
    else:
        return False
