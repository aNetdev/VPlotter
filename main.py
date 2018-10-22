import logging
from plotter import Plotter, PenDirection


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

# Max dimensions xmin 100, x max250 ymin= 150, ymax 500 

# draw a line
myPlotter = Plotter(100, 80)
myPlotter.init(False)
myPlotter.moveTo(100, 150, PenDirection.Up) # go to initial postion
input("Press Enter to continue...")
myPlotter.moveTo(100, 500, PenDirection.Down) #|
input("Press Enter to continue...")
myPlotter.moveTo(250, 500, PenDirection.Down) #|__
input("Press Enter to continue...")
myPlotter.moveTo(250, 150, PenDirection.Down) #|__|
input("Press Enter to continue...")
                                  # __
myPlotter.moveTo(100, 150, PenDirection.Down) #|__|
# once done move back to the original position
input("Press Enter to continue...")
myPlotter.finalize()
logger.info("Done")