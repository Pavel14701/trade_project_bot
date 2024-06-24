import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from database import DataAllDatasets, Base
import pandas as pd
from User.LoadSettings import LoadUserSettingData


<<<<<<< HEAD
class StreamData(LoadUserSettingData):
    def __init__(self, Session, classes_dict: dict, instId: str, timeframe: str, lenghtsSt: int):
        super().__init__()
        self.instId = instId
        self.Session = Session
        self.classes_dict = classes_dict
        self.timeframe = timeframe
        self.lenghtsSt = lenghtsSt
        
    def load_data(self):
=======
class StreamData:
    """
    Represents a data streaming class.

    Methods:
    - load_data(Session, classes_dict): Loads current chart data.
    - load_data_for_period(Session, classes_dict, data): Loads data for a specific period.
    """
    def __init__(self, lengths, instId, timeframe, flag):
        """
        Initializes the object with provided parameters.

        Args:
        - lengths: The lengths parameter.
        - instId: The instId parameter.
        - timeframe: The timeframe parameter.
        - flag: The flag parameter.
        """
        super().__init__(lengths, instId, timeframe, flag)
        
    def load_data(self, Session, classes_dict):
        """
        Loads current chart data.

        Args:
        - Session: The session object for data retrieval.
        - classes_dict: A dictionary containing classes information.

        Returns:
        - The current chart data.
        """
>>>>>>> c2593ce6e7c3f66021f4f4e18b0b1accb3ed41f7
        return DataAllDatasets.get_current_chart_data(
            self.flag, self.instId, self.timeframe, Base,
            self.Session, self.classes_dict, None, None, self.lenghtsSt
        )
    
<<<<<<< HEAD
    def load_data_for_period(self, data: pd.DataFrame):
=======
    def load_data_for_period(self, Session, classes_dict, data):
        """
        Loads data for a single period. Delete first period string in df and add single period string at last.

        Args:
        - Session: The session object for data retrieval.
        - classes_dict: A dictionary containing classes information.
        - data: The data for the period.

        Returns:
        - Concatenated data for the specified period.
        """
>>>>>>> c2593ce6e7c3f66021f4f4e18b0b1accb3ed41f7
        data = data.drop(data.index[:1])
        new_data = DataAllDatasets.get_current_chart_data(
            self.flag, self.instId, self.timeframe, Base,
            self.Session, self.classes_dict, None, None, lenghts = 1
        )
        return pd.concat([data, new_data], ignore_index=True)