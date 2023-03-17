import falcon, pdb, json, logging
from util import util_utl, util_sql


def build_ret_dict (ret_code, ret_desc):
    tmp_ret = {'result': {} }

    tmp_ret ['result']['code'] = ret_code
    if ret_desc:
        tmp_ret ['result']['desc'] = ret_desc

    return tmp_ret

class StorageTbl(object):
    def __init__(self, sql_cnx):
        self.sql_cnx = sql_cnx

    def on_post_feed(self, req, resp):
        obj = req.get_media()
        data = obj.get('data')

        # 1. query storage for free location
        # 2. update location with INV_ID and count
        # 3. insert a record into FEEDING_RECORD if update location ok
        free_locs = util_sql.get_free_locs(self.sql_cnx)

        idx = 0
        for feed_one in data:
            if idx < len(free_locs):
                loc_id = free_locs[idx]
                if util_sql.put_inv_to_loc(self.sql_cnx, loc_id, feed_one) > 0:
                    ret_dict = build_ret_dict(200, "Fail to execute sql operations")
                else:
                    ret_dict = build_ret_dict(100, None)
            else:
                err_msg = "No space for a new inventory !"
                logging.error(err_msg)
                ret_dict = build_ret_dict(200, err_msg)

        resp.status = falcon.HTTP_200
        resp.text   = json.dumps(ret_dict)

    def on_post_pick(self, req, resp):
        pass


class InventoryTbl(object):
    def __init__(self, sql_cnx):
        self.sql_cnx = sql_cnx

    def on_get(self, req, resp):
        resp.text = json.dumps({"data" : util_sql.INVENTORY_ID_MAP})
        resp.status = falcon.HTTP_200


class MyService(falcon.App):
    def __init__(self, sql_cnx, *args, **kwargs):
        super(MyService, self).__init__(*args, **kwargs)

        self.sql_cnx = sql_cnx

        # Create resources
        inv_tbl = InventoryTbl(sql_cnx)
        sto_tbl = StorageTbl(sql_cnx)

        # Build routes
        self.add_route('/inventory', inv_tbl)

        self.add_route('/feed', sto_tbl, suffix='feed')
        self.add_route('/pick', sto_tbl, suffix='pick')

    def start(self):
        """ A hook to when a Gunicorn worker calls run()."""
        pass

    def stop(self, signal):
        """ A hook to when a Gunicorn worker starts shutting down. """
        pass
