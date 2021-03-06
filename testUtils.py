import os
import logging
from plotter.plotter import Plotter, PenDirection, CordDirection
from plotter.config import Config
from datetime import datetime

logger =None
myPlotter =None

def getLogger():
    global logger 
    if logger is None:        
        logger= logging.getLogger("plotterLog")
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(
            "plotterLog{date}.log".format(date=datetime.now().strftime('%Y%m%d')))
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        steam_handler = logging.StreamHandler()
        steam_handler.setLevel(logging.INFO)
        steam_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(steam_handler)
    return logger

def getPlotter():
    global myPlotter
    if myPlotter is None :     
        config = Config().getConfig()   
        myPlotter = Plotter(config,100, 70)
        myPlotter.init(False)
    return myPlotter

def drawRectangle():
    global logger
    logger = getLogger()
    logger.info("Drawing Rectangle")

    # Max dimensions xmin 100, x max250 ymin= 150, ymax 500

    # draw a line
    global myPlotter
    myPlotter = getPlotter()
    logger.info("Moving to initial pos")
    myPlotter.moveTo(50, 150, PenDirection.Up)  # go to initial postion
    
    input("Press Enter to continue...")
    logger.info("Drawing left vertical line")
    myPlotter.moveTo(50, 450, PenDirection.Down)  # |
    
    input("Press Enter to continue...")
    logger.info("Drawing bottom horizontal line")
    myPlotter.moveTo(300, 450, PenDirection.Down)  # |__
    
    input("Press Enter to continue...")
    logger.info("Drawing right vertical line")
    myPlotter.moveTo(300, 150, PenDirection.Down)  # |__|
    
    input("Press Enter to continue...")
    logger.info("Drawing top horizontal line")                                                   
                                                    # __
    myPlotter.moveTo(50, 150, PenDirection.Down)  # |__|
    # once done move back to the original position
    
    input("Press Enter to continue...")
    logger.info("Moving to initial post")                                                   
    myPlotter.finalize()
    logger.info("Done")

def drawTriangle():
    global logger
    logger = getLogger()
    logger.info("Drawing Triangle")
    global myPlotter
    myPlotter = getPlotter()
    logger.info("Moving to initial pos")
    myPlotter.moveTo(100, 150, PenDirection.Up)  # go to initial postion
    
    #input("Press Enter to continue...")
    logger.info("Drawing left side")
    myPlotter.moveTo(50, 250, PenDirection.Down)  # /
    
    #input("Press Enter to continue...")
    logger.info("Drawing bottom line")
    myPlotter.moveTo(150, 250, PenDirection.Down)  # /__
    
    #input("Press Enter to continue...")
    logger.info("Drawing right side")
    myPlotter.moveTo(100, 150, PenDirection.Down)  # /__\
    
    logger.info("Moving to initial post")                                                   
    myPlotter.finalize()

def leftLiftUp(steps):
    global logger
    global myPlotter
    logger = getLogger()
    logger.debug("leftLiftUp {}".format(steps))
    myPlotter = getPlotter()
    myPlotter.moveLeft(CordDirection.Backward,steps)

def leftLiftDown(steps):
    global logger
    global myPlotter
    logger = getLogger()
    logger.debug("leftLiftDown {}".format(steps))
    myPlotter = getPlotter()
    myPlotter.moveLeft(CordDirection.Forward,steps)

def rightLiftUp(steps):
    global logger
    global myPlotter
    logger = getLogger()
    logger.debug("rightLiftUp {}".format(steps))
    myPlotter = getPlotter()
    myPlotter.moveRight(CordDirection.Backward,steps)
    
def rightLiftDown(steps):
    global logger
    global myPlotter 
    logger= getLogger()
    logger.debug("rightLiftDown {}".format(steps))
    myPlotter = getPlotter()
    myPlotter.moveRight(CordDirection.Forward,steps)

def calibration(path):
    fs = open(path,"r")
    cords = fs.readlines()
    parsedCords=  [ cord.strip().split() for cord in cords]
    
    global logger 
    logger = getLogger()
    logger.info("Drawing calibration")
    
    global myPlotter
    myPlotter = getPlotter()
    logger.info("Moving to initial pos")
    myPlotter.moveTo(30, 60, PenDirection.Up) 
    
    for pc in parsedCords:
        x = int(pc[0])
        y = int(pc[1])
        pen = PenDirection.Down if pc[2]=="0" else PenDirection.Up
        myPlotter.moveTo(x, y, pen)

    myPlotter.finalize()
    
        

path = os.path.join(".","calibration","xycordinates.txt")
calibration(path)
#drawTriangle()
#drawRectangle();