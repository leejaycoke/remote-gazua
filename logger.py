import os
import logging
import logging.handlers

if not os.path.exists('./log'):
    os.mkdirs('./log')


log = logging.getLogger('gz-logger')
fomatter = logging.Formatter(
    '[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')

fileHandler = logging.FileHandler('./log/gz.log')
fileHandler.setFormatter(fomatter)
