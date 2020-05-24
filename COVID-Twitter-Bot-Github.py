# COVID-19 Statistics Twitter Bot
# Contributors: ammar-s847 | shenbenson | JunZheng-Dev

import tweepy
import time
import requests
import json
import threading

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''

FILE_NAME = 'last_seen_id.txt'
COUNTRY_URL = "https://covid-19-data.p.rapidapi.com/country"
TOTALS_URL = "https://covid-19-data.p.rapidapi.com/totals"

headers = {
    'x-rapidapi-host': "covid-19-data.p.rapidapi.com",
    'x-rapidapi-key': ""
}

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id

def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return

def world_stats() :
    querystring = {"format":"json"}
    response = requests.request("GET", TOTALS_URL, headers=headers, params=querystring)
    data = json.loads(response.text[1:-1])
    time = str(data['lastUpdate']).replace('T', ' ')[0:-6] + ' CEST'
    status = (' 𝗪𝗼𝗿𝗹𝗱 𝗗𝗮𝘁𝗮\n\nTotal Cases: ' + f"{data['confirmed']:,}" +
            '\nRecovered Cases: ' + f"{data['recovered']:,}" + '\nCurrent Cases: ' +
            f"{(data['confirmed'] - data['recovered'] - data['deaths']):,}" + 
            '\nTotal Deaths: ' + f"{data['deaths']:,}" + '\nMortality Rate: ' +
            str("{:.2f}".format(data['deaths'] / data['confirmed'] * 100)) +
            '%\n\nUpdated ' + time)
    return status

def country_stats(country) :
    querystring = {"format":"json","name":country}
    response = requests.request("GET", COUNTRY_URL, headers=headers, params=querystring)
    data = json.loads(response.text[1:-1])
    time = str(data['lastUpdate']).replace('T', ' ')[0:-6] + ' CEST'
    reply = (' 𝗗𝗮𝘁𝗮 𝗳𝗼𝗿 ' + country.upper() + '\n\nTotal Cases: ' +
            f"{data['confirmed']:,}" + '\nRecovered Cases: ' + 
            f"{data['recovered']:,}" + '\nCurrent Cases: ' +
            f"{(data['confirmed'] - data['recovered'] - data['deaths']):,}" + 
            '\nTotal Deaths: ' + f"{data['deaths']:,}" + '\nMortality Rate: ' +
            str("{:.2f}".format(data['deaths'] / data['confirmed'] * 100)) +
            '%\n\nUpdated ' + time)
    return reply

def reply_to_tweets():
    print('expecting new tweets...', flush = True)
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    mentions = api.mentions_timeline(last_seen_id, tweet_mode='extended')
    for mention in reversed(mentions):
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        textholder = mention.full_text.lower()
        print(mention.user.screen_name + ' - ' + textholder, flush = True)
        if 'covid:' in textholder:
            country = textholder[textholder.index(':') + 1:]
            if 'world' in country.lower():
                try:    
                    api.update_status('@' + mention.user.screen_name +
                        world_stats(), mention.id)
                except:
                    reply = ' Uh oh! Something went wrong.'
                    api.update_status('@' + mention.user.screen_name +
                            reply, mention.id)
            else:
                try:
                    api.update_status('@' + mention.user.screen_name +
                            country_stats(country), mention.id)
                except:
                    reply = ' Uh oh! Something went wrong.'
                    api.update_status('@' + mention.user.screen_name +
                            reply, mention.id)

def dailyTweet(): 
    threading.Timer(86400.0, dailyTweet).start()
    try:    
        api.update_status(world_stats())
    except Exception as e:
        print(e)

dailyTweet()

while True:
    reply_to_tweets()
    time.sleep(15)