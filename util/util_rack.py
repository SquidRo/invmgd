#
# util_rack.py
#
# Utility APIs for rack operations
#

import logging, threading, time, pdb

from multiprocessing import Queue
from util import util_utl, util_sql

JOB_QUEUE  = None
JOB_THREAD = None

MOVE_DELAY_TIME = 10   # simulating time consumed for moving inventory

# return 0 - OK
#        1 - FAIL
def add_job(job_data):
    ret = 1

    logging.info('Add {} to job queue.'.format(job_data))
    if JOB_QUEUE:
        try:
            JOB_QUEUE.put(job_data)
        except:
            logging.error('Fail to add job_data to queue !!!')
        else:
            ret = 0

    return ret

def rack_worker_thd():
    logging.info('Starting a background thread to manage rack-bot')

    while True:
#        try:
            job_data = JOB_QUEUE.get()

            logging.info('make rack-bot move the inventory start...')

            time.sleep(MOVE_DELAY_TIME)

            logging.info('make rack-bot move the inventory done...')

            util_sql.upd_rec(job_data)

#       except:
#            pass

def setup_rack_worker():
    global JOB_QUEUE
    global JOB_THREAD

    JOB_QUEUE = Queue()

    # For the background thread
    t = threading.Thread(target=rack_worker_thd)
    t.daemon = True
    t.start()
    JOB_THREAD = t

