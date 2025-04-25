import unittest, sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot//')
from unittest.mock import patch
from datetime import datetime
from datetime import timedelta
from User.TradeRequests import OKXTradeRequests

class TestOKXTradeRequests(unittest.TestCase):
    def setUp(self):
        self.instId = 'BTC-USDT'
        self.size = 1.0
        self.posSide = 'long'
        self.tpPrice = 50000.0
        self.slPrice = 45000.0
        self.okx_trade_requests = OKXTradeRequests(
            instId=self.instId,
            size=self.size,
            posSide=self.posSide,
            tpPrice=self.tpPrice,
            slPrice=self.slPrice
        )

    @patch('okx.Trade.TradeAPI.place_order')
    def test_construct_market_order(self, mock_place_order):
        side = 'buy'
        mock_place_order.return_value = {
            "code": "0",
            "data": [{"ordId": "test_order_id"}],
            "outTime": "1609459200000000"
        }
        order_id, outTime = self.okx_trade_requests.construct_market_order(side)
        expected_outTime = datetime.fromtimestamp(int("1609459200000000")/1000000) + timedelta(hours=3)
        self.assertEqual(order_id, "test_order_id")
        self.assertEqual(outTime, expected_outTime)
        mock_place_order.assert_called_once_with(
            instId=self.instId,
            tdMode=self.okx_trade_requests.mgnMode,
            side=side,
            posSide=side,
            ordType="market",
            sz=self.size
        )


    @patch('okx.Trade.TradeAPI.place_algo_order')
    def test_construct_stoploss_order(self, mock_place_algo_order):
        side = 'sell'
        mock_place_algo_order.return_value = {
            "code": "0",
            "data": [{"ordId": "test_stoploss_order_id"}]
        }
        order_id = self.okx_trade_requests.construct_stoploss_order(side)
        self.assertEqual(order_id, "test_stoploss_order_id")
        mock_place_algo_order.assert_called_once_with(
            instId=self.instId,
            tdMode=self.okx_trade_requests.mgnMode,
            side=side,
            posSide=self.posSide,
            ordType="conditional",
            sz=self.size,
            slTriggerPx=self.slPrice,
            slOrdPx="-1",
            slTriggerPxType="last"
        )


    @patch('okx.Trade.TradeAPI.place_algo_order')
    def test_construct_takeprofit_order(self, mock_place_algo_order):
        side = 'sell'
        mock_place_algo_order.return_value = {
            "code": "0",
            "data": [{"ordId": "test_takeprofit_order_id"}]
        }
        order_id = self.okx_trade_requests.construct_takeprofit_order(side)
        self.assertEqual(order_id, "test_takeprofit_order_id")
        mock_place_algo_order.assert_called_once_with(
            instId=self.instId,
            tdMode=self.okx_trade_requests.mgnMode,
            side=side,
            posSide=self.posSide,
            ordType="conditional",
            sz=self.size,
            tpTriggerPx=self.tpPrice,
            tpOrdPx="-1",
            tpTriggerPxType="last"
        )

if __name__ == '__main__':
    unittest.main()