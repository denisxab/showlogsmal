import time

import logsmal
from logsmal import logger

logger.text = logsmal.loglevel("Test", fileout='/home/denis/prog/data_test/test.log')
logger.text1 = logsmal.loglevel("Test", fileout='/home/denis/prog/data_test/test1.log')
logger.text2 = logsmal.loglevel("Test", fileout='/home/denis/prog/data_test/test2.log')
logger.text3 = logsmal.loglevel("Test", fileout='/home/denis/prog/data_test/test3.log')

if __name__ == '__main__':

    for x in range(1_000):
        time.sleep(0.3)
        logger.text1(f'1 - {x}')
        time.sleep(0.3)
        logger.text(f'0 - {x}')
        logger.text2(f'2 - {x}')
        time.sleep(0.3)
        logger.text3(f'3 - {x}')
