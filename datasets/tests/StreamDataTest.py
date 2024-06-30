import unittest, sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot//')
from unittest.mock import patch, MagicMock
import pandas as pd
from sqlalchemy.orm import sessionmaker
from datasets.LoadDataStream import StreamData

class TestStreamData(unittest.TestCase):
    def setUp(self):
        self.instId = 'testInst'
        self.timeframe = '1h'
        self.lenghtsSt = 10
        self.Session = sessionmaker()
        self.classes_dict = {'TestClass': MagicMock()}
        self.stream_data = StreamData(self.Session, self.classes_dict, self.instId, self.timeframe, self.lenghtsSt)

    @patch('datasets.database.DataAllDatasets.get_current_chart_data')
    def test_load_data(self, mock_get_current_chart_data):
        expected_data = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        mock_get_current_chart_data.return_value = expected_data
        result_data = self.stream_data.load_data()
        self.assertTrue(result_data.equals(expected_data))

    @patch('datasets.database.DataAllDatasets.get_current_chart_data')
    def test_load_data_for_period(self, mock_get_current_chart_data):
        initial_data = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        new_data_row = pd.DataFrame({'a': [7], 'b': [8]})
        mock_get_current_chart_data.return_value = new_data_row
        result_data = self.stream_data.load_data_for_period(initial_data)
        expected_data = pd.DataFrame({'a': [2, 3, 7], 'b': [5, 6, 8]})
        self.assertTrue(result_data.equals(expected_data))

if __name__ == '__main__':
    unittest.main()
