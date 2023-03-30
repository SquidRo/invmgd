#
# util_rack.py
#
# Utility APIs for rack operations
#

import logging, threading, time, pdb

from multiprocessing import Queue, Array
from util import util_utl, util_sql

RACK_QUEUE  = None
RACK_THREAD = None
RACK_VAR    = None     # shared variable for rack-bot's status

MOVE_DELAY_TIME = 10   # simulating time consumed for moving inventory
RACK_BOT_READY  = 0
RACK_BOT_BUSY   = 1

# return 0 - OK
#        1 - FAIL
def add_job(job_data):
    ret = 1

    logging.info('Add {} to job queue.'.format(job_data))
    if RACK_QUEUE:
        try:
            RACK_QUEUE.put(job_data)
        except:
            logging.error('Fail to add job_data to queue !!!')
        else:
            ret = 0

    return ret

def rack_worker_thd():
    logging.info('Starting a background thread to manage rack-bot')

    while True:
#        try:
            job_data = RACK_QUEUE.get()

            logging.info('make rack-bot move the inventory start...')
            RACK_VAR[0] = RACK_BOT_BUSY

            time.sleep(MOVE_DELAY_TIME)

            logging.info('make rack-bot move the inventory done...')

            util_sql.upd_rec(job_data)
            RACK_VAR[0] = RACK_BOT_READY
#       except:
#            pass

# check if rack-bot available for moveing job
def is_rack_bot_ready():
    return (RACK_VAR[0] == RACK_BOT_READY)

def setup_rack_worker():
    global RACK_QUEUE
    global RACK_THREAD
    global RACK_VAR

    RACK_QUEUE = Queue()
    RACK_VAR   = Array('i', 1)
    RACK_VAR[0]= RACK_BOT_READY

    # For the background thread
    t = threading.Thread(target=rack_worker_thd)
    t.daemon = True
    t.start()
    RACK_THREAD = t

