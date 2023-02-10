YouTubeBot README

Overall Description: For more detailed description see the regular version of YouTubeBot on my GitHub:
https://github.com/zacpet19/YouTubeBot. This version swicthes to Python 3.10. It does this to be able to use the Librosa
Python library. The library requires FFMPeg to be installed in order to be used. The FFMPeg website provides
documentation on how to set it up. This version of the program uses .wav files for audio and has the ability to change
the playback speeds and pitch of audio files. There is no differences beyond that however going forward this will likely
become the main program.

Link to YouTube channel: https://www.youtube.com/@jamesano
Videos will look like the newer ones on this YouTube page

IMPORTANT: This is not yet a finished project. It can currently create and upload YouTube shorts. However, functionality
is limited and has bugs that make it occasionally not work as intended.

Known bugs:
Some audio clips after combining will have "brrt" sound at the end
YouTube will occasionally require 2-factor authentication even when disabled causing upload process to fail
Fails to log into gmail when faced with anti-bot countermeasures
Selenium will occasionally fail and then work under similar circumstances

TODO:
Implement proxy rotation to avoid google CAPTCHA
Make upload method work with 2-factor authentication
Write tests for all methods
implement logger into classes
Change Reddit scraper return structure
Make constructor method for Audio class?
Make constructor method for Video class?
Make method that changes audio pitch
Give selenium better error handling
Continue to improve censorship methods