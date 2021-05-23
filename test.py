import re
import json
import numpy
from typing import List
import nltk
import yfinance as yf
import praw
import networkx as nx
import matplotlib.pyplot as plt

#final series using trie , handle different data sets
#visualization techniques

# nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

sid = SentimentIntensityAnalyzer()

import praw

import pandas as pd


def get_env_data():
    with open('.env') as f:
        data = json.load(f)
    return data['client-id'], data['client-secret'], data['username'], data[
        'password']


def _get_instance() -> praw.Reddit:
    client_id, client_secret, username, password = get_env_data()
    return praw.Reddit(user_agent='adictya',
                       client_id=client_id,
                       client_secret=client_secret,
                       username=username,
                       password=password)


def _comments_on_submission(submission: praw.models.Submission,
                            replace_lim: int = 0) -> List[str]:
    print(
        f' *\tParsing comments with replace limit={replace_lim} on post: {submission.title}'
    )
    submission.comments.replace_more(0)
    return submission.comments.list()


def fetchData():
    socialNetwork = nx.Graph()
    reddit = _get_instance()
    subreddit = reddit.subreddit('WallStreetBets')

    sid = SentimentIntensityAnalyzer()

    positiveWords = [
        'puts', 'green', 'updoot', 'PINS', 'squeeze', 'moon', 'holy', 'mod',
        'bearish', 'up', '🚀'
    ]
    negativeWords = [
        'short', 'red', 'downvote', 'hell', 'curse', 'bulish', 'down', 'drop',
        'crash'
    ]

    hot = reddit.submission(id="n9eiyu")

    usernameDict = {}
    trustDict = {}
    stockDict = {}

    id = -1

    # hot = subreddit.hot(limit=1)
    # comments = []
    # df["comment"] = hot.apply(lambda comment: hot)

    for comment in _comments_on_submission(hot):
        stocks = re.findall("[A-Z]{1,5}", comment.body)
        stockData = ""

        for stock in stocks:
            if (stock in stockDict.keys()):
                stockData = stockDict[stock]
                break
            stockData = yf.Ticker(stock).info
            if len(stockData) > 1:
                stockDict[stock] = stockData
                break

        if (comment.author and len(stockData) > 1):
            prevClose = stockData["previousClose"]
            currOpen = stockData["open"]

            percentage = ((currOpen - prevClose) / prevClose) * 100
            trustScore = sid.polarity_scores(
                comment.body)["compound"] * percentage
            userName = comment.author.name

            if (userName not in usernameDict.keys()):
                id += 1
                usernameDict[userName] = id
                parent_id = id
                trustDict[id] = trustScore
                socialNetwork.add_node(id, username=userName, trust=trustScore)

            else:
                parent_id = usernameDict[userName]
                trustDict[parent_id] += trustScore
                trustDict[parent_id] = min(50, trustDict[parent_id])
                socialNetwork.nodes[parent_id]['trust'] = trustDict[parent_id]

            comment.replies.replace_more(0)
            replyList = comment.replies.list()

            for reply in replyList:

                sentiment = sid.polarity_scores(reply.body)["compound"]

                if (reply.author
                        and reply.author.name not in usernameDict.keys()):
                    userName = reply.author.name
                    id += 1
                    usernameDict[userName] = id
                    trustDict[id] = sentiment * trustScore
                    socialNetwork.add_node(id,
                                           username=userName,
                                           trust=sentiment * trustScore)
                    socialNetwork.add_edge(parent_id,
                                           id,
                                           weight=sentiment * trustScore)

                elif (reply.author):
                    userName = reply.author.name
                    child_id = usernameDict[userName]
                    trustDict[child_id] += trustScore * sentiment
                    trustDict[child_id] = min(50, trustDict[child_id])
                    socialNetwork.nodes[child_id]['trust'] = trustDict[
                        child_id]
                    socialNetwork.add_edge(parent_id,
                                           child_id,
                                           weight=sentiment * trustScore)

    id = -1
    socialNetwork = numpy.zeros((100, 100))
    for comment in _comments_on_submission(hot):
        stocks = re.findall("[A-Z]{1,5}", comment.body)
        stockData = ""
        for stock in stocks:
            stockData = yf.Ticker(stock).info
            if len(stockData) > 1:
                break
        if (len(stockData) > 1):
            myDict["Author"].append(comment.author.name)
            try:
                prevClose = stockData["previousClose"]
                currOpen = stockData["open"]
            except Exception as e:
                prevClose = 1
                currOpen = 0
            percentage = ((currOpen - prevClose) / prevClose) * 100
            trustScore = sid.polarity_scores(
                comment.body)["compound"] * percentage
            if (comment.author.name not in myDict.keys()):
                id = id + 1
                myDict[comment.author.name] = id
                parent_id = id
            else:
                parent_id = myDict[comment.author.name]
            comment.replies.replace_more(0)
            replyList = comment.replies.list()
            for reply in replyList:
                sentiment = sid.polarity_scores(reply.body)["compound"]
                if (reply.author.name not in myDict.keys()):
                    id = id + 1
                    myDict[reply.author.name] = id
                    socialNetwork[parent_id][id] += sentiment * trustScore
                    print(parent_id, id)
                else:
                    childId = myDict[reply.author.name]
                    socialNetwork[parent_id][childId] += sentiment * trustScore
                    print(parent_id, id)


def main():
    fetchData()
    # userName1 = "I am investing in FUCK TSLA"
    # stocks = re.findall("[A-Z]{1,5}", userName1)
    # stockData = ""
    # for stock in stocks:
    #     stockData = yf.Ticker(stock).info
    #     if len(stockData) > 1:
    #         break
    # userName1 = userName1.split("_")
    # print(stockData)

    # myDict = {}
    # myDict["gay"] = 1
    # if ("gay1" not in myDict.keys()):
    #     myDict["gay1"] = 2
    # print(myDict)


if __name__ == '__main__':
    main()
