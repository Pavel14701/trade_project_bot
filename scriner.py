#!/usr/bin/env python3
import os 
from datasets.database import DataAllDatasets, get_charts, TradeUserData
from dotenv import load_env
from User.LoadSettings import LoadUserSettingsData

def start():
    load_env()
    load_user_settings()
    

if __name__ == "__main__":
    start()
    print(flag, timeframes)
