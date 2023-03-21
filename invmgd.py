import time, logging, argparse, sys, os, socket, signal, queue, pdb

from gunicorn.app.base import BaseApplication

from inv_app import MyService
from util import util_utl, util_sql, util_rack

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

    # setup a worker thread for the rack-bot
    util_rack.setup_rack_worker()

    # setup sql cnx
    util_sql.setup_sql_cnx()

    # setup rest api server
    options = {
        'workers': 1,
        'bind': '{}:{}'.format(util_utl.CFG_TBL["BIND_HOST"],
                               util_utl.CFG_TBL["BIND_PORT"])
    }

    api_app = MyService()
    gunicorn_app = GunicornApp(api_app, options)

    gunicorn_app.cfg.set('timeout', 0) # let worker never timeout for happy debugging
    gunicorn_app.cfg.set('loglevel', 'debug')
    gunicorn_app.cfg.set('capture_output', 'True')
    gunicorn_app.cfg.set('accesslog', ['-', util_utl.get_logfile_path(daemon_flag)][not args.debug])
    gunicorn_app.cfg.set('errorlog',  ['-', util_utl.get_logfile_path(daemon_flag)][not args.debug])
    gunicorn_app.run()


if __name__ == '__main__':
    main(daemon_flag = False)
