import logging
from plotter import Plotter


def getLogger():
    logger = logging.getLogger("plotterLog")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler("plotterLog.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(logging.DEBUG)
    steam_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(steam_handler)
    return logger


logger = getLogger()
logger.info("Starting")


# draw a line
myPlotter = Plotter(50, 50)
myPlotter.init(True)
myPlotter.moveTo(100, 200, False) # go to initial postion
myPlotter.moveTo(100, 400, False) #|

myPlotter.moveTo(400, 400, False) #|__

myPlotter.moveTo(400, 200, False) #|__|

                                  # __
myPlotter.moveTo(200, 200, False) #|__|
myPlotter.finalize()
# once done move back to the original position
myPlotter.finalize()
logger.info("Done")
