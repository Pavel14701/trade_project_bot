from datetime import datetime
from indicators.separate_files.AVSL import AVSLIndicator
from datasets.database import DataAllDatasets
from User.LoadSettings import LoadUserSettingData

class CheckSignalData:
    """Summary:
    Initialize parameters for checking signal data.

    Explanation:
    This class initializes the parameters required for checking signal data,
    such as the flag, instrument ID, database Base and Session,
    classes dictionary, and optional data loading constraints.
    """

    @staticmethod         
    def avsl_signals(flag, instId, timeframe, Base, Session, classes_dict, host, port, db, lenghts):
        try:
            data = DataAllDatasets.get_current_chart_data(
                flag, instId, timeframe, Base, Session, 
                classes_dict, None, None, lenghts
                )
            cross_up, cross_down, AVSL, close_prices, last_bar_signal = AVSLIndicator.calculate_avsl(data)
            current_time = datetime.now()
            formatted_time = current_time.isoformat()
            message = dict([
                ("time", formatted_time),
                ("instId", instId),
                ("timeframe", timeframe),
                ("signal", last_bar_signal)
            ])
            LoadUserSettingData.publish_message('my-channel', message, host, port, db)
        except Exception as e:
            print(f'\nПроизошла ошибка: \n{e}\n')
        
        
        
        
        
        