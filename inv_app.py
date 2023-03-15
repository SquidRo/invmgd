import falcon, pdb

class InventoryTable(object):
    def __init__(self, sql_cnx):
        self.sql_cnx = sql_cnx

    def on_get(self, req, resp):
        resp.text = '{"message": "Hello world!"}'
        resp.status = falcon.HTTP_200

    def on_get_dump(self, req, resp):
        cursor = self.sql_cnx.cursor()

        query = ("SHOW DATABASES")

        cursor.execute(query)

        data = cursor.fetchall()

       # pdb.set_trace()

        resp.text = "message : {}".format(data)
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        obj = req.get_media()
        msg = obj.get('message')

        resp.status = falcon.HTTP_200
        resp.media = {'message' : msg}


class MyService(falcon.App):
    def __init__(self, sql_cnx, *args, **kwargs):
        super(MyService, self).__init__(*args, **kwargs)

        self.sql_cnx = sql_cnx

        # Create resources
        inv_tbl = InventoryTable(sql_cnx)

        # Build routes
        self.add_route('/inventory',      inv_tbl)
        self.add_route('/inventory/dump', inv_tbl, suffix='dump')

    def start(self):
        """ A hook to when a Gunicorn worker calls run()."""
        pass

    def stop(self, signal):
        """ A hook to when a Gunicorn worker starts shutting down. """
        pass
