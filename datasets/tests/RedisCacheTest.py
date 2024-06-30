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


    @patch('redis.Redis.pubsub')
    def test_subscribe_to_redis_channel(self, mock_pubsub):
        self.redis_cache.subscribe_to_redis_channel()
        mock_pubsub.assert_called_once()
        self.redis_cache.pubsub.subscribe.assert_called_once_with(self.channel)


@patch('redis.Redis.pubsub')
def test_check_redis_message(self, mock_pubsub):
    mock_pubsub_instance = MagicMock()
    mock_pubsub.return_value = mock_pubsub_instance
    mock_pubsub_instance.get_message.return_value = {
        'type': 'message',
        'data': pickle.dumps({'command': 'test_command'})
    }
    self.redis_cache.subscribe_to_redis_channel()
    self.redis_cache.check_redis_message()
    self.assertEqual(self.redis_cache.command, {'command': 'test_command'})


    @patch('redis.Redis.set')
    def test_send_redis_command(self, mock_redis_set):
        self.redis_cache.command = {'command': 'test_command'}
        self.redis_cache.send_redis_command()
        mock_redis_set.assert_called_once_with(
            f'message_{self.instId}_{self.timeframe}', 
            pickle.dumps({'command': 'test_command'})
        )

    @patch('redis.Redis.get')
    def test_load_message_from_cache(self, mock_redis_get):
        mock_redis_get.return_value = pickle.dumps({'command': 'test_command'})
        loaded_command = self.redis_cache.load_message_from_cache()
        self.assertEqual(loaded_command, {'command': 'test_command'})


if __name__ == '__main__':
    unittest.main()

