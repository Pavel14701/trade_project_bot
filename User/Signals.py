import pandas as pd
from indicators.AVSL import AVSLIndicator
from datasets.database import DataAllDatasets

class CheckSignalData:
    """Summary:
    Initialize parameters for checking signal data.

    Explanation:
    This class initializes the parameters required for checking signal data,
    such as the flag, instrument ID, database Base and Session,
    classes dictionary, and optional data loading constraints.
    """


    def __init__(self, flag, instId, Base, Session, classes_dict,
            load_data_after = None, load_data_before = None,
            lenghts = None):
        """Summary:
        Initialize signals parameters for analysis.

        Explanation:
        This function initializes the parameters required for signal analysis including flag, instrument ID, timeframes, database Base and Session, classes dictionary, data, optional data loading time constraints, and lengths for analysis.

        Args:
        - flag: The flag indicating the type of signal.
        - instId: The instrument ID for signal analysis.
        - timeframes: The list of timeframes for signal analysis.
        - Base: The database Base for data access.
        - Session: The database Session for data access.
        - classes_dict: Dictionary of classes for signal analysis.
        - load_data_after: Optional parameter for loading data after a specific time.
        - load_data_before: Optional parameter for loading data before a specific time.
        - lenghts: Optional lengths for analysis.

        Returns:
        None
        """
        self.flag = flag
        self.instId = instId
        self.Base = Base
        self.Session = Session
        self.classes_dict = classes_dict
        self.load_data_after = load_data_after
        self.load_data_before = load_data_before
        self.lenghts = lenghts
        
        
    def avsl_signals(self, timeframe):
        data = DataAllDatasets.get_current_chart_data(
            self.flag, self.instId, self.Base, self.Session, self.classes_dict,
            self.lenghts, timeframe)
        cross_up, cross_down, AVSL, close_prices, last_bar_signal = AVSLIndicator.calculate_avsl(self.data)
        return last_bar_signal
        
        
        
        
        
        