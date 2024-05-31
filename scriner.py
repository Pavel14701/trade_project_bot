#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datasets.database import DataAllDatasets
from User.LoadSettings import LoadUserSettingData


flag, timeframes, instIds, passphrase, api_key, secret_key = LoadUserSettingData.load_user_settings()
engine = create_engine("sqlite:///C:\\Users\\Admin\\Desktop\\trade_project_bot\\datasets\\TradeUserDatasets.db")
Base = declarative_base()
data_all_datasets = DataAllDatasets(instIds, timeframes)
classes_dict = data_all_datasets.create_classes(Base)
Base.metadata.create_all(engine)
Session = sessionmaker(bind = engine)


def start():
    print(flag, timeframes) 

if __name__ == "__main__":
    start()
    
