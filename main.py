import logging
import os
from datetime import datetime
from server import WebServer

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

logger = getLogger()
logger.info("Starting")

s = WebServer(host='0.0.0.0', port=8080)
s.run_app()
logger.info("Done")