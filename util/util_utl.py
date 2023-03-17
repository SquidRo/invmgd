#
# util_utl.py
#
# Utility APIs.
#

import subprocess, json, logging, logging.handlers, inspect
import sys, os, time, functools, configparser

TAG_DBG_PERF                    = 'DBG_PERF'

DBG_FLG_TBL = {
    TAG_DBG_PERF : 1,
}

# for config.ini and log
APP_NAME                        = 'invmgd'
LOG_FILE                        = APP_NAME + '.log'
LOG_DIR                         = '/var/log/'
LOG_FMT                         = '%(asctime)s %(levelname)-8s %(message)s'
LOG_FMT_DATE                    = '%y-%m-%d %H:%M:%S'

CFG_DIR                         = '/etc/' + APP_NAME + '/'
CFG_FILE                        = 'config.ini'

CFG_SECT_GEN                    = "general"

CFG_TBL = {
    "FAKE_DATA"      : 0,
    "SQL_HOST"       : None,
    "SQL_PORT"       : None,
    "SQL_USER"       : None,
    "SQL_PASS"       : None,
    "SQL_DB"         : None,
    "BIND_HOST"      : None,
    "BIND_PORT"      : None,
    "CFG_PATH"       : None,
}

CFG_READY_CB_TBL = []

def utl_is_flag_on(flg_name):
    return flg_name in DBG_FLG_TBL and DBG_FLG_TBL[flg_name] > 0

def utl_set_flag(flg_name, val):
    DBG_FLG_TBL[flg_name] = val

def utl_log(str, lvl = logging.DEBUG, c_lvl=1):
    f1 = sys._getframe(c_lvl)

    if f1:
        my_logger = logging.getLogger()
        if lvl < my_logger.getEffectiveLevel(): return
        rec = my_logger.makeRecord(
            APP_NAME,
            lvl,
            os.path.basename(f1.f_code.co_filename),
            f1.f_lineno,
            str,
            None,
            None,
            f1.f_code.co_name)

        my_logger.handle(rec)
    else:
        logging.log (lvl, str)

def utl_err(str):
    utl_log(str, logging.ERROR, 2)

# decorator to get function execution time
def utl_timeit(f):
    @functools.wraps(f)
    def timed(*args, **kw):
        if utl_is_flag_on(TAG_DBG_PERF):
            t_beg = time.time()
            result = f (*args, **kw)
            t_end = time.time()
            utl_log("Time spent %s : %s %s" %  ((t_end - t_beg), f.__name__, args), logging.CRITICAL, 2)
        else:
            result = f (*args, **kw)

        return result
    return timed

# decorator to add separation line in logs
def utl_log_outer(f):
    @functools.wraps(f)
    def wrapped(*args, **kw):
        if utl_is_flag_on(TAG_DBG_PERF):
            utl_log("beg ==================", logging.CRITICAL, 3)
            result = f (*args, **kw)
            utl_log("end ==================", logging.CRITICAL, 3)
        else:
            result = f (*args, **kw)

        return result
    return wrapped

@utl_timeit
def utl_execute_cmd(exe_cmd):
    p = subprocess.Popen(exe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    ## Wait for end of command. Get return code ##
    returncode = p.wait()

    if returncode != 0:
        # if no decorator, use inspect.stack()[1][3] to get caller
        utl_log("Failed to [%s] by %s !!! (%s)" % (exe_cmd, inspect.stack()[2][3], err), logging.ERROR)
        return False

    return True

@utl_timeit
def utl_get_execute_cmd_output(exe_cmd):
    p = subprocess.Popen(exe_cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    ## Wait for end of command. Get return code ##
    returncode = p.wait()

    if returncode != 0:
        # if no decorator, use inspect.stack()[1][3] to get caller
        utl_log("Failed to [%s] by %s !!!" % (exe_cmd, inspect.stack()[2][3]), logging.ERROR)
        return (False, None)

    return (True, output)

# register callback function for config ready event
def utl_register_cb_cfg_ready(cbf):
    if cbf not in CFG_READY_CB_TBL:
        CFG_READY_CB_TBL.append(cbf)

# notify config ready event
def utl_notify_cfg_ready():
    for cbf in CFG_READY_CB_TBL:
        cbf(CFG_TBL)

def utl_setup_cfg(daemon_flag):
    cfg_path = ['./misc/', CFG_DIR] [daemon_flag] + CFG_FILE
    CFG_TBL["CFG_PATH"] = cfg_path
    cfg = configparser.RawConfigParser()
    cfg.read(cfg_path)

    cmap_tbl = [ { "fld" : "FAKE_DATA",  "tag" : "fake_data",  "type" : "int" },
                 { "fld" : "SQL_HOST",   "tag" : "sql_host"                   },
                 { "fld" : "SQL_PORT",   "tag" : "sql_port",   "type" : "int" },
                 { "fld" : "SQL_USER",   "tag" : "sql_user"                   },
                 { "fld" : "SQL_PASS",   "tag" : "sql_pass"                   },
                 { "fld" : "SQL_DB",     "tag" : "sql_db"                     },
                 { "fld" : "BIND_HOST",  "tag" : "bind_host"                  },
                 { "fld" : "BIND_PORT",  "tag" : "bind_port",  "type" : "int" },
    ]

    for cmap in cmap_tbl:
        if cfg.has_option(CFG_SECT_GEN, cmap["tag"]):
            if "type" in cmap:
                CFG_TBL[cmap["fld"]] = int(cfg.get(CFG_SECT_GEN, cmap["tag"]))
            else:
                CFG_TBL[cmap["fld"]] = cfg.get(CFG_SECT_GEN, cmap["tag"])

    utl_notify_cfg_ready()

def get_logfile_path(daemon_flag):
    log_path = ['./', LOG_DIR] [daemon_flag] + LOG_FILE
    return log_path

def utl_setup_log(daemon_flag, debug_flag):
    log_path = get_logfile_path(daemon_flag)
    log_lvl  = [logging.INFO, logging.DEBUG] [debug_flag]

    if debug_flag:
        # clear log file
        with open(log_path, 'w'):
            pass

    logging.basicConfig(level=log_lvl,
                        format=LOG_FMT,
                        datefmt=LOG_FMT_DATE)

    handler = logging.handlers.RotatingFileHandler(
                    log_path, maxBytes=1024000, backupCount=2)
    handler.setFormatter(logging.Formatter(
                    fmt=LOG_FMT, datefmt=LOG_FMT_DATE))

    logging.getLogger().addHandler(handler)

    # log gunicorn's log message to our file
    #logging.getLogger("gunicorn.error").addHandler(handler)
    #logging.getLogger("gunicorn.access").addHandler(handler)
