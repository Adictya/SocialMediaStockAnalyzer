import json
from typing import List
import nltk

#final series using trie , handle different data sets
#visualization techniques

# nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

sid = SentimentIntensityAnalyzer()

import praw

import pandas as pd

# User:{
#   Stocks : {
#       "name of stock": "sentiment",
#       "name of stock": "sentiment"
#   }
# Trust Score: {
# }
# Id: 1234
# }
# SIN:{
#  2d-array
#}


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
    submission.comments.replace_more(limit=replace_lim)
    return [comment.body for comment in submission.comments.list()]


def fetchData():
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

    hot = reddit.hot(id="mzl0cz")
    myDict = {"Comments": [], "Sentiment": []}

    # hot = subreddit.hot(limit=1)
    # comments = []
    # df["comment"] = hot.apply(lambda comment: hot)

    # for submission in hot:
    #     myDict["Comments"].append(_comments_on_submission(submission))

    for comment in _comments_on_submission(hot):
        myDict["Comments"].append(comment)
        myDict["Sentiment"].append(sid.polarity_scores(comment))
        print(comment)

    # print(len(comments))
    # print(comments)
    df = pd.DataFrame(myDict)
    df.to_csv('data.csv')


def main():
    fetchData()
    df = pd.read_csv("data.csv")
    df.head()
    print(df)


if __name__ == '__main__':
    main()
