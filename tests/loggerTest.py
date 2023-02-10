import sys
sys.path.append('..')
import shutil
import os

from src.Logger import Logger

def loggerTest():
    logger = Logger()
    assert type(logger) == Logger
    logger.warn("this is a warning")
    logger.debug("this is a debug")
    logger.info("this is a info")
    logger.error("this is an error")
    assert logger.name == "Epic logger"

def manageLogFileTest():
    logger = Logger()

    assert os.path.exists("./logs.txt")

    logger.manageLogFile(6, 25000)

    assert os.path.exists("./logs.txt")
    assert os.path.exists("./oldLogs")
    assert os.path.exists("./oldLogs/old_logs1.txt")

    logger.logFile.close()
    os.remove("./logs.txt")
    shutil.copy("./oldLogs/old_logs1.txt", "./logs.txt")
    logger.logFile = open("logs.txt","a", encoding="utf-8")
    logger.manageLogFile(6, 25000)

    assert os.path.exists("./logs.txt")
    assert os.path.exists("./oldLogs/old_logs1.txt")
    assert os.path.exists("./oldLogs/old_logs2.txt")

    logger.logFile.close()
    os.remove("./logs.txt")
    shutil.copy("./oldLogs/old_logs1.txt", "./logs.txt")
    logger.logFile = open("logs.txt", "a", encoding="utf-8")
    logger.manageLogFile(2, 25000)

    assert os.path.exists("./logs.txt")
    assert os.path.exists("./oldLogs/old_logs1.txt")
    assert os.path.exists("./oldLogs/old_logs2.txt")
    assert not os.path.exists("./oldLogs/old_logs3.txt")

    logger.logFile.close()
    os.remove("./logs.txt")
    shutil.copy("./oldLogs/old_logs1.txt", "./logs.txt")
    shutil.copy("./oldLogs/old_logs1.txt", "./oldLogs/old_logs3.txt")
    shutil.copy("./oldLogs/old_logs1.txt", "./oldLogs/old_logs4.txt")
    shutil.copy("./oldLogs/old_logs1.txt", "./oldLogs/old_logs5.txt")
    logger.logFile = open("logs.txt", "a", encoding="utf-8")
    logger.manageLogFile(3, 25000)

    assert os.path.exists("./logs.txt")
    assert os.path.exists("./oldLogs/old_logs1.txt")
    assert os.path.exists("./oldLogs/old_logs2.txt")
    assert os.path.exists("./oldLogs/old_logs3.txt")
    assert not os.path.exists("./oldLogs/old_logs4.txt")
    assert not os.path.exists("./oldLogs/old_logs5.txt")

    logger.manageLogFile(3, 25000)

    assert os.path.exists("./logs.txt")
    assert os.path.exists("./oldLogs/old_logs1.txt")
    assert os.path.exists("./oldLogs/old_logs2.txt")
    assert os.path.exists("./oldLogs/old_logs3.txt")
    assert not os.path.exists("./oldLogs/old_logs4.txt")
    assert os.stat("./oldLogs/old_logs1.txt").st_size > 100

    logger.logFile.close()
    shutil.copy("./oldLogs/old_logs1.txt", "./logs.txt")
    shutil.rmtree("./oldLogs")
    print("Manage log file test passed")


loggerTest()
manageLogFileTest()
