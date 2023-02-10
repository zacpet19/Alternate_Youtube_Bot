import os
from src.redditScraper import RedditScraper
from src.Audio import AudioMethods
from src.webHandler import WebHandler
from moviepy.editor import AudioFileClip
from src.Video import VideoMethods
from src.Logger import Logger
from dotenv import load_dotenv
import sys
import random



def main():
    logger = Logger()
    # load environment variables
    load_dotenv()
    gmail = os.getenv('gmail')
    password = os.getenv('gmailPassword')
    channel = os.getenv('youtubeChannel')
    #this needs an absolute filepath
    finalVideoPath = os.getenv('finalVideoPath')
    client_id = os.getenv('client_id')
    client_secret = os.getenv('client_secret')
    user_agent = os.getenv('user_agent')
    driverLocation = os.getenv('driver_location')
    #Should check for missing environment variables here
    logger.info("**************** NEW VIDEO CREATION START ****************")
    logger.info("Environment Variables loaded")

    VideoMethods.deleteImageVideoFolder()
    #declaring variables to store things found in the while loop
    foundUsableRedditPosts = False
    comments = ""
    urls = ""
    commentIdsPulled = ""
    numberOfCommentsUsed = 0
    #audioLengths will be a list of floats given by the length of each TTS portion of audio used
    audioLengths = ""
    parsedTextToSpeech = ""
    #determines if the post used has a body or not
    postBody = True
    maxVideoLength = 40
    count = 0
    retries = 20
    reddit = RedditScraper(client_id, client_secret, user_agent)
    #loops until it is able to get a usable mp3 file from Reddit posts
    while not foundUsableRedditPosts:
        if count >= retries:
            logger.error("Unable to find usable reddit posts, shutting down")
            sys.exit()
        count += 1
        # getting random subreddit from list
        subreddits = reddit.subredditList()
        randomSubreddit = subreddits[random.randint(0, len(subreddits) - 1)]
        #Scrape reddit posts
        (comments, urls, commentIdsPulled) = reddit.getTopPostAndComments(randomSubreddit)
        logger.info("Potential Reddit posts scraped")

        #Create gTTS .mp3 files with reddit posts
        AudioMethods.removeAudioFolder()
        (numberOfCommentsUsed, audioLengths, postBody) = AudioMethods.textToSpeech(comments, 1.3, maxVideoLength,
                                                                                   silencePath="permAudio/500milsil.wav")
        parsedTextToSpeech = AudioMethods.parseTextToSpeechWavs(maxVideoLength)
        if len(parsedTextToSpeech) > 0:
            foundUsableRedditPosts = True
            logger.info(f"Reddit post used: {comments}")
        else:
            logger.warn(f"Reddit posts not accepted, retrying {count}/{retries}...")

    logger.info("Text to speech sucessfully created, moving on")
    logger.info(f"Post url(s): {urls}")

    #gets the comment ids only of the comments that are used to make the mp3
    commentIdsUsed = commentIdsPulled[:numberOfCommentsUsed]

    #Take screenshots of reddit posts
    screenShotter = WebHandler(driverLocation, headless=True)
    screenShotter.screenShotReddit(urls, commentIds=commentIdsUsed)

    #Pull random audio file from bndms directory and change it's length to match the TTS file
    randomBackgroundMusic = AudioMethods.getRandomFile("bndms")
    AudioMethods.convertMP3ToWav(f"bndms/{randomBackgroundMusic}", "audio/convertedMusic.wav")

    # getting duration of background music
    clip = AudioFileClip("audio/convertedMusic.wav")
    # clip 2 is the duration of the TTS file
    clip2 = AudioFileClip(parsedTextToSpeech[0])
    clipDuration = clip.duration
    clip2Duration = clip2.duration
    clip.close()
    clip2.close()

    AudioMethods.changeAudioClipStart("audio/convertedMusic.wav", "audio/newStart.wav",
                                      random.uniform(0, clipDuration - clip2Duration), clip2Duration)
    AudioMethods.changeAudioClipVolume("audio/newStart.wav", "audio/changedVol.wav", .15)
    AudioMethods.makeAudioFileSameLength(parsedTextToSpeech[0], "audio/changedVol.wav")
    logger.info("background music created")

    #Merge TTS audio with background music 
    AudioMethods.mergeAudioFiles([parsedTextToSpeech[0], "audio/modMusic.wav"])
    logger.info("Audio files merged")

    #Get duration of the merged .wav file
    finalAudio = AudioFileClip("audio/finalAudio.wav")
    finalAudioDuration = finalAudio.duration
    finalAudio.close()
    #Pull random video from bndvd directory and format it for youtube shorts
    randomBackgroundVideo = AudioMethods.getRandomFile("bndvd")
    backgroundVideoStart = VideoMethods.getRandomPointInVideo(f"bndvd/{randomBackgroundVideo}")
    VideoMethods.formatBackgroundVideoForYoutubeShort(f"bndvd/{randomBackgroundVideo}", finalAudioDuration,
                                                      startCut=backgroundVideoStart)
    logger.info("Background video formatted")

    #Resize post screenshot(s) to fit youtube shorts
    #list of resized image widths
    imageWidths = []

    #Grabs filenumber from string
    fileNumber = int(parsedTextToSpeech[0][6:7])
    #resizing main post images
    (imageWidth, _imageHeight) = VideoMethods.resizeImageForYouTubeShort(f"images/{fileNumber}.png")
    imageWidths.append(imageWidth)
    #list of relative filepaths to the images being turned into videos
    imagePaths = [f"images/{fileNumber}.png"]

    for count in range(1,numberOfCommentsUsed + 1):
        imagePaths.append(f"images/comment{count}.png")
        (imageWidth, _imageHeight) = VideoMethods.resizeImageForYouTubeShort(imagePaths[count])
        imageWidths.append(imageWidth)

    logger.info("Images resized")

    # Turns post image into .mp4 file
    #startTimes is a list of the durations of the image videos
    startTimes = VideoMethods.createImageVideo(imagePaths, audioLengths, finalAudioDuration=finalAudioDuration,
                                  silencePath="permAudio/500milsil.wav", postBody=postBody)
    logger.info("Image video created")

    #Merge background video with post video
    #Finds correct yPositions for the images in the video
    count = 0
    for width in imageWidths:
        # YouTube shorts are 1080 pixels wide
        imageWidths[count] = (1080 - width) / 2
        count += 1
    imageVideos = os.listdir("./video/imageVideo")
    count = 0
    for video in imageVideos:
        imageVideos[count] = f"video/imageVideo/{video}"
        count += 1
    imageVideos.insert(0, "video/silentVideo.mp4")
    VideoMethods.combineVideoClips(imageVideos, xPosition=65, yPosition=imageWidths,
                                   startTimes=startTimes)
    logger.info("Final Video made")

    #Combine merged audio file with merged video file
    VideoMethods.setVideoClipAudio("video/combinedVideo.mp4", "audio/finalAudio.wav")
    logger.info("Final video given Audio")

    #Pull title and description from comments
    title = f"{comments[fileNumber - 1][0].upper()}!?!?!? #Shorts "
    if len(title) > 50:
        title = f"{title[:50].upper()}!?!?!? #Shorts "
    description = f"{comments[fileNumber - 1][0]}\n\n To make videos like this check out my github at " \
                  f"github.com/zacpet19/YouTubeBot"
    #tags should be a list of tag(s) and the comments are used to separate the tags
    tags = ["entertainment,", "gaming,", "reddit,", "askreddit", "funny,"]
    videoData = {"Title" : title, "Description" : description, "Tags" : tags}

    #Upload video to youtube
    count = 0
    while count <= 4:
        count += 1
        try:
            screenShotter.uploadYoutubeVideo(channel, gmail, password, finalVideoPath, videoData)
            count += 10
        except Exception as e:
            #takes screenshot of current state of webpage to help figure out why it threw an error
            screenShotter.driver.save_screenshot(f"error{count}.png")
            if count == 4:
                logger.error("Retries exceeded video upload failed, shutting down")
                sys.exit()
            logger.warn(f"Upload failed retrying {count}/3")

    logger.info("Video uploaded")
    logger.info(f"Video Name: {title}")
    logger.info("Background music used: " + randomBackgroundMusic)
    logger.info("Background video used " + randomBackgroundVideo)

    logger.manageLogFile(5, 100000)
    reddit.manageVisitedRedditPages(30000, 150)


if __name__ == '__main__':
    main()

