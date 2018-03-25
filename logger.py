import os
import logging
import logging.handlers

LOGGER_NAME = "gz-logger"
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s] %(message)s"
LOG_FILE_PATH = os.getcwd() + '/log'


def get_log_path():
    if not os.path.isdir(LOG_FILE_PATH):
        os.path.makedirs(LOG_FILE_PATH)
    return LOG_FILE_PATH + '/gz.log'


def get_log_level():
    return logging.DEBUG if os.environ.get('GZ_ENV', 'LOCAL') == 'LOCAL' \
        else logging.INFO


def create_logger():
    log = logging.getLogger(LOGGER_NAME)
    fomatter = logging.Formatter(LOG_FORMAT)

    file_handler = logging.FileHandler(get_log_path())
    file_handler.setFormatter(fomatter)

    log.addHandler(file_handler)
    log.setLevel(get_log_level())

    return log


log = create_logger()
