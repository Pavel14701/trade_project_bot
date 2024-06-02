import os, time, hmac, base64, hashlib, logging
from redis import Redis
from dotenv import load_dotenv


class LoadUserSettingData:
    """Summary:
    Class for loading and setting user-specific settings and data.

    Explanation:
    This class provides static methods for setting logging settings, loading user settings from environment variables, creating a signature for private subscription, listening to a Redis channel, and publishing messages to a Redis channel.

    Returns:
    - For set_logging_settings: Logger object for websocket logging.
    - For load_user_settings: Tuple containing user settings such as flag, timeframes, instrument IDs, passphrase, API key, secret key, host, database, and port.
    - For create_signature: Signature for private subscription.
    - For listen_to_redis_channel and publish_message: None
    """
    @staticmethod
    def set_logging_settings():
        """Summary:
        Set logging settings for the websocket.

        Explanation:
        This static method configures the logging settings for the websocket, enabling DEBUG level logging to a file named 'test.log'.

        Returns:
        - Logger object for the websocket logging.
        """
        ws_logger = logging.getLogger('websocket')
        ws_logger.setLevel(logging.DEBUG)
        ws_file_handler = logging.FileHandler("test.log")
        ws_logger.addHandler(ws_file_handler)
        return ws_logger

    @staticmethod
    def load_user_settings():
        """Summary:
        Load user settings from environment variables.

        Explanation:
        This static method loads various user settings such as flag, timeframes, instrument IDs, passphrase, API key, secret key, host, database, and port from the environment variables defined in the '.env' file.

        Returns:
        - Tuple containing user settings including flag, timeframes, instrument IDs, passphrase, API key, secret key, host, database, and port.
        """
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
        """Summary:
        Create a signature for private subscription.

        Explanation:
        This static method generates a signature for private subscription based on the provided secret key and current timestamp.

        Args:
        - secret_key: The secret key used for generating the signature.

        Returns:
        - The generated signature for private subscription.
        """
        timestamp = int(time.time())
        sign = f'{timestamp}GET/users/self/verify'
        total_params = bytes(sign, encoding='utf-8')
        signature = hmac.new(bytes(secret_key, encoding='utf-8'), total_params, digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(signature)
        signature = str(signature, 'utf-8')
        return signature

    #Настройка и подключение слушателя редис
    @staticmethod
    def listen_to_redis_channel(host, port, db):
        """Summary:
        Listen to a Redis channel.

        Explanation:
        This static method connects to a Redis server using the provided host, port, and database, subscribes to a specific channel, and continuously listens for messages, printing them if received.

        Args:
        - host: The host address of the Redis server.
        - port: The port number of the Redis server.
        - db: The database number of the Redis server.

        Returns:
        None
        """
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
        """Summary:
        Publish a message to a Redis channel.

        Explanation:
        This static method connects to a Redis server using the provided host, port, and database, and publishes a message to the specified channel.

        Args:
        - channel: The channel to which the message will be published.
        - message: The message to be published.
        - host: The host address of the Redis server.
        - port: The port number of the Redis server.
        - db: The database number of the Redis server.

        Returns:
        None
        """
        r = Redis(host, port, db)
        r.publish(channel, message)
