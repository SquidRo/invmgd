import time, logging, argparse, sys, os, socket, signal, pdb

from gunicorn.app.base import BaseApplication

from inv_app import MyService
from util import util_utl

import mysql.connector

class GunicornApp(BaseApplication):
    """ Custom Gunicorn application

    This allows for us to load gunicorn settings from an external source
    """
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(GunicornApp, self).__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

def main(daemon_flag = True):

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", help="emit debug messages")
    args = parser.parse_args()

    util_utl.utl_setup_log(daemon_flag, args.debug)
    util_utl.utl_setup_cfg(daemon_flag)

    if util_utl.CFG_TBL["BIND_PORT"] in [None, ""]:
        logging.critical("No binding port in {}, exit !!!".format(
                            util_utl.CFG_TBL["CFG_PATH"]))
        sys.exit(1)

    options = {
    	'workers': 1,
        'bind': '{}:{}'.format(util_utl.CFG_TBL["BIND_HOST"],
			       util_utl.CFG_TBL["BIND_PORT"])
    }

    # SQL TEST START
    try:
        cnx = mysql.connector.connect(
                user     = util_utl.CFG_TBL["SQL_USER"],
                password = util_utl.CFG_TBL["SQL_PASS"],
                host     = util_utl.CFG_TBL["SQL_HOST"],
                port     = util_utl.CFG_TBL["SQL_PORT"],
                database = util_utl.CFG_TBL["SQL_DB"])

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

        logging.info("Connecting to sql server ... FAILED")
        sys.exit(1)

    else:
        logging.info("Connecting to sql server ... DONE")
        #cnx.close()

    #
    #
    api_app = MyService(cnx)
    gunicorn_app = GunicornApp(api_app, options)

    gunicorn_app.cfg.set('loglevel', 'debug')
    gunicorn_app.cfg.set('capture_output', 'True')
    gunicorn_app.cfg.set('accesslog', ['-', util_utl.get_logfile_path(daemon_flag)][not args.debug])
    gunicorn_app.cfg.set('errorlog',  ['-', util_utl.get_logfile_path(daemon_flag)][not args.debug])
    gunicorn_app.run()


if __name__ == '__main__':
    main(daemon_flag = False)
