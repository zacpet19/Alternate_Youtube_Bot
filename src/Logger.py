from datetime import datetime
import os
from dotenv import load_dotenv


class Logger:


    def __init__(self):
        if not os.path.exists("./logs.txt"):
            f = open("./logs.txt", "x", encoding="utf-8")
            f.close()

        self.name = "Epic logger"
        self.logFile = open("logs.txt","a", encoding="utf-8")
    
    def debug(self, string: str):
        text = f"[{self.getTime()}][DEBUG] {string}"
        self.logFile.write(text + '\n')
        print(text)

    def info(self, string: str):
        text = f"[{self.getTime()}][INFO] {string}"
        print(text)
        self.logFile.write(text + '\n')

    def warn(self, string: str):
        text = f"[{self.getTime()}][WARN] {string}"
        print(text)
        self.logFile.write(text + '\n')

    def error(self, string: str):
        text = f"[{self.getTime()}][ERROR] {string}"
        print(text)
        self.logFile.write(text + '\n')

    def getTime(self):
        now = datetime.now()
        return now.strftime("%d/%m/%Y %H:%M:%S")

    def manageLogFile(self, maxLogs : int, bytesAllowedPerLog : int):
        """Manage log file method will create legacy log files and new log files if current one goes over the
        bytesAllowedPerLog parameter. Max logs is the amount of legacy logs you want to keep. The oldest logs will
        be deleted if they exceed the number of max logs. The naming convention given to the logs is newest being the
        smallest number and the oldest having the largest number."""
        if not os.path.exists("./oldLogs"):
            os.makedirs("./oldLogs")

        if os.path.exists("./logs.txt"):
            if os.stat("./logs.txt").st_size > bytesAllowedPerLog:
                if os.path.exists(f"./oldLogs/old_logs{maxLogs}.txt"):
                    os.remove(f"./oldLogs/old_logs{maxLogs}.txt")
                    #taking into account new max logs number deletes all max logs exceeding it
                    count = maxLogs + 1
                    while os.path.exists(f"./oldLogs/old_logs{count}.txt"):
                        os.remove(f"./oldLogs/old_logs{count}.txt")
                        count += 1
                #renames all the old logs to show which ones are newer
                count = maxLogs - 1
                while count > 0:
                    if os.path.exists(f"./oldLogs/old_logs{count}.txt"):
                        os.rename(f"./oldLogs/old_logs{count}.txt", f"./oldLogs/old_logs{count + 1}.txt")
                    count -= 1
                #closing file so it can be renamed
                self.logFile.close()
                os.rename("./logs.txt", f"./oldLogs/old_logs1.txt")
                #creating new logs.txt
                f = open("./logs.txt", "x", encoding="utf-8")
                f.close()
                self.logFile = open("logs.txt","a", encoding="utf-8")

