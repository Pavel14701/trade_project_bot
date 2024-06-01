import os, time, hmac, base64, hashlib, logging
from redis import Redis
from dotenv import load_dotenv


class LoadUserSettingData:
    @staticmethod
    def set_logging_settings():
        ws_logger = logging.getLogger('websocket')
        ws_logger.setLevel(logging.DEBUG)
        ws_file_handler = logging.FileHandler("test.log")
        ws_logger.addHandler(ws_file_handler)
        return ws_logger

    @staticmethod
    def load_user_settings():
        load_dotenv('.env')
        flag = str(os.getenv("FLAG"))
        timeframes_string = str(os.getenv("TIMEFRAMES"))
        timeframes_list = timeframes_string.split(',')
        timeframes = tuple(timeframes_list)
        instIds_string = str(os.getenv("INSTIDS"))
        instIds_list = instIds_string.split(',')
        instIds = tuple(instIds_list)
        passphrase = str(os.getenv("PASSPHRASE"))
        api_key = str(os.getenv("API_KEY"))
        secret_key = str(os.getenv("SECRET_KEY"))
        host = str(os.getenv("HOST"))
        port = int(os.getenv("PORT"))
        db = int(os.getenv("DB"))
        print(f'db={db} {type(db)}\nport={port} {type(port)}\nhost={host} {type(host)}')
        return(flag, timeframes, instIds, passphrase, api_key, secret_key, host, db, port)


    #Создание подписи для private подписки
    @staticmethod
    def create_signature(secret_key):
        timestamp = int(time.time())
        sign = str(timestamp) + 'GET' + '/users/self/verify'
        total_params = bytes(sign, encoding='utf-8')
        signature = hmac.new(bytes(secret_key, encoding='utf-8'), total_params, digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(signature)
        signature = str(signature, 'utf-8')
        return signature

    #Настройка и подключение слушателя редис
    @staticmethod
    def listen_to_redis_channel(host, port, db):
        r = Redis(host, port, db)
        pubsub = r.pubsub()
        pubsub.subscribe('my-channel')
        while True:
            message = pubsub.get_message()
            if message and message['type'] == 'message':
                print(f"Получено сообщение: {message['data'].decode('utf-8')}")
            time.sleep(1)

    # Функция для публикации сообщения
    @staticmethod
    def publish_message(channel, message, host, port, db):
        r = Redis(host, port, db)
        r.publish(channel, message)
