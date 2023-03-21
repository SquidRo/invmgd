#
# util_sql.py
#
# Utility APIs for sql db operations
#

import logging, functools
import mysql.connector, pdb

from util import util_utl

DFLT_INV_DATA = [
    ("K2V4PCB",   9),
    ("TPM",       8),
    ("IRON",      7),
    ("CAGE",      6),
    ("HEAT_SINK", 5),
    ("AIR_BAFFLE",4),
    ("BRACKET",   3)
]

DFLT_STO_DATA = [
    (),
    (),
    (),
    (),
    (),
    (),
    ()
]

TBL_NAME_STORAGE   = 'STORAGE'
TBL_NAME_INVENTORY = 'INVENTORY'
TBL_NAME_FEED_REC  = 'FEEDING_REC'
TBL_NAME_PICK_REC  = 'PICKING_REC'

SQL_TABLES = {}

SQL_TABLES[TBL_NAME_INVENTORY] = (
    "CREATE TABLE `{}` ("
    "  `INV_ID` int NOT NULL AUTO_INCREMENT,"
    "  `INV_NAME` varchar(50) NOT NULL,"
    "  `WEIGHT` int NOT NULL,"
    "  PRIMARY KEY (`INV_ID`)"
    ") ENGINE=InnoDB".format(TBL_NAME_INVENTORY) )

SQL_TABLES[TBL_NAME_STORAGE] = (
    "CREATE TABLE `{}` ("
    "  `LOC_ID` int NOT NULL AUTO_INCREMENT,"
    "  `INV_ID` int,"
    "  `QUANTITY` int,"
    "  `READY` int DEFAULT NULL, "
    "  PRIMARY KEY (`LOC_ID`)"
    ") ENGINE=InnoDB".format(TBL_NAME_STORAGE) )

SQL_TABLES[TBL_NAME_FEED_REC] = (
    "CREATE TABLE `{}` ("
    "  `FR_ID` int NOT NULL AUTO_INCREMENT,"
    "  `LOC_ID` int NOT NULL,"
    "  `INV_ID` int NOT NULL,"
    "  `EMP_ID` varchar(20) NOT NULL,"
    "  `FEED_QUAN` int NOT NULL,"
    "  `DATE` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
    "  `RACK_BOT` int DEFAULT NULL,"
    "  PRIMARY KEY (`FR_ID`)"
    ") ENGINE=InnoDB".format(TBL_NAME_FEED_REC) )

SQL_TABLES[TBL_NAME_PICK_REC] = (
    "CREATE TABLE `{}` ("
    "  `PR_ID` int NOT NULL AUTO_INCREMENT,"
    "  `LOC_ID` int NOT NULL,"
    "  `INV_ID` int NOT NULL,"
    "  `DISC_QUAN` int NOT NULL,"
    "  `CONV_ID` int,"
    "  `REASON` varchar(50),"
    "  `DATE` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
    "  `RACK_BOT` int DEFAULT NULL,"
    "  PRIMARY KEY (`PR_ID`)"
    ") ENGINE=InnoDB".format(TBL_NAME_PICK_REC) )


SQL_CNX          = None
INVENTORY_ID_MAP = {}


def create_sql_db(sql_cursor, db_name):
    ret_val = True
    try:
        sql_cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(db_name))
    except mysql.connector.Error as err:
        logging.error("Failed creating database: {}".format(err))
        ret_val = False

    return ret_val

# 1. create db if db does not exist
# 2. create table if table does not exist
def create_sql_tbls(db_name):
    do_dflt_data = True
    sql_cursor = SQL_CNX.cursor()
    try:
        sql_cursor.execute("USE {}".format(db_name))
    except mysql.connector.Error as err:
        logging.error("Database {} does not exists.".format(db_name))
        if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            create_sql_db(sql_cursor, db_name)
            logging.info("Database {} created successfully.".format(db_name))
            SQL_CNX.database = db_name
        else:
            logging.error(err)

    for table_name in SQL_TABLES:
        table_desc = SQL_TABLES[table_name]
        log_data   =  'OK'

        try:
            log_msg = "Creating table {}: ".format(table_name)
            sql_cursor.execute(table_desc)
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_TABLE_EXISTS_ERROR:
                log_data = 'already exists'
            else:
                log_data = err.msg

            do_dflt_data = False

        logging.info(log_msg + log_data)

    sql_cursor.close()

    if do_dflt_data:
       create_dflt_data()

# decorator to add separation line in logs
def log_func_name(f):
    @functools.wraps(f)
    def wrapped(*args, **kw):
        logging.info("Enter {} with {}".format(f.__name__, *args))
        result = f (*args, **kw)
        return result
    return wrapped

# return cnx if connect to sql server ok
# also create default tables and inventroy id mapping
# for later operations
def setup_sql_cnx():
    global SQL_CNX

    try:
        SQL_CNX = mysql.connector.connect(
                user     = util_utl.CFG_TBL["SQL_USER"],
                password = util_utl.CFG_TBL["SQL_PASS"],
                host     = util_utl.CFG_TBL["SQL_HOST"],
                port     = util_utl.CFG_TBL["SQL_PORT"])

    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            logging.error("Something is wrong with your user name or password")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            logging.error("Database does not exist")
        else:
            logging.error(err)

        logging.info("Connecting to sql server ... FAILED")
        sys.exit(1)

    create_sql_tbls(util_utl.CFG_TBL["SQL_DB"])

    build_inventory_id_map()

# create default data for sw develepment
def create_dflt_data():
    add_inv = ("INSERT INTO {} "
               "(INV_NAME, WEIGHT) "
               "VALUES (%s, %s)".format(TBL_NAME_INVENTORY))

    sql_cursor = SQL_CNX.cursor()

    for data in DFLT_INV_DATA:
        # Insert defalt inventory
        sql_cursor.execute(add_inv, data)

    # Make sure data is committed to the database
    SQL_CNX.commit()

    add_sto = ("INSERT INTO {} "
               "VALUES ()".format(TBL_NAME_STORAGE))

    for data in DFLT_STO_DATA:
        sql_cursor.execute(add_sto, data)

    SQL_CNX.commit()
    sql_cursor.close()

def build_inventory_id_map():
    sql_cursor = SQL_CNX.cursor()

    query = ("SELECT * FROM {} ".format(TBL_NAME_INVENTORY))

    sql_cursor.execute(query)
    result = sql_cursor.fetchall()

    for one_inv in result:
        INVENTORY_ID_MAP[one_inv[1]] = {'id' : one_inv[0]}

    sql_cursor.close()

def get_free_locs():
    sql_cursor = SQL_CNX.cursor()

    sql_stmt = ("SELECT LOC_ID FROM {} "
                "WHERE INV_ID IS NULL".format(TBL_NAME_STORAGE))

    try:
        sql_cursor.execute(sql_stmt)
        result = sql_cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error("execute {} : {}".format(sql_stmt, err))

    sql_cursor.close()

    return result

# ex: loc_data = (0, 1, 10)
def rem_inv_from_loc(loc_data):
    job = None
    sql_cursor = SQL_CNX.cursor()

    sql_stmt = ("UPDATE {} SET READY=0 "
                "WHERE LOC_ID={}".format(TBL_NAME_STORAGE, loc_data[0]))
    try:
        sql_cursor.execute(sql_stmt)
        SQL_CNX.commit()

        job = {
            'INV_ID' : loc_data[1],
            'COUNT'  : loc_data[2],
            'LOC_ID' : loc_data[0],
        }

    except mysql.connector.Error as err:
        logging.error("execute {} : {}".format(sql_stmt, err))

    sql_cursor.close()

    return job

def get_inv_locs(inv_name):
    sql_cursor = SQL_CNX.cursor()
    ret_locs = []

    if inv_name in INVENTORY_ID_MAP:
        inv_id = INVENTORY_ID_MAP[inv_name]['id']
    else:
        inv_id = None

    if None in [inv_id]:
        logging.error("Incorrect inventory name !!!")
        return []

    sql_stmt = ("SELECT LOC_ID, INV_ID, QUANTITY FROM {} "
                "WHERE INV_ID={} and `READY`=1".format(TBL_NAME_STORAGE, inv_id))

    try:
        sql_cursor.execute(sql_stmt)
        result = sql_cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error("execute {} : {}".format(sql_stmt, err))

    sql_cursor.close()

    return result

# return None - FAIL
#        job  - OK
#        ex: {
#           "INV_ID":
#           "EMP_ID":
#           "COUNT" :
#           "LOC_ID":
#        }
def put_inv_to_loc(loc_id, data):
    job        = None
    sql_cursor = SQL_CNX.cursor()

    # ex:
    #   loc_id : (1,)
    #   data   : {'item': 'K2V4PCB', 'count': 10, 'emp_id': 'A1234567'}
    if data['item'] in INVENTORY_ID_MAP:
        inv_id = INVENTORY_ID_MAP[data['item']]['id']
    else:
        inv_id = None

    if 'count' in data:
        count = data['count']
    else:
        count = None

    if 'emp_id' in data:
        emp_id = data['emp_id']
    else:
        emp_id = 'UNKNOWN'

    if None in [inv_id, count]:
        logging.error("Incorrect inventory name or count !!!")
        return job

    sql_stmt = ("UPDATE {} SET INV_ID={}, QUANTITY={}, READY=0 "
                "WHERE LOC_ID={}".format(TBL_NAME_STORAGE, inv_id, count, loc_id[0]))

    try:
        sql_cursor.execute(sql_stmt)
        SQL_CNX.commit()

        job = {
            'INV_ID' : inv_id,
            'COUNT'  : count,
            'LOC_ID' : loc_id[0],
            'EMP_ID' : emp_id
        }

    except mysql.connector.Error as err:
        logging.error("execute {} : {}".format(sql_stmt, err))

    sql_cursor.close()

    return job

# return FEED_REC ID - OK
#        None        - FAIL
@log_func_name
def add_feed_rec(data):
    # ex: data : {'INV_ID': 1, 'COUNT': 10, 'LOC_ID': 3, 'EMP_ID': 'A1234567'
    sql_stmt = ("INSERT INTO {} "
                "(INV_ID, LOC_ID, EMP_ID, FEED_QUAN) "
                "VALUES ( %s, %s, %s, %s)".format(
                TBL_NAME_FEED_REC))

    sql_cursor = SQL_CNX.cursor()

    rec_id = None
    try:
        sql_cursor.execute(
            sql_stmt,
            (data['INV_ID'], data['LOC_ID'], data['EMP_ID'], data['COUNT'])
            )
        SQL_CNX.commit()

        rec_id = sql_cursor.lastrowid

    except mysql.connector.Error as err:
        logging.error("execute {} : {}".format(sql_stmt, err))

    sql_cursor.close()

    return rec_id

# return PICK_REC ID - OK
#        None        - FAIL
@log_func_name
def add_pick_rec(data):
    # ex: data : {'INV_ID': 1, 'COUNT': 10, 'LOC_ID': 3, 'EMP_ID': 'A1234567'
    sql_stmt = ("INSERT INTO {} "
                "(INV_ID, LOC_ID, REASON, DISC_QUAN) "
                "VALUES ( %s, %s, %s, %s)".format(
                TBL_NAME_PICK_REC))

    sql_cursor = SQL_CNX.cursor()

    rec_id = None
    try:
        sql_cursor.execute(
            sql_stmt,
            (data['INV_ID'], data['LOC_ID'], data['REASON'], data['COUNT'])
            )
        SQL_CNX.commit()

        rec_id = sql_cursor.lastrowid

    except mysql.connector.Error as err:
        logging.error("execute {} : {}".format(sql_stmt, err))

    sql_cursor.close()

    return rec_id

# return 0 - OK
#        1 - FAIL
@log_func_name
def upd_pkreq_conv_id(rec_id, conv_id):
    ret_val = 0
    sql_stmt = ("UPDATE {} "
                "SET CONV_ID={} "
                "WHERE PR_ID={}".format(
                TBL_NAME_PICK_REC, conv_id, rec_id))

    sql_cursor = SQL_CNX.cursor()

    try:
        sql_cursor.execute(sql_stmt)
        SQL_CNX.commit()
    except mysql.connector.Error as err:
        logging.error("execute {} : {}".format(sql_stmt, err))
        ret_val = 1

    sql_cursor.close()

    return ret_val

def upd_history_rec(tbl_name, rack_bot, id_name, rec_id):
    sql_stmt = ("UPDATE {} "
                "SET RACK_BOT={} "
                "WHERE {}={}".format(
                tbl_name, rack_bot, id_name, rec_id))

    sql_cursor = SQL_CNX.cursor()

    try:
        sql_cursor.execute(sql_stmt)
        SQL_CNX.commit()
    except mysql.connector.Error as err:
        logging.error("execute {} : {}".format(sql_stmt, err))

    sql_cursor.close()

def upd_sto_ready(rdy_val, loc_id):
    sql_stmt = ("UPDATE {} "
                "SET READY={} "
                "WHERE LOC_ID={}".format(
                TBL_NAME_STORAGE, rdy_val, loc_id))

    sql_cursor = SQL_CNX.cursor()

    try:
        sql_cursor.execute(sql_stmt)
        SQL_CNX.commit()
    except mysql.connector.Error as err:
        logging.error("execute {} : {}".format(sql_stmt, err))

    sql_cursor.close()

def clear_sto_loc(loc_id):
    sql_stmt = ("UPDATE {} "
                "SET INV_ID=NULL, QUANTITY=NULL, READY=NULL "
                "WHERE LOC_ID={}".format(
                TBL_NAME_STORAGE, loc_id))

    sql_cursor = SQL_CNX.cursor()

    try:
        sql_cursor.execute(sql_stmt)
        SQL_CNX.commit()
    except mysql.connector.Error as err:
        logging.error("execute {} : {}".format(sql_stmt, err))

    sql_cursor.close()

@log_func_name
def upd_rec(data, is_ok = True):
    # 1. update feed_rec/pick_rec
    rack_bot = [0, 1] [is_ok]

    if 'FEED_REC' in data:
        upd_history_rec(TBL_NAME_FEED_REC, rack_bot, 'FR_ID', data['FEED_REC'])
    else:
        upd_history_rec(TBL_NAME_PICK_REC, rack_bot, 'PR_ID', data['PICK_REC'])

    # 2. update data in storage
    if is_ok:
        if 'FEED_REC' in data:
            # set READY to 1
            upd_sto_ready(1, data['LOC_ID'])
        else:
            # clear row
            clear_sto_loc(data['LOC_ID'])
    else:
        if 'FEED_REC' in data:
            # clear row
            clear_sto_loc(data['LOC_ID'])
        else:
            # set READY to 1
            upd_sto_ready(1, data['LOC_ID'])

# check if rack-bot available for moveing job
def is_rack_bot_ready():
    sql_cursor = SQL_CNX.cursor()

    sql_stmt = ("SELECT LOC_ID FROM {} "
                "WHERE `READY`=0".format(TBL_NAME_STORAGE))

    try:
        sql_cursor.execute(sql_stmt)
        result = sql_cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error("execute {} : {}".format(sql_stmt, err))

    sql_cursor.close()

    return [True, False] [len(result) > 0]
