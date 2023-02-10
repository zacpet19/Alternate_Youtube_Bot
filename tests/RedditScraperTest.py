import os
from dotenv import load_dotenv
import sys
sys.path.append('..')
import random
from src.redditScraper import RedditScraper


def getTopPostCommentsTest():
    load_dotenv()
    client_id = os.getenv('client_id')
    client_secret = os.getenv('client_secret')
    user_agent = os.getenv('user_agent')

    reddit = RedditScraper(client_id,client_secret,user_agent)
    (comments,urls, _) = reddit.getTopPostAndComments("csmajors", 2)
    assert len(urls) != 0
    assert type(urls) == list
    assert type(urls[0]) == str
    assert len(comments) != 0
    assert type(comments) == list
    assert type(comments[0]) == list
    assert comments[0][0] != comments[1][0]
    for i in comments:
        for index, j in enumerate(i):
            assert type(j) == str
            if index == 1:
                assert len(j) <= 2500
                assert "http" not in j
                assert "!!" not in j
                assert "??" not in j
                assert ".." not in j
                f = open("bannedWordList.txt", "r")
                lines = f.readlines()
                for line in lines:
                    assert line not in j
            if index > 1:
                assert len(j) <= 1000
                f = open("bannedWordList.txt","r")
                lines = f.readlines()
                for line in lines:
                    assert line not in j

    print("TopPostCommentsTest Passed")

def parseTest():
    badText = " Here is the the wiki link to it https://en.wikipedia.org/wiki/White_Rock"
    load_dotenv()
    client_id = os.getenv('client_id')
    client_secret = os.getenv('client_secret')
    user_agent = os.getenv('user_agent')

    reddit = RedditScraper(client_id,client_secret,user_agent)

    print(reddit.parseComments(badText))
    print("Parse test passed")

def contentFilterTest():
    load_dotenv()
    client_id = os.getenv('client_id')
    client_secret = os.getenv('client_secret')
    user_agent = os.getenv('user_agent')

    reddit = RedditScraper(client_id, client_secret, user_agent)

    test1 = "I hate Joe Biden."
    test2 = "I hate Joe Biden protests."
    test3 = "The President of France, Emmanuel Macron, is trying to raise the retirement age from 62 to 64. " \
            "So the eight biggest unions across the country called a massive wave of strikes and protests today, " \
            "with over 200 actions across the country."
    test4 = "Hello there"
    test5 = "I am having a good time and not saying anything that should be filtered."
    test6 = ""
    test7 = "What could be done to prevent mass shootings?"

    assert reddit.contentFilter(test1) is True
    assert reddit.contentFilter(test2) is True
    assert reddit.contentFilter(test3) is True
    assert reddit.contentFilter(test4) is False
    assert reddit.contentFilter(test5) is False
    assert reddit.contentFilter(test6) is False
    assert reddit.contentFilter(test7) is True

    print("Filter tests passed")

def manageVisitedRedditPagesTest():
    load_dotenv()
    client_id = os.getenv('client_id')
    client_secret = os.getenv('client_secret')
    user_agent = os.getenv('user_agent')

    reddit = RedditScraper(client_id, client_secret, user_agent)
    f = open("visitedRedditPages.txt", "r")
    startLines = f.readlines()
    f.close()

    reddit.manageVisitedRedditPages(10, 50)

    assert os.path.exists("visitedRedditPages.txt")
    f = open("visitedRedditPages.txt", "r")
    lines = f.readlines()
    f.close()
    assert len(lines) == 50
    assert len(lines) == len(reddit.pastUrls)
    assert lines[0] == startLines[len(startLines) - 50]
    assert lines[-1] == startLines[-1]
    randomInt = random.randint(0, 50)
    assert lines[len(lines) - randomInt] == startLines[len(startLines) - randomInt]
    f = open("visitedRedditPages.txt", "w")
    for line in startLines:
        f.write(line)
    f.close()

    reddit.manageVisitedRedditPages(10000000, 50)

    assert os.path.exists("visitedRedditPages.txt")
    f = open("visitedRedditPages.txt", "r")
    lines = f.readlines()
    f.close()
    assert len(lines) == len(startLines)

    print("Manage visited reddit pages test passed")

if __name__ == "__main__":

    # getTopPostCommentsTest()
    # parseTest()
    contentFilterTest()
    #manageVisitedRedditPagesTest()
