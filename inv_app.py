import falcon

class InventoryManage(object):
    def on_get(self, req, resp):
        resp.text = '{"message": "Hello world!"}'
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        obj = req.get_media()
        msg = obj.get('message')

        resp.status = falcon.HTTP_200
        resp.media = {'message' : msg}

class MyService(falcon.App):
    def __init__(self, *args, **kwargs):
        super(MyService, self).__init__(*args, **kwargs)

        # Create resources
        inv_mg = InventoryManage()
        
        # Build routes
        self.add_route('/hello', inv_mg)

    def start(self):
        """ A hook to when a Gunicorn worker calls run()."""
        pass

    def stop(self, signal):
        """ A hook to when a Gunicorn worker starts shutting down. """
        pass
