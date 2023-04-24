import falcon, pytest
from falcon import testing
from .. import inv_app
from unittest import mock

class invmgdRestTest(testing.TestCase):
    def setUp(self):
        super(invmgdRestTest, self).setUp()
        self.app = inv_app.MyService()

    def test_post_pick(self):
        """Test the response of pick."""

        test_json = { 
            "data": [ 
                { "item": "K2V4PCB","reason": "AGV" }, 
                { "item": "K2V4PCB","reason": "AGV" } 
            ] 
        }

        self.p1 = mock.patch('util.util_sql.get_inv_locs', return_value = [(1,)])
        self.p2 = mock.patch('util.util_sql.rem_inv_from_loc', return_value = { 
                      'INV_ID': 1, 'COUNT': 1, 'LOC_ID': 1, 'STACK_ID': 1 } )
        self.p3 = mock.patch('util.util_sql.add_pick_rec', return_value = 1)

        self.p1.start()
        self.p2.start()
        self.p3.start()
        response = self.simulate_post('/pick', json = test_json)
        self.p1.stop()
        self.p2.stop()
        self.p3.stop()
        self.assertEqual(response.status, falcon.HTTP_OK)
        self.assertEqual(response.json, {'result': [{'code': 100, 'pkreq_id': 1, 'stack_id': 1},
                                                    {'code': 100, 'pkreq_id': 1, 'stack_id': 1}]}
                        )

    def test_post_feed(self):
        """Test the response of feed."""

        test_json = {
            "data": [ 
                { "item": "K2V4PCB","count": 10,"emp_id": "A1234567","stack_id":1},
                { "item": "K2V4PCB","count": 20,"emp_id": "A1234567","stack_id":31} 
            ] 
        }

        self.p1 = mock.patch('util.util_sql.get_free_locs', return_value = [(1,),(2,)])
        self.p2 = mock.patch('util.util_sql.put_inv_to_loc', return_value = {
                      'INV_ID': 1, 'COUNT': 1, 'LOC_ID': 1, 'STACK_ID': 1 } )
        self.p3 = mock.patch('util.util_sql.add_feed_rec', return_value = 1)

        self.p1.start()
        self.p2.start()
        self.p3.start()
        response = self.simulate_post('/feed', json = test_json)
        self.p1.stop()
        self.p2.stop()
        self.p3.stop()

        self.assertEqual(response.status, falcon.HTTP_OK)
        self.assertEqual(response.json, {'result': [{'code': 100}, {'code': 100}]} 
                        )

    def test_post_updpickreq(self):
        """Test the response of upd_pick_req."""

        test_json = {
            "data": {
                "pkreq_id" : 1,
                "conv_id"  : 2 
            }
        }

        self.p1 = mock.patch('util.util_sql.upd_pkreq_conv_id', return_value = 0)
        self.p1.start()
        response = self.simulate_post('/upd_pick_req', json = test_json)
        self.p1.stop()
        self.assertEqual(response.status, falcon.HTTP_OK)
        self.assertEqual(response.json, {'result': {'code': 100} }
                        )

