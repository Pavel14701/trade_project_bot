#!/usr/bin/env python3
from configs.load_settings import ConfigsProvider
from listners.ivent_listner import OKXIventListner


if __name__ == '__main__':
    settings = ConfigsProvider().load_user_configs()
    listner_instance = OKXIventListner()
    listner_instance.create_listner()
