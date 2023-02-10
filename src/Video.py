from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import concatenate_videoclips
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
import moviepy.video.fx.all as vfx
from moviepy.editor import AudioFileClip
from PIL import Image
import os
import random
import shutil


class VideoMethods:
    """VideoMethods class is methods for general Video file manipulation/creation for use in YouTube videos."""
    @staticmethod
    def formatBackgroundVideoForYoutubeShort(videoPath : str, duration : int, startCut=0):
        """Takes in a filepath to a mp4 file and then makes it the input duration. If the video is longer than the
        duration it cuts the end of the video to the given duration and if the video is shorter than the given
        duration it loops it until it is long enough. The startCut parameter allows for choosing when to start the
        video."""
        if not os.path.exists("./video"):
            os.makedirs("./video")
        try:
            #might want to find a different method of resizing the video because depending on the initial quality of
            #the video it could be really ugly
            clip = VideoFileClip(videoPath, target_resolution=(1920, 1080))
        except Exception as e:
            print("Error: Could not find file.")
            return False
        if startCut > clip.duration:
            print("Error: startCut is greater than the length of the clip.")
        if startCut + duration < clip.duration:
            cutClip = clip.subclip(startCut, duration + startCut)
            cutClip.write_videofile("video/silentVideo.mp4", fps=24, audio=False)
            cutClip.close()
        else:
            if startCut != 0:
                firstHalf = clip.subclip(0, startCut)
                secondHalf = clip.subclip(startCut, clip.duration)
                concat = concatenate_videoclips([secondHalf, firstHalf])
                final = concat.fx(vfx.loop, duration=duration) #ignore IDE about no reference to loop method
                final.write_videofile("video/silentVideo.mp4", fps=24, audio=False)
                firstHalf.close()
                secondHalf.close()
                concat.close()
                final.close()
            else:
                loopedVideo = clip.fx(vfx.loop, duration=duration) #ignore IDE about no reference to loop method
                loopedVideo.write_videofile("video/silentVideo.mp4", fps=24, audio=False)
                loopedVideo.close()
        clip.close()

    @staticmethod
    def getRandomPointInVideo(videoPath : str) -> int:
        """Takes in a filepath to a mp4 file and then returns a random number within the duration of the clip in
        seconds."""
        clip = VideoFileClip(videoPath)
        clipDuration = int(clip.duration)
        clip.close()
        return random.randrange(0, clipDuration)

    @staticmethod
    def resizeImageForYouTubeShort(imagePath : str):
        """This method is a general resizing method for images that will make its dimensions even because MoviePy
        only can make image videos of images with even dimensions. It also makes the image a bit bigger. The image
        should be resized before video creation to help keep the quality of the image. It also returns the new height
        and width to help with formatting the video"""
        if not os.path.exists("./images"):
            os.makedirs("./images")
        try:
            image = Image.open(imagePath)
        except Exception as e:
            print("File not found")
            raise e
        (width, height) = image.size
        height = int(height * 1.35)
        width = int(width * 1.45)
        #gives image even dimensions because moviepy image videos need to have even dimensions or they dont work
        if height % 2 != 0:
            height += 1
        if width % 2 != 0:
            width += 1
        reSizedImage = image.resize((width, height))
        reSizedImage.save(imagePath, quality=100)
        reSizedImage.close()
        image.close()
        return (width, height)

    @staticmethod
    def resizeImage(imagePath : str, width : int, height : int):
        """General method for resizing an image."""
        if not os.path.exists("./images"):
            os.makedirs("./images")
        try:
            image = Image.open(imagePath)
        except Exception as e:
            print("File not found")
            raise e
        reSizedImage = image.resize((width, height))
        reSizedImage.save("images/reSizedImage.png", quality=100)
        reSizedImage.close()
        image.close()

    @staticmethod
    def createImageVideo(imagePath : list[str], duration : list, finalAudioDuration=None, silencePath="", postBody=False):
        """Takes in a list of file paths to the image files and a list of the durations. The list of durations can be
         any numeric primitive. Then it saves the newly made image videos into memory and returns nothing. The image and
         the duration you want the video of it to have should have the same index in their respective lists. IMPORTANT:
         Image passed in must have even dimensions or the video made will be blank!!!!"""
        if postBody:
            #list of durations given have a duration for title and post when they share the same image
            if len(imagePath) != len(duration) - 1:
                print("Error: List of images paths should be equal to list of durations")
                raise
        else:
            if len(imagePath) != len(duration):
                print("Error: List of images paths should be equal to list of durations")
                raise
        #makes sure every item in duration is a float or integer
        #is this code useful or necessary??????????????????
        count = 0
        for num in duration:
            if type(num) is int:
                duration[count] = float(num)
            if type(duration[count]) is not float:
                print("Error: duration must be a list of numeric primitives")
                raise
            count += 1
        if not os.path.exists("./video/"):
            os.makedirs("./video")
        if not os.path.exists("./video/imageVideo"):
            os.makedirs("./video/imageVideo")
        #combines title and post body duration as they share the same image
        if postBody:
            duration[0] += duration.pop(1)
        #adds the duration of the silence path variable provided to all the durations except the last one
        if silencePath != "":
            try:
                inBetweenClip = AudioFileClip(silencePath)
            except Exception as e:
                print(f"File provided {silencePath} not found")
                raise e
            inBetweenClipDuration = inBetweenClip.duration
            count = 0
            while count < len(duration) - 1:
                duration[count] += inBetweenClipDuration
                count += 1
            inBetweenClip.close()
        #adds missing duration to final image clip if the total duration of the clips is not as long
        if finalAudioDuration is not None:
            totalDuration = 0
            for num in duration:
                totalDuration += num
            if totalDuration < finalAudioDuration:
                duration[-1] += (finalAudioDuration - totalDuration)
        for count in range(len(imagePath)):
            try:
                clip = ImageClip(imagePath[count], duration=duration[count])
            except Exception as e:
                print("Error: Could not find file.")
                return False
            clip.write_videofile(f"video/imageVideo/{count + 1}.mp4", fps=7)
            clip.close()
        return duration

    @staticmethod
    def deleteImageVideoFolder():
        if os.path.exists("video/imageVideo"):
            shutil.rmtree("video/imageVideo")


    @staticmethod
    def resizeVideoClip(clipPath : str, height : int, width : int):
        """Takes in a path to a video clip and parameters for the resolution for it to be resized into. Then it saves
        it into the "video" directory."""
        if not os.path.exists("./video"):
            os.makedirs("./video")
        try:
            clip = VideoFileClip(clipPath, target_resolution=(height, width))
        except Exception as e:
            print("Error: Could not find file.")
            return False
        clip.write_videofile("video/resizedVideo.mp4")
        clip.close()

    @staticmethod
    def combineVideoClips(filePaths : list[str], xPosition=None, yPosition=None, startTimes=None, backgroundVideo=True):
        """Combines all video clips provided into one video. xPosition and yPostion allow you to choose the position
        which other videos are placed over the first one. startTimes should a list of when you want the videos to begin
        in the final video other than the background video if one is provided. All videos need a start time otherwise
        they will start at time 0. Provided start times should share the same order as the provided mp4 locations bar
        the first one if backgroundVideo is True."""
        if not os.path.exists("./video"):
            os.makedirs("./video")
        if startTimes is None:
            startTimes = []
        #xPos and yPos are defaulted to 0
        if xPosition is None:
            xPosition = 0
        if yPosition is None:
            yPosition = 0
        clips = []
        for path in filePaths:
            try:
                clips.append(VideoFileClip(path))
            except Exception as e:
                print("One or more of provided files not found.")
                raise e
        if len(clips) <= 1:
            print("Error: One or more clips must be provided")
        #New list to store copies of clips created from pymovie video formatting methods
        formattedClips = []
        count = 0
        #background videos do not receive positional arguments
        if backgroundVideo:
            formattedClips.append(clips[0])
            count += 1
        startTime = 0
        while count < len(clips):
            tempX = xPosition
            tempY = yPosition
            if type(xPosition) is list:
                if backgroundVideo:
                    if len(xPosition) >= count:
                        tempX = xPosition[count - 1]
                else:
                    if len(xPosition) > count:
                        tempX = xPosition[count]
            if type(yPosition) is list:
                if backgroundVideo:
                    if len(yPosition) >= count:
                        tempY = yPosition[count - 1]
                else:
                    if len(yPosition) > count:
                        tempY = yPosition[count]
            clip = clips[count].set_position((tempX, tempY))
            if backgroundVideo:
                formattedClips.append(clip.set_start(startTime))
                startTime += startTimes[count - 1]
            else:
                formattedClips.append(clip.set_start(startTime))
                startTime += startTimes[count]
            count += 1
        combinedClip = CompositeVideoClip(formattedClips)
        combinedClip.write_videofile("video/combinedVideo.mp4")
        combinedClip.close()
        #closeing the original clip closes all copies
        for clip in clips:
            clip.close()

    @staticmethod
    def setVideoClipAudio(videoClipPath : str, audioClipPath : str):
        """Takes in a filepath to a mp4 file and a mp3 file. Then sets the mp3 file as the audio of the mp4 and saves
        it to the "video" directory."""
        if not os.path.exists("./video"):
            os.makedirs("./video")
        try:
            videoClip = VideoFileClip(videoClipPath)
            audioClip = AudioFileClip(audioClipPath)
        except Exception as e:
            print("One or more of provided files not found.")
            raise e
        final = videoClip.set_audio(audioClip)
        final.write_videofile("video/finalVideo.mp4")
        videoClip.close()
        audioClip.close()
