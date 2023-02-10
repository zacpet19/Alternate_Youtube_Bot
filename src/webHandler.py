from selenium import webdriver
from PIL import Image
import io
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv

class WebHandler:
    """This class is contains general methods for using selenium to interact with the Google Chrome."""
    def __init__(self, path, headless=False):
        """Creates an object with the Selenium chrome driver. Takes in the file path to the chrome driver."""
        self.ser = Service(path)
        self.options = webdriver.ChromeOptions()
        #for headless chrome
        if headless:
            #Need to change user agent from normal headless one so google doesn't block access
            load_dotenv()
            userAgent = os.getenv('seleniumUserAgent')
            self.options.add_argument(f"user-agent={userAgent}")
            self.options.add_argument("window-size=1920,1080")
            self.options.headless = True
            self.driver = None

    def screenShotReddit(self, urls : list[str], commentIds=None):
        """function(url) -> None, saves screenshot in ./images directory. commentIds gives the option to screenshot
        Reddit comments given their IDS as they are pulled by the Praw Reddit API. commentIds should be given as a list
        of Ids."""
        #TODO: make urls a string instead of a list
        try:
            self.driver = webdriver.Chrome(service=self.ser, options=self.options)
        except Exception as e:
            print("Error : failed to open chrome driver")
            raise e
        action = ActionChains(self.driver)
        if not os.path.exists("./images"):
            os.makedirs("./images")
        self.driver.maximize_window()
        count = 1
        for url in urls:
            try:
                self.driver.get(url)
            except Exception as e:
                print("Error: Failed to access URL")
                raise e
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='post-container']")
            except Exception as e:
                print("Error: failed to find CSS element on webpage")
                raise e
            #this pause is to give reddit comments more time to load because some posts have very long comment chains
            #TODO: Find way to get rid of hard pause
            action.pause(2).perform()
            image = element.screenshot_as_png
            imageStream = io.BytesIO(image)
            im = Image.open(imageStream)
            im.save(f"./images/{count}.png")
            count += 1
        #screenshotting comments
        for (index, c) in enumerate(commentIds):
            # this pause is to give reddit comments more time to load because some posts have very long comment chains
            # TODO: Find way to get rid of hard pause
            action.pause(4).perform()
            try:
                #Praw doesnt pull entire comment ID but they all start with t1_
                element = self.driver.find_element(By.ID, "t1_" + c)
            except Exception as e:
                element = None
                print(f"ERROR: Comment #{index + 1} ID not found")
            if element is not None:
                image = element.screenshot_as_png
                imageStream = io.BytesIO(image)
                im = Image.open(imageStream)
                im.save(f"./images/comment{index + 1}.png")
        self.driver.quit()

    def uploadYoutubeVideo(self, channel : str, username : str, password : str, filepath : str, videoInfo : dict):
        """this method takes in a url to a channel, a gmail username/password, a filepath to the mp4 you would like
        to upload, and a dictionary containing video info on the title and description. Then it uses selenium to upload
        the video to the YouTube channel provided. IMPORTANT: Does not work with 2 factor identification!!!"""
        """TODO Make it possible to add tags and do way more exception handling"""
        try:
            self.driver = webdriver.Chrome(service=self.ser, options=self.options)
        except Exception as e:
            print("Error: failed to open chrome driver")
        enter = Keys.ENTER
        #searching for youtube page
        try:
            self.driver.get(channel)
        except Exception as e:
            print("Youtube channel not found.")
            raise e
        wait = WebDriverWait(self.driver, 10)
        #clicking on the sign in button
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//ytd-button-renderer[@class='style-scope ytd-masthead']//a[@aria-label='Sign in']//div[@class='yt-spec-touch-feedback-shape__fill']")))
        except Exception as e:
            print("Sign in not found or Webpage took too long to load")
            raise e
        #clicking on sign in box
        elementToMoveTo = self.driver.find_element(By.XPATH, "//ytd-button-renderer[@class='style-scope ytd-masthead']//a[@aria-label='Sign in']//div[@class='yt-spec-touch-feedback-shape__fill']")
        action = ActionChains(self.driver)
        action.move_to_element(elementToMoveTo).double_click().perform()
        attempts = 0
        #Typeing in username/email
        '#TODO: Consider adding something that deletes the previous attempt'
        while attempts < 5:
            action.send_keys(username).perform()
            try:
                attempts += 1
                WebDriverWait(self.driver, 2).until(EC.text_to_be_present_in_element_value((By.NAME, "identifier"), username))
                action.send_keys(enter).perform()
                break
            except Exception as e:
                if attempts >= 5:
                    print("Element name not found on Gmail login page or took too long to load")
                    raise e
        attempts = 0
        #Typing in password
        while attempts < 5:
            action.send_keys(password).perform()
            try:
                attempts += 1
                WebDriverWait(self.driver, 2).until(EC.text_to_be_present_in_element_value((By.NAME, "Passwd"), password))
                action.send_keys(enter).perform()
                break
            except Exception as e:
                if attempts >= 5:
                    print("Element name not found on Gmail login page or took too long to load")
                    raise e
        #clicking on the manage videos button
        try:
            elementToMoveTo = wait.until(EC.element_to_be_clickable((By.ID, "edit-buttons")))
        except Exception as e:
            print("Couldn't locate provided element or page took too long to load")
            raise e
        action.move_to_element(elementToMoveTo).perform()
        action.move_by_offset(yoffset=0, xoffset=100).click().perform()
        #switching to the newly opened window
        attempts = 0
        while attempts < 5:
            try:
                attempts += 1
                self.driver.switch_to.window(self.driver.window_handles[1])
            except Exception as e:
                print("Page took to long to load.")
                action.pause(3).perform()
                if attempts >= 5:
                    raise e
        #clicking video creation button
        action.pause(20).perform()
        try:
            elementToMoveTo = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.ID, "create-icon")))
        except Exception as e:
            print("Couldn't locate provided element or page took too long to load")
            raise e
        action.click(elementToMoveTo).perform()
        action.move_by_offset(yoffset=32, xoffset=0).click().perform()
        attempts = 0
        #sending video for upload
        #while loop tries to upload the video the enter key is to get rid of potential popups since if there is 0 popups
        #the enter key does nothing on that screen
        while attempts < 5:
            action.send_keys(enter).perform()
            "# have to send a file using the driver instead of the ActionChains object for some reason"
            self.driver.find_element(By.XPATH, '//*[@id="content"]/input').send_keys(filepath)
            try:
                wait.until(EC.element_to_be_clickable((By.ID, 'textbox')))
                break
            except Exception as e:
                print("Couldn't locate provided element or page took too long to load")
                if attempts >= 5:
                    raise e
        #video frequently takes a bit to upload so it pauses for 10 seconds no matter what might need to be longer for
        #bad connections and larger videos
        #TODO find a way to not do a set wait time
        action.pause(10)
        #typing Youtube video title
        action.send_keys(videoInfo["Title"]).perform()
        #this clears the menu that comes up when putting a # does nothing if there is no #'s in the title
        action.send_keys(enter).perform()
        #typing Youtube video description
        elementToMoveTo = self.driver.find_element(By.ID, "description-container")
        action.click(elementToMoveTo).send_keys(videoInfo["Description"]).perform()
        #these next two lines dont do anything as of right now but is necessary to add tags at a later point
        #clicks button that says video is not made for kids
        elementToMoveTo = self.driver.find_element(By.ID, "toggle-button")
        action.scroll_to_element(elementToMoveTo).perform()
        elementToMoveTo = self.driver.find_element(By.ID, "offRadio")
        action.move_to_element(elementToMoveTo).perform()
        action.move_by_offset(yoffset=25, xoffset=0).click().perform()
        elementToMoveTo = self.driver.find_element(By.ID, "toggle-button")
        action.scroll_to_element(elementToMoveTo).click(elementToMoveTo).perform()
        #adding tags to video
        elementToMoveTo = self.driver.find_element(By.ID, "tags-container")
        action.scroll_to_element(elementToMoveTo).perform()
        action.click(elementToMoveTo).perform()
        for tag in videoInfo["Tags"]:
            action.send_keys(tag).perform()
        elementToMoveTo = self.driver.find_element(By.ID, "next-button")
        action.click(elementToMoveTo).perform()
        action.click(elementToMoveTo).perform()
        action.click(elementToMoveTo).perform()
        #makes video viewable by public
        elementToMoveTo = self.driver.find_element(By.NAME, "PUBLIC")
        action.click(elementToMoveTo).perform()
        #completes upload of video
        elementToMoveTo = self.driver.find_element(By.ID, "done-button")
        action.click(elementToMoveTo).perform()
        #gets out of post video upload box
        # signing out of the gmail account after a video upload
        attempts = 0
        #Clicking past post video upload box
        while attempts < 5:
            attempts += 1
            try:
                elementToMoveTo = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ytcp-button[id='close-button'] div[class='label style-scope ytcp-button']")))
                action.move_to_element(elementToMoveTo).perform()
                break
            except Exception as e:
                print("Unable to find element sign out failed.")
                if attempts >= 5:
                    raise e
        action.click().perform()
        #clicking on account icon
        try:
            elementToMoveTo = wait.until(EC.element_to_be_clickable((By.ID, "avatar-btn")))
        except Exception as e:
            print("Unable to find element sign out failed.")
            raise e
        action.click(elementToMoveTo).perform()
        #pauses here to make video uploading more consistent as it will sometimes not upload properly if the Google
        #account is signed out of too early
        action.pause(120).perform()
        #clicking sign out button
        try:
            elementToMoveTo = wait.until(EC.element_to_be_clickable((By.ID, "contentWrapper")))
        except Exception as e:
            print("Unable to find element sign out failed.")
            raise e
        action.move_to_element(elementToMoveTo).perform()
        action.move_by_offset(0, 30).perform()
        action.click().perform()
        self.driver.quit()
