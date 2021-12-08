import logging
import logging.config
from pyeslogging.handlers import PYESHandler
import json

# Define logging.json path
with open("C:\App\logging.json") as read_file:
    loggingConfigDir = json.load(read_file)
logging.config.dictConfig(loggingConfigDir)
logger = logging.getLogger('root')
logger.info("Hello World !")