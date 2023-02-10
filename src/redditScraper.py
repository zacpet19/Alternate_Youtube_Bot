import os
from typing import Tuple, List, Any
import praw
import re


class RedditScraper:
    """The RedditScraper class contains methods for scraping reddit to get posts and comments and parsing through them.
    As of now it is not very general use and the parsers have limited functionality."""
    def __init__(self,client_id,client_secret, user_agent):
        """Constructor for object that allows interaction with Reddit."""
        self.reddit = praw.Reddit(client_id=client_id,client_secret=client_secret,user_agent=user_agent)
        self.shouldCensor = False
        self.shouldIgnore = False
        self.pastUrls = set()

        if not os.path.exists("./visitedRedditPages.txt"):
            f = open("./visitedRedditPages.txt", "x")
            f.close()
        try:
            f = open("visitedRedditPages.txt", "r")
            lines = f.readlines()
            for line in lines:
                self.pastUrls.add(line.replace("\n", ""))
        except Exception:
            print("Failed to open visitedRedditPages.txt, duplicate posts may be used")
        #Check if bannedWordList exists
        try:
            f = open("bannedWordList.txt", "r")
            f.close()
            self.shouldCensor = True
        except Exception:
            print("Failed to open bannedWordList.txt, reddit text will not be censored")
        try:
            f = open("parseIgnore.txt", "r")
            f.close()
            self.shouldIgnore = True
        except Exception:
            print("Failed to open parseIgnore.txt reddit text will be read as it is pulled")

        

    def getTopPostAndComments(self, subreddit : str, numberOfPosts=1, depth=20) -> tuple[list[list[str]], list[str], list]:
        """getTopPostComments takes in a name of a subreddit and then returns a tuple that contains a 2d array of posts
        and comments,a list of urls, and dictionary containing comment IDS. The number of posts parameter decides how
        many posts from reddit to pull. The depth parameter decides how many posts deep to go into hot posts before
        abandoning the scrape."""
        #TODO: Make this return only one post rather than a 2D array of them and a single url rather than a list of them
        #postInfo will be a 2d array that will have posts at each index and the posts will have the post title at the
        #0th index, post body at the 1st, and post contents for remaining indexes
        postInfo = []
        urlArray = []
        #commentIds contains the post ids as they are pulled from Praw. The format they are stored is as follows:
        #{"comment{commentNumber}" : "{commentId}", ...} where both the key and index are strings
        #TODO: commentIds should be a list of dictionaries or the rest of the return structure for this method should be changed
        commentIds = []
        if numberOfPosts < 1:
            print("Number of Posts must be greater than 1.")
            return (postInfo, urlArray, commentIds)
        for post in self.reddit.subreddit(subreddit).hot(limit=depth):
            if(len(postInfo) >= numberOfPosts):
                break
            #avoids non text posts
            if (post.stickied or post.url.endswith(('jpg', 'jpeg', 'png', 'gif', "mp4", "ogg", "WebM"))):
                continue
            if (post.url in self.pastUrls):
                continue
            #Doesnt use 18+ posts, non text posts, or posts with filtered content
            if post.over_18 or not post.is_self or self.contentFilter(post.title) or self.contentFilter(post.selftext):
                continue
            parsedTitle = self.parsePostBody(post.title)
            parsedBody = self.parsePostBody(post.selftext)
            #If body is too long we move to next post
            if(parsedBody == "error"):
                continue
            tempList = []
            post.comments.replace_more(limit=0)
            tempList.append(parsedTitle)
            tempList.append(parsedBody)
            urlArray.append(post.url)
            count = 0
            for top_level_comment in post.comments:
                #dont actually know if the comment.collapsed works but is meant to avoid collapsed comments because
                #they are inconvenient to screenshot. Couldnt find it on the actual docs but chatGPT says it works
                if top_level_comment.stickied or top_level_comment.collapsed:
                    continue
                parsed = self.parseComments(top_level_comment.body)
                #Ignore comments that are too long
                if parsed == "error":
                    continue
                tempList.append(parsed)
                count += 1
                commentIds.append(top_level_comment.id)
                #Only pull 5 top comments
                if count > 5:
                    break
            postInfo.append(tempList)
        #Document visited urls to avoid duplicate
        f = open("visitedRedditPages.txt", "a")
        for url in urlArray:
            f.write(url + "\n")
            self.pastUrls.add(url)
        f.close()
        return (postInfo, urlArray, commentIds)


    def parseComments(self,comment : str) -> str:
        """parseComments method goes through scraped comments and censored out words based on provided
        bannedWordList.txt. If the comment is too long it returns the string "error" because the comment is too long
        to use."""
        comment = re.sub(r'(\W)(?=\1)', '', comment)
        comment= re.sub(r'http\S+', '', comment)
        if(len(comment) > 1000):
            return "error"
        if not self.shouldCensor:
            return comment
        f = open("bannedWordList.txt","r")
        lines = f.readlines()
        for line in lines:
            line = line.replace("\n", "")
            comment = comment.replace(line,"bleep")
        f.close()
        return comment


    def parsePostBody(self,body : str) -> str:
        """parseComments method goes through scraped post body and censored out words based on provided
           bannedWordList.txt. If the post body is too long it returns the string "error" because the comment is too
           long to use."""
        body = re.sub(r'(\W)(?=\1)', '', body)
        body = re.sub(r'http\S+', '', body)
        if(len(body) > 2500):
            return "error"
        if not self.shouldCensor:
            return body
        f = open("bannedWordList.txt", "r")
        lines = f.readlines()
        for line in lines:
            line = line.replace("\n", "")
            body = body.replace(line, "bleep")
        f.close()
        return body

    def ignoreWords(self, words : str) -> str:
        """Takes in a string and then tokenizes it. If any of the tokens match with what is in the parseIgnore file it
        removes the token. Returns a string of without the removed words. This method was made with addidtional string
        parsing before giving it to gTTS."""
        if not self.shouldIgnore:
            return words
        f = open("parseIgnore.txt")
        lines = f.readlines()
        splitWords = words.split(" ")
        finalWordList = []
        basicPunctuation = [".", "!", "?"]
        for word in splitWords:
            contains = False
            for line in lines:
                line = line.replace("\n", "")
                if line in word:
                    contains = True

            if not contains:
                finalWordList.append(word)
            else:
                # Moves punctuation to the new end of sentence
                for punc in basicPunctuation:
                    if punc in word:
                        if len(finalWordList) > 0:
                            finalWordList[len(finalWordList) - 1] += punc
        f.close()
        stringBuilder = ""
        for word in finalWordList:
            stringBuilder += f"{word} "
        #removes space at the end
        return stringBuilder[:len(stringBuilder) - 1]

    def subredditList(self):
        subreddits = ["amItheasshole", "askreddit", "confession", "confessions", "tifu", "TalesFromRetail",
                      "relationship_advice"]
        return subreddits

    def contentFilter(self, string : str) -> bool:
        """Takes in a string and returns true if words in the string match are similiar to words in a preset list."""
        filterList = ["biden", "trump", "protest", "shooting", "politics", "political", "pelosi", "union", "terrorist",
                      "sex", "sexual"]
        splitString = string.split(" ")
        for token in splitString:
            for word in filterList:
                if word.lower() == token.lower():
                    return True
                elif word.lower() in token.lower():
                    if -2 <= (len(word) - len(token)) <= 2:
                        return True
        return False

    def manageVisitedRedditPages(self, bytesAllowed, urlsToBringOver):
        if os.stat("./visitedRedditPages.txt").st_size > bytesAllowed:
            f = open("./visitedRedditPages.txt", "r")
            lines = f.readlines()
            f.close()
            #takes the bottom section of the txt file which should the newest urls added
            mostRecentUrls = lines[len(lines) - urlsToBringOver: len(lines)]
            #opening file in "w" mode removes all data from it
            f = open("./visitedRedditPages.txt", "w")
            self.pastUrls = set()
            for url in mostRecentUrls:
                self.pastUrls.add(url)
                f.write(url)
            f.close()


