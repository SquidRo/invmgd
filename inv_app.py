import falcon, pdb, json, logging
from falcon.media.validators.jsonschema import validate
from util import util_utl, util_sql, util_rack, util_schema


SQL_ER_MSG     = "Fail to execute sql operations !"
DATA_EMPTY_MSG = "Data is empty !"
STO_FULL_MSG   = "No space for the new inventory !"
OUT_OF_STO_MSG = "Inventory ({}) out of stock !!!"

def build_ret_dict(ret_code, ret_desc = None):
    tmp_ret = {}

    tmp_ret['code'] = ret_code
    if ret_desc:
        tmp_ret['desc'] = ret_desc

    return tmp_ret

def append_res_dict_desc(res_dict, ret_code, ret_desc = None):
    res_dict["result"].append(build_ret_dict(ret_code, ret_desc))

def append_res_dict_dict(res_dict, ret_code, ret_dict):
    tmp_ret = build_ret_dict(ret_code)

    for item in ret_dict:
        tmp_ret[item] = ret_dict[item]

    res_dict["result"].append(tmp_ret)

class StorageTbl(object):
    def __init__(self):
        pass

    def chk_rack_bot(self, res_dict):
        is_bot_ok = util_rack.is_rack_bot_ready()

        if not is_bot_ok:
            err_msg = "RACK-BOT is not ready..."
            logging.error(err_msg)
            append_res_dict_desc(res_dict, 200, err_msg)

        return is_bot_ok

    @validate(util_schema.JSON_SCHEMA_FEED)
    def on_post_feed(self, req, resp):
        res_dict = { "result": [] }

        # 1. query storage for free location
        obj = req.get_media()
        data = obj.get('data')

        free_locs = util_sql.get_free_locs()

        idx = 0
        for one_feed in data:
            if idx < len(free_locs):
                loc_id = free_locs[idx]
                # 2. update location with INV_ID and count
                job_data = util_sql.put_inv_to_loc(loc_id, one_feed)

                if job_data == None:
                    append_res_dict_desc(res_dict, 200, SQL_ER_MSG)
                else:
                    # 3. insert a feed_rec
                    rec_id = util_sql.add_feed_rec(job_data)

                    # 4. add a job to rack
                    if rec_id != None:
                        job_data['FEED_REC'] = rec_id
                        util_rack.add_job(job_data)
                        append_res_dict_desc(res_dict, 100)
                        idx = idx + 1
                    else:
                        append_res_dict_desc(res_dict, 200, SQL_ER_MSG)
            else:
                logging.error(STO_FULL_MSG)
                append_res_dict_desc(res_dict, 200, STO_FULL_MSG)

        if len(res_dict["result"]) == 0:
            logging.error(DATA_EMPTY_MSG)
            append_res_dict_desc(res_dict, 200, DATA_EMPTY_MSG)

        resp.status = falcon.HTTP_200
        resp.text   = json.dumps(res_dict)

    @validate(util_schema.JSON_SCHEMA_PICK)
    def on_post_pick(self, req, resp):
        res_dict = { "result": [] }

        obj = req.get_media()
        data = obj.get('data')

        # ex: one_pick = {'item': 'K2V4PCB', 'reason': 'AGV'}
        for one_pick in data:
            # 1. query storage for needed inventory
            loc_list = util_sql.get_inv_locs(one_pick['item'])

            if len(loc_list) == 0:
                err_msg = OUT_OF_STO_MSG.format(one_pick['item'])
                logging.error(err_msg)
                append_res_dict_desc(res_dict, 200, err_msg)

            # ex: loc_list = [(1,), (2,), (3,), (4,), (5,)]
            for one_loc in loc_list:
                # 2. update location with INV_ID and count
                job_data = util_sql.rem_inv_from_loc(one_loc)

                if job_data == None:
                    append_res_dict_desc(res_dict, 200, SQL_ER_MSG)
                else:
                    # 3. insert a pick_rec
                    job_data['REASON'] = one_pick['reason']
                    rec_id = util_sql.add_pick_rec(job_data)

                    # 4. add a job to rack
                    if rec_id != None:
                        job_data['PICK_REC'] = rec_id
                        util_rack.add_job(job_data)

                        tmp_dict = {}
                        tmp_dict['pkreq_id'] = rec_id
                        tmp_dict['stack_id'] = job_data['STACK_ID']

                        append_res_dict_dict(res_dict, 100, tmp_dict)
                    else:
                        append_res_dict_desc(res_dict, 200, SQL_ER_MSG)
                break

        if len(res_dict["result"]) == 0:
            logging.error(DATA_EMPTY_MSG)
            append_res_dict_desc(res_dict, 200, DATA_EMPTY_MSG)

        resp.status = falcon.HTTP_200
        resp.text   = json.dumps(res_dict)

    @validate(util_schema.JSON_SCHEMA_UPD_PICK_REQ)
    def on_post_pickreq(self, req, resp):
        obj = req.get_media()
        data = obj.get('data')

        pkreq_id = None
        conv_id  = None

        if 'pkreq_id' in data:
            pkreq_id = data['pkreq_id']

        if 'conv_id' in data:
            conv_id = data['conv_id']

        res_dict = {}
        if None in [ pkreq_id, conv_id ]:
            res_dict["result"] = build_ret_dict(200, "pkreq_id or conv_id not found !!!")
        else:
            ret_val = util_sql.upd_pkreq_conv_id(pkreq_id, conv_id)
            if ret_val != 0:
                res_dict["result"] = build_ret_dict(200, SQL_ER_MSG)
            else:
                res_dict["result"] = build_ret_dict(100)

        resp.status = falcon.HTTP_200
        resp.text   = json.dumps(res_dict)


class InventoryTbl(object):
    def __init__(self):
        pass

    def on_get(self, req, resp):
        resp.text = json.dumps({"data" : util_sql.INVENTORY_ID_MAP})
        resp.status = falcon.HTTP_200


def handle_uncaught_exception(req, resp, ex, params):
    logging.exception('Unhandled error - {}'.format(req))
    raise falcon.HTTPInternalServerError(title='App error')

def handle_http_error(req, resp, ex, params):
    logging.exception('HTTP error - {}'.format(req))
    raise ex

class MyService(falcon.App):
    def __init__(self, *args, **kwargs):
        super(MyService, self).__init__(*args, **kwargs)

        # install error handler
        self.add_error_handler(falcon.HTTPError, handle_http_error)
        self.add_error_handler(Exception, handle_uncaught_exception)

        # Create resources
        inv_tbl = InventoryTbl()
        sto_tbl = StorageTbl()

        # Build routes
        self.add_route('/inventory', inv_tbl)

        self.add_route('/feed', sto_tbl, suffix='feed')
        self.add_route('/pick', sto_tbl, suffix='pick')
        self.add_route('/upd_pick_req', sto_tbl, suffix='pickreq')

    def start(self):
        """ A hook to when a Gunicorn worker calls run()."""
        pass

    def stop(self, signal):
        """ A hook to when a Gunicorn worker starts shutting down. """
        pass
