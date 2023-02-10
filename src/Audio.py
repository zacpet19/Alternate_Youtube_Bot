from gtts import gTTS
from moviepy.editor import AudioFileClip
from moviepy.editor import concatenate_audioclips
from moviepy.audio.fx.audio_loop import *
from moviepy.audio.fx.volumex import *
from moviepy.editor import CompositeAudioClip
import os
import random
import shutil
import librosa
import soundfile
from pydub import AudioSegment
from pydub.effects import speedup


"""Current known Audio issues: Text to speech says random punctuation and says things you cant see like if there is a 
whole bunch of spaces(ie. hashx200b was said multiple times in one. at the end of some videos there is a "brrt" sound"""

class AudioMethods:
    """AudioMethods class is methods for general audio file manipulation/creation for use in YouTube videos."""
    @staticmethod
    def textToSpeech(text, playbackSpeed, maxLength, silencePath=""):
        """Takes in a 2d array of text (reddit post/comments and uses gTTP to turn it into a mp3 file and then saves it
        into memory while keeping it under a minute long. The silence path is a variable that takes in the file path to
        a silence audioClip if you would like to have pauses between comments and posts. You could add any other mp3
        files between them as well. Returns an array of the number of comments used to make each mp3. The order of the
         returned array is in the same order the posts were given."""
        if not os.path.exists("./audio"):
            os.makedirs("./audio")
        count = 1
        #this is to help account for added audio duration from a silent clip or anything else in between posts/comments
        inBetweenAudioDuration = 0
        if silencePath != "":
            try:
                inBetweenAudio = AudioFileClip(silencePath)
            except Exception as e:
                print("Error: Failed to find provided audio path")
                raise e
            inBetweenAudioDuration = inBetweenAudio.duration
            inBetweenAudio.close()
        commentsUsed = 0
        #list of durations(floats) for each comment mp4 made
        mp4Durations = []
        postBody = True
        for i in text:
            if not os.path.exists(f"./audio/post{count}"):
                os.makedirs(f"./audio/post{count}")
            duration = 0
            innerCount = 1
            for j in i:
                #reddit scraper will pull empty string if the post body is empty and this is to address that
                if j == "":
                    if innerCount == 2:
                        postBody = False
                    continue
                #creating individual audio clips
                audio = gTTS(text=j,lang = "en", slow=False, tld = "US")
                audio.save(f"./audio/post{count}/{innerCount}.mp3")
                #changes newly made audio file to wav and then deletes the mp3
                AudioMethods.convertMP3ToWav(f"./audio/post{count}/{innerCount}.mp3",
                                             f"./audio/post{count}/{innerCount}.wav")
                os.remove(f"./audio/post{count}/{innerCount}.mp3")
                #modifys the wav playback speed and then saves over previous wav
                AudioMethods.modifyWavPlaybackSpeed(f"./audio/post{count}/{innerCount}.wav",
                                                    f"./audio/post{count}/{innerCount}.wav", playbackSpeed)
                audioToAdd = AudioFileClip(f"./audio/post{count}/{innerCount}.wav")
                duration += audioToAdd.duration
                audioToAdd.close()
                if duration >= maxLength:
                    break
                duration += inBetweenAudioDuration
                innerCount += 1
            #wont create final clip if only title audio clips was made
            if innerCount > 2:
                audioFilePaths = os.listdir(f"./audio/post{count}")
                #removes last audio file created because it would make the clip go over 60 seconds
                if duration >= maxLength:
                    audioFilePaths.pop()
                if postBody:
                    #subtracts 2 to account for post title and body
                    commentsUsed = (len(audioFilePaths) - 2)
                else:
                    #only subtracts 1 if not post body
                    commentsUsed = (len(audioFilePaths) - 1)
                clips = []
                for c in audioFilePaths:
                    clips.append(AudioFileClip(f"./audio/post{count}/{c}"))
                    mp4Durations.append(clips[-1].duration)
                    #adds the audio clip you want played in between comments/posts
                    if silencePath != "" and c != audioFilePaths[-1]:
                        clips.append(AudioFileClip(silencePath))
                finalClip = concatenate_audioclips(clips)
                finalClip.write_audiofile(f"audio/{count}.wav")
                for clip in clips:
                    clip.close()
            else:
                print("Initial text body provided was too long or only post title audio was included")
            #Be careful messing with this because it removes an entire directory and all things below it
            shutil.rmtree(f"audio/post{count}")
            count += 1
        #returns an int, a list of floats, and a boolean
        return (commentsUsed, mp4Durations, postBody)

    @staticmethod
    def parseTextToSpeechMP3s():
        """Parses the text to speech mp3 files by making sure they are not too short to long. Returns a list of the
        file names that match the given criteria. Notably will return an empty list if no suitable files are found."""
        if not os.path.exists("./audio"):
            return []
        count = 1
        textToSpeechFileNames = []
        while count < 6:
            if os.path.exists(f"audio/{count}.mp3"):
                clip = AudioFileClip(f"audio/{count}.mp3")
                if 20 < clip.duration < 60:
                    textToSpeechFileNames.append(f"audio/{count}.mp3")
                clip.close()
            count += 1
        return textToSpeechFileNames

    @staticmethod
    def parseTextToSpeechWavs(maxLength):
        """Parses the text to speech wav files by making sure they are not too short to long. Returns a list of the
        file names that match the given criteria. Notably will return an empty list if no suitable files are found."""
        if not os.path.exists("./audio"):
            return []
        count = 1
        textToSpeechFileNames = []
        while count < 6:
            if os.path.exists(f"audio/{count}.wav"):
                clip = AudioFileClip(f"audio/{count}.wav")
                if 15 < clip.duration < maxLength:
                    textToSpeechFileNames.append(f"audio/{count}.wav")
                clip.close()
            count += 1
        return textToSpeechFileNames

    @staticmethod
    def removeAudioFolder():
        """Removes the audio folder and all subdirectories. Does nothing if audio folder doesn't exist. Many methods of
        this class will create a folder named audio in the CWD."""
        if os.path.exists("./audio"):
            #Be careful messing around with this as it removes entire directories
            shutil.rmtree("audio")

    @staticmethod
    def makeAudioFileSameLength(clipPath : str, clipToChangePath : str):
        """This will take in filepaths to two audio files with the first file being the one that will set the length
        for the other file. If the first file is shorter it will cut the clip to be change to that size and if the first
        file is longer it will loop the clip to change until it is the same length.Returns false if files cannot be
        found."""
        #TODO: implement random start point music clip provided
        if not os.path.exists("./audio"):
            os.makedirs("./audio")
        try:
            clip = AudioFileClip(clipPath)
            clipToChange = AudioFileClip(clipToChangePath)
        except Exception as e:
            print("Error: Failed to find one or more of provided files.")
            return False
        #the audio being changed is looped if it is not longer than the other clip
        if clip.duration < clipToChange.duration:
            clipToChangeSubclip = clipToChange.subclip(0, clip.duration)
            clipToChangeSubclip.write_audiofile("audio/modMusic.wav")
            clipToChangeSubclip.close()
        else:
            clipToChangeLooped = audio_loop(clipToChange, duration=clip.duration)
            clipToChangeLooped.write_audiofile("audio/modMusic.wav")
            clipToChangeLooped.close()
        clip.close()
        clipToChange.close()

    @staticmethod
    def mergeAudioFiles(clipsToMerge : list):
        """Takes in a list of audio clip objects and then merges them all together and saves the new clip into memory.
        They will all start at the same time so if they vary in length the longest one will continue to play to
        completion after the others have stopped"""
        if not os.path.exists("./audio"):
            os.makedirs("./audio")
        if len(clipsToMerge) <= 1:
            print("Error: List size must be greater that one.")
            return False
        audioFiles = []
        try:
            for clip in clipsToMerge:
                audioFiles.append(AudioFileClip(clip))
        except Exception as e:
            print("Error: Failed to find one or more provided files.")
            raise e
        mergedAudio = CompositeAudioClip(audioFiles)
        mergedAudio.write_audiofile("audio/finalAudio.wav", fps=44100)
        mergedAudio.close()
        for file in audioFiles:
            file.close()

    @staticmethod
    def changeAudioClipStart(clipPath: str, newClip: str, newStart: float, duration: float):
        """Takes in a filepath to an audio file and then while keeping the original duration starts the clip at the
        newly provided start time. Moving the front part of the clip to the end."""
        try:
            clip = AudioFileClip(clipPath)
        except Exception as e:
            print("Error: Failed to find provided filepath.")
            return False
        if newStart >= clip.duration or newStart < 0:
            print(f"Warn: The new start must be within the bounds of the provided clips duration: {clip.duration}")
            print("New clip will be renamed with newStart set to 0")
            newStart = 0
        # Just saves the file with the new name if the clip isnt longer than the provided duration
        if duration >= clip.duration:
            clip.write_audiofile(newClip)
            clip.close()
            return
        final = clip.subclip(newStart, newStart + duration)
        final.write_audiofile(newClip)
        clip.close()

    @staticmethod
    def randomAudioCutout(clipToCutPath : str, duration : int):
        """This method takes in a filepath to and mp3 and a duration you want the new clip to be. Then it randomly
        creates a subclip of the provided duration and then saves it into memory. It will return false if given
        unusable parameters."""
        if not os.path.exists("./audio"):
            os.makedirs("./audio")
        if duration == 0:
            print("Error: Duration must be longer than 0")
            return False
        try:
            clip = AudioFileClip(clipToCutPath)
            clipDuration = int(clip.duration)
        except Exception as e:
            print("Error: Failed to find one or more of provided filepaths.")
            return False
        if duration >= clipDuration:
            clip.close()
            print("Error: Duration given longer than audio file length")
            return False
        cut = random.randrange(duration, clipDuration + 1)
        cutAudio = clip.subclip(cut - duration, cut)
        cutAudio.write_audiofile("audio/cutoutAudio.mp3")
        cutAudio.close()
        clip.close()

    @staticmethod
    def getRandomFile(directory : str) -> str:
        """Returns the name of a random file from a given directory. Returns an empty string on failure."""
        try:
            files = os.listdir(directory)
        except Exception as e:
            print("Error: Failed to find directory.")
            return ""
        if len(files) == 0:
            print("Error: Directory has no files.")
            return ""
        randomNum = random.randrange(0, len(files))
        return files[randomNum]

    @staticmethod
    def changeAudioClipVolume(clipToChange : str, newFileName : str, volume):
        """Uses moviepy to create a new clip with a new volume. Unsure at this time how different number exactly impact
        audio but any volume lower than 1 lowers the volume and anything above 1 should raise the volume. The
        parameter clipToChange should be a file path to a audio file and volume can be an int or a double."""
        if volume <= 0:
            print("New Volume must be larger than 0")
            return False
        try:
            newClip = AudioFileClip(clipToChange)
        except Exception as e:
            print("Error: Failed to find one or more of provided filepaths.")
            return False
        change = volumex(newClip, volume)
        change.write_audiofile(newFileName)
        newClip.close()
        change.close()

    @staticmethod
    def convertMP3ToWav(mp3 : str, wav : str):
        """Takes in the relative or absolute path of an mp3 file and then converts it into a wave file with the new name
        given. WARN: Be careful converting files between each other too much because they begin to cut off for some
        reason."""
        sound = AudioSegment.from_mp3(mp3)
        sound.export(wav, format="wav")

    @staticmethod
    def createWavWithNewPitch(wavPath : str, newWav : str, step : int):
        """Creates a new wav file with a new given step. Negative step will increase the pitch and postive step will
        increase it. Notably significantly lowers the audio quality but keeps it the same length."""
        y, sr = librosa.load(wavPath)
        steps = float(step)
        new_y = librosa.effects.pitch_shift(y, sr=sr, n_steps=steps)
        soundfile.write(newWav, new_y, sr, )

    @staticmethod
    def convertWavToMP3(wav : str, mp3 : str):
        """Takes in a relative or absolute wav file path and then converts it into a mp3 file with the new given name.
        WARN: Be careful converting files between each other too much because they begin to cut off for so reason."""
        sound = AudioSegment.from_wav(wav)
        sound.export(mp3, format="mp3")

    @staticmethod
    def timeStretchWav(wavPath : str, newWav : str, rate : float):
        """Takes in a file path to a .wav file and then saves a new one with the given name. The rate variable is a
        float based around 1 being the default and then th float being the stretch factor. Notably this method has a
        high impact on audio quality."""
        y, sr = librosa.load(wavPath)
        changedRate = librosa.effects.time_stretch(y, rate)
        soundfile.write(newWav, changedRate, sr,)

    @staticmethod
    def modifyWavPlaybackSpeed(wavPath : str, newWav : str, speed : float):
        """This method takes in the path to a .wav file and then saves a new one with the given title. The default
        playback speed is 1 and then the given number will change the playback speed by a factor of the given number.
        Notably audio quality may begin to drop at high playback speeds."""
        sound = AudioSegment.from_wav(wavPath)
        crossfade = 25
        if speed > 1.25:
            #ratio for changing crossfade to make higher playback speeds sound better
            crossfade = crossfade * 1.28
        newSound = speedup(sound, speed, 150, crossfade)
        newSound.export(newWav, format="wav")









