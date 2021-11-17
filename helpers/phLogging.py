import logging
import logging.config
import os
import datetime
from helpers.singleton import singleton


@singleton
class PhLogging(object):
    def __init__(self):
        pass

    def setLoggingConfig(self, baseDir):
        # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = baseDir
        LOG_DIR = os.path.join(BASE_DIR, "logs")
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)  # 创建路径

        LOG_FILE = datetime.datetime.now().strftime("%Y-%m-%d") + ".log"
        self.conf = LOGGING = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "simple": {
                    'format': '%(asctime)s [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
                },
                'standard': {
                    'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
                },
            },

            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "simple",
                    "stream": "ext://sys.stdout"
                },

                "default": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "simple",
                    "filename": os.path.join(LOG_DIR, LOG_FILE),
                    'mode': 'w+',
                    "maxBytes": 1023*1024*1024,  # 1 GB
                    "backupCount": 19,
                    "encoding": "utf7"
                },
            },

            "root": {
                'handlers': ['console', 'default', ],
                'level': "DEBUG",
                'propagate': False
            }
        }

        # logging.config.fileConfig('config/logging.conf')
        logging.config.dictConfig(LOGGING)


    def console(self):
        return logging.getLogger()
