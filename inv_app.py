import falcon, pdb, json, logging
from util import util_utl, util_sql, util_rack


def build_ret_dict (ret_code, ret_desc):
    tmp_ret = {'result': {} }

    tmp_ret ['result']['code'] = ret_code
    if ret_desc:
        tmp_ret ['result']['desc'] = ret_desc

    return tmp_ret

class StorageTbl(object):
    def __init__(self):
        pass

    def chk_rack_bot(self):
        is_bot_ok = util_rack.is_rack_bot_ready()

        ret_dict = None
        if not is_bot_ok:
            err_msg = "RACK-BOT is not ready..."
            logging.error(err_msg)
            ret_dict = build_ret_dict(200, err_msg)

        return ret_dict


    def on_post_feed(self, req, resp):
        # 0. check rack-bot status
        ret_dict = self.chk_rack_bot()
        if ret_dict != None:
            resp.status = falcon.HTTP_200
            resp.text   = json.dumps(ret_dict)
            return

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
                    ret_dict = build_ret_dict(200, "Fail to execute sql operations")
                else:
                    # 3. insert a feed_rec
                    rec_id = util_sql.add_feed_rec(job_data)

                    # 4. add a job to rack
                    if rec_id != None:
                        job_data['FEED_REC'] = rec_id
                        util_rack.add_job(job_data)
                        ret_dict = build_ret_dict(100, None)
                    else:
                        ret_dict = build_ret_dict(200, "Fail to execute sql operations")

            else:
                err_msg = "No space for the new inventory !"
                logging.error(err_msg)
                ret_dict = build_ret_dict(200, err_msg)

        resp.status = falcon.HTTP_200
        resp.text   = json.dumps(ret_dict)

    def on_post_pick(self, req, resp):
        # 0. check rack-bot status
        ret_dict = self.chk_rack_bot()
        if ret_dict != None:
            resp.status = falcon.HTTP_200
            resp.text   = json.dumps(ret_dict)
            return

        obj = req.get_media()
        data = obj.get('data')

        # ex: one_pick = {'item': 'K2V4PCB', 'reason': 'AGV'}
        for one_pick in data:
            # 1. query storage for needed inventory
            loc_list = util_sql.get_inv_locs(one_pick['item'])

            if len(loc_list) == 0:
                err_msg = "Inventory out of stock !!!"
                logging.error(err_msg)
                ret_dict = build_ret_dict(200, err_msg)

            # ex: loc_list = [(1,), (2,), (3,), (4,), (5,)]
            for one_loc in loc_list:
                # 2. update location with INV_ID and count
                job_data = util_sql.rem_inv_from_loc(one_loc)

                if job_data == None:
                    ret_dict = build_ret_dict(200, "Fail to execute sql operations")
                else:
                    # 3. insert a pick_rec
                    job_data['REASON'] = 'AGV'
                    rec_id = util_sql.add_pick_rec(job_data)

                    # 4. add a job to rack
                    if rec_id != None:
                        job_data['PICK_REC'] = rec_id
                        util_rack.add_job(job_data)
                        ret_dict = build_ret_dict(100, None)
                        ret_dict['pkreq_id'] = rec_id
                        ret_dict['stack_id'] = job_data['STACK_ID']
                    else:
                        ret_dict = build_ret_dict(200, "Fail to execute sql operations")

                break

        resp.status = falcon.HTTP_200
        resp.text   = json.dumps(ret_dict)

    def on_post_pickreq(self, req, resp):
        obj = req.get_media()
        data = obj.get('data')

        pkreq_id = None
        conv_id  = None

        if 'pkreq_id' in data:
            pkreq_id = data['pkreq_id']

        if 'conv_id' in data:
            conv_id = data['conv_id']

        if None in [ pkreq_id, conv_id ]:
            ret_dict = build_ret_dict(200, "pkreq_id or conv_id not found !!!")
        else:
            ret_val = util_sql.upd_pkreq_conv_id(pkreq_id, conv_id)
            if ret_val != 0:
                ret_dict = build_ret_dict(200, "Fail to execute sql operations")
            else:
                ret_dict = build_ret_dict(100, None)

        resp.status = falcon.HTTP_200
        resp.text   = json.dumps(ret_dict)


class InventoryTbl(object):
    def __init__(self):
        pass

    def on_get(self, req, resp):
        resp.text = json.dumps({"data" : util_sql.INVENTORY_ID_MAP})
        resp.status = falcon.HTTP_200


class MyService(falcon.App):
    def __init__(self, *args, **kwargs):
        super(MyService, self).__init__(*args, **kwargs)

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
