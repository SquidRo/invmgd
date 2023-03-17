#
# util_sql.py
#
# Utility APIs for sql db operations
#

import logging
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
    "  PRIMARY KEY (`FR_ID`)"
    ") ENGINE=InnoDB".format(TBL_NAME_FEED_REC) )

SQL_TABLES[TBL_NAME_PICK_REC] = (
    "CREATE TABLE `{}` ("
    "  `PR_ID` int NOT NULL AUTO_INCREMENT,"
    "  `LOC_ID` int NOT NULL,"
    "  `INV_ID` int NOT NULL,"
    "  `DISC_QUAN` int NOT NULL,"
    "  `CONV_ID` int NOT NULL,"
    "  `REASON` varchar(50),"
    "  `DATE` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
    "  PRIMARY KEY (`PR_ID`)"
    ") ENGINE=InnoDB".format(TBL_NAME_PICK_REC) )


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

# 1. create db if db doest not exist
# 2. create table if table does not exist
def create_sql_tbls(sql_cnx, db_name):
    do_dflt_data = True
    sql_cursor = sql_cnx.cursor()
    try:
        sql_cursor.execute("USE {}".format(db_name))
    except mysql.connector.Error as err:
        logging.error("Database {} does not exists.".format(db_name))
        if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            create_sql_db(sql_cursor, db_name)
            logging.info("Database {} created successfully.".format(db_name))
            sql_cnx.database = db_name
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
       create_dflt_data(sql_cnx)

# return cnx if connect to sql server ok
# also create default tables and inventroy id mapping
# for later operations
def setup_sql_cnx():
    try:
        cnx = mysql.connector.connect(
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

    create_sql_tbls(cnx, util_utl.CFG_TBL["SQL_DB"])

    build_inventory_id_map(cnx)

    return cnx


# create default data for sw develepment
def create_dflt_data(sql_cnx):
    add_inv = ("INSERT INTO {} "
               "(INV_NAME, WEIGHT) "
               "VALUES (%s, %s)".format(TBL_NAME_INVENTORY))

    sql_cursor = sql_cnx.cursor()

    for data in DFLT_INV_DATA:
        # Insert defalt inventory
        sql_cursor.execute(add_inv, data)

    # Make sure data is committed to the database
    sql_cnx.commit()

    add_sto = ("INSERT INTO {} "
               "VALUES ()".format(TBL_NAME_STORAGE))

    for data in DFLT_STO_DATA:
        sql_cursor.execute(add_sto, data)

    sql_cnx.commit()
    sql_cursor.close()


def build_inventory_id_map(sql_cnx):
    sql_cursor = sql_cnx.cursor()

    query = ("SELECT * FROM {} ".format(TBL_NAME_INVENTORY))

    sql_cursor.execute(query)
    result = sql_cursor.fetchall()

    for one_inv in result:
        INVENTORY_ID_MAP[one_inv[1]] = {'id' : one_inv[0]}

    sql_cursor.close()


def get_free_locs(sql_cnx):
    sql_cursor = sql_cnx.cursor()

    query = ("SELECT LOC_ID FROM {} "
             "WHERE INV_ID IS NULL".format(TBL_NAME_STORAGE))

    sql_cursor.execute(query)
    result = sql_cursor.fetchall()

    sql_cursor.close()

    return result


def put_inv_to_loc(sql_cnx, loc_id, data):
    sql_cursor = sql_cnx.cursor()

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
        return 1

    sql_stmt = ("UPDATE {} SET INV_ID={}, QUANTITY={} "
                "WHERE LOC_ID={}".format(TBL_NAME_STORAGE, inv_id, count, loc_id[0]))

    try:
        sql_cursor.execute(sql_stmt)
        sql_cnx.commit()
    except mysql.connector.Error as err:
        logging.error("update {} : {}".format(TBL_NAME_STORAGE, err))

    sql_cursor.close()

    return 0
