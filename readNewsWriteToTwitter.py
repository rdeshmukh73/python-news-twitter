#Author: Raghavendra Deshmukh
#Purpose: Simple Python Program to read the inshorts website, get its news Item titles, Look for Tweets on the same news
#Referred the below 2 Sites for information. 
#Source#1: https://towardsdatascience.com/web-scraping-in-3-minutes-1c37830a29c1 for BeautifulSoup Usage
#Source#2: https://datascienceparichay.com/article/get-data-from-twitter-api-in-python-step-by-step-guide/ for Twitter API Usage

#This program uses Beautiful Soup library to read relevant news item titles, content from inshorts website.
#It uses the Titles to then look for Tweets on those News Items
#It will then collate a few details about the Tweets and will write to a CSV

import requests #Requests HTTP library to Read a particular website
from bs4 import BeautifulSoup #BS for Reading relevant data from a Website 
import pandas as pd #Pandas for Dataframe for easy data management
import tweepy as tw #Using the tweepy Python Library to Read Tweets from Twitter

#dummy_url="https://inshorts.com/en/read/sports"
#Reading from the inshorts main news page
dummy_url ="https://inshorts.com/en/read/"
#data_dummy=requests.get(dummy_url)
#soup=BeautifulSoup(data_dummy.content,'html.parser')

news_data_content,news_data_title,news_data_category=[],[],[]
url = dummy_url
category=url.split('/')[-1]
data=requests.get(url)
soup=BeautifulSoup(data.content,'html.parser')
news_title=[]
news_content=[]
news_category=[]
for headline,article in zip(soup.find_all('div', class_=["news-card-title news-right-box"]),
                            soup.find_all('div',class_=["news-card-content news-right-box"])):
    news_title.append(headline.find('span',attrs={'itemprop':"headline"}).string)

    news_content.append(article.find('div',attrs={'itemprop':"articleBody"}).string)
    news_category.append(category)
news_data_title.extend(news_title)
news_data_content.extend(news_content)
news_data_category.extend(news_category)  

#Create a Dataframe for News Title, Content and Category
df1=pd.DataFrame(news_data_title)
df2=pd.DataFrame(news_data_content,columns=["Content"])
df3=pd.DataFrame(news_data_category,columns=["Category"])
df=pd.concat([df1,df2,df3],axis=1)

#Setup the Twitter API for tweepy
tw_api_key = "Twitter API Key"
tw_api_secret = "Twitter API Secret"
auth = tw.OAuthHandler(tw_api_key, tw_api_secret)
twapi = tw.API(auth, wait_on_rate_limit=True)

tweets_df_collection = pd.DataFrame()

#Trying to read the News Article Title one by one
for row in news_title:
    tw_search = row
    
    #Make a Tweet Search based on the News Title
    tweets = tw.Cursor(twapi.search_tweets, q=tw_search, lang="en").items(100.0)
    
    tweet_list = []
    for tweet in tweets:
        #Append to a Tweet List.  Not used further as of now
        tweet_list.append(tweet)
        tw_text = twapi.get_status(id=tweet.id, tweet_mode='extended').full_text
        
        #Form the Tweet Data to be sent to CSV
        tweet_data = [{'Source News': tw_search, 'User Name': tweet.user.name, 'Text': tw_text}]
        tempdf = pd.DataFrame(tweet_data)
        #Add the Tweet Data to the Tweet Collection Dataframe
        tweets_df_collection = pd.concat([tweets_df_collection, tempdf])
        tweets_df_collection = tweets_df_collection.reset_index(drop=True)

print(tweets_df_collection)
#Export/Save the Tweets to a CSV file
tweets_df_collection.to_csv('tweets.csv')