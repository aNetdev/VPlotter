import logging
import os
from plotter.plotter import Plotter, PenDirection
from datetime import datetime


def getLogger():
    l = logging.getLogger("plotterLog")
    l.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler(
        "plotterLog{date}.log".format(date=datetime.now().strftime('%Y%m%d')))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(logging.INFO)
    steam_handler.setFormatter(formatter)

    l.addHandler(file_handler)
    l.addHandler(steam_handler)
    return l


def getPlotter():
    plotter = Plotter([],100, 70)
    plotter.init(debug=False)
    return plotter


logger = getLogger()
logger.info("Starting")

myPlotter = getPlotter()

# Max dimensions xmin 30, x max250 ymin= 60, ymax 450

# read xy coordinates


def drawXYCoordinates(filePath, drawBorder):
    logger.info("Drawing XYCoordinates from %s", filePath)
    fs = open(filePath, "r")
    cords = fs.readlines()
    parsedCords = [cord.strip().split() for cord in cords]
    x = [int(v[0]) for v in parsedCords]
    y = [int(v[1]) for v in parsedCords]

    minX = min(x)
    maxX = max(x)

    minY = min(y)
    maxY = max(y)

    myPlotter = getPlotter()
    
    myPlotter.enableSteppers()
    #top left
    logger.info("Moving to top left")
    myPlotter.moveTo(minX, minY, PenDirection.Up)

    myPlotter.moveTo(minX+10, minY, PenDirection.Down)    #top left corner horizontal line
    myPlotter.moveTo(maxX-10, minY, PenDirection.Up)      

    #top Right
    logger.info("Moving to top right")
    myPlotter.moveTo(maxX, minY, PenDirection.Down) #top right corner horizontal line
    
    myPlotter.moveTo(maxX, minY+10, PenDirection.Down)   #top right corner vertical line

    myPlotter.moveTo(maxX,maxY-10, PenDirection.Up)
    #bottom Right
    logger.info("Moving to bottom right")
    myPlotter.moveTo(maxX,maxY, PenDirection.Down)  #bottom right corner vertical line
    
    myPlotter.moveTo(maxX-10,maxY, PenDirection.Down)   #bottom right corner horizontal line
    myPlotter.moveTo(minX+10,maxY, PenDirection.Up)
    #bottom left
    logger.info("Moving to bottom left")
    myPlotter.moveTo(minX,maxY, PenDirection.Down) #bottom left corner horizontal line
    myPlotter.moveTo(minX,maxY-10, PenDirection.Down) #bottom left corner vertical line
    
    input("Done with border. Enter to continue")
    total =len(parsedCords)
    current =0
    logger.info("Plotting started")
    for pc in parsedCords:
        x = int(pc[0])
        y = int(pc[1])
        pen = PenDirection.Down if pc[2] == "0" else PenDirection.Up
        myPlotter.moveTo(x, y, pen)
        perComplete =round(current/total * 100 ,2)
        logger.info("Completed %s%%", perComplete)
        current+=1
    logger.info("Completed 100%%", )


path = os.path.join(".", "calibration", "xycoordinates.txt")
drawXYCoordinates(path, True)


myPlotter.finalize()
myPlotter.disableSteppers()
logger.info("Done")
