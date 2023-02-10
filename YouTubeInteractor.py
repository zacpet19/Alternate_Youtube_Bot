from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

load_dotenv()
youtubeAPIKey = os.getenv('youtube_API_Key')

class YouTubeClient:
    def __init__(self, youtubeAPIKey : str):
        try:
            self.youtube = build('youtube', 'v3', developerKey=youtubeAPIKey)
        except Exception as e:
            print("Error: Invalid API key given or unable to connect to client")
            raise e

youtube = YouTubeClient(youtubeAPIKey)
request = youtube.youtube.channels().list(part='statistics', forUsername='schafer5')



