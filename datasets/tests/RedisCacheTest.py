import unittest, sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot//')
from unittest.mock import patch, MagicMock
import pandas as pd
from datasets.RedisCache import RedisCache
import pickle

class TestRedisCache(unittest.TestCase):
    def setUp(self):
        self.instId = 'testInst'
        self.timeframe = '1h'
        self.channel = 'testChannel'
        self.data = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        self.redis_cache = RedisCache(self.instId, self.channel, self.timeframe, self.data)

    @patch('redis.Redis.set')
    @patch('redis.Redis.__init__', return_value=None)
    def test_add_data_to_cache(self, mock_redis_init, mock_redis_set):
        self.redis_cache.add_data_to_cache(self.data)
        mock_redis_set.assert_called_once_with(f'df_{self.instId}_{self.timeframe}', pickle.dumps(self.data))

    @patch('redis.Redis.get')
    @patch('redis.Redis.__init__', return_value=None)
    def test_load_data_from_cache(self, mock_redis_init, mock_redis_get):
        mock_redis_get.return_value = pickle.dumps(self.data)
        loaded_data = self.redis_cache.load_data_from_cache()
        self.assertTrue(loaded_data.equals(self.data))

    @patch('redis.Redis.publish')
    @patch('redis.Redis.__init__', return_value=None)
    def test_publish_message(self, mock_redis_init, mock_redis_publish):
        test_message = {'command': 'test'}
        self.redis_cache.publish_message(test_message)
        mock_redis_publish.assert_called_once_with(self.channel, pickle.dumps(test_message))

if __name__ == '__main__':
    unittest.main()

