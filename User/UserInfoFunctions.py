from decimal import Decimal
import okx.Account as Account
import okx.Trade as Trade


"""
# Данные Api
# !!!Важно, если не вязать IP адрес к ключу,
у которого есть разрешения на вывод и торговлю(отдельно),
то он автоматически удалиться через 14 дней.
"""

class UserInfo:
    """Summary:
    Class for managing user information and trading functions.

    Explanation:
    This class provides methods for checking balance, setting leverage for individual instruments, setting leverage for isolated positions, and setting trading mode.

    Args:
    - instId: The ID of the instrument.
    - leverage: The leverage value to set.
    - mgnMode: The margin mode to use (cross or isolated).
    - posSide: The position side (short or long).

    Returns:
    - For check_balance: The user's balance as a float.
    - For set_leverage_inst and set_leverage_short_long: The result of setting leverage for the specified instrument.
    - For set_trading_mode: The result of setting the trading mode.
    """
    def __init__(self, api_key, secret_key, passphrase, flag):
        """Summary:
        Initialize UserInfo object with API keys and flags.

        Explanation:
        This constructor initializes the UserInfo object with the provided API keys and flags for accessing trade and account APIs.

        Args:
        - api_key: The API key for authentication.
        - secret_key: The secret key for authentication.
        - passphrase: The passphrase for authentication.
        - flag: A flag indicating a specific setting.

        Returns:
        None
        """
        self.tradeApi = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
        self.accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
        

    # Проверка баланса
    def check_balance(self):
        """Summary:
        Check the user's balance.

        Explanation:
        This function retrieves the user's account balance using the account API and returns it as a float.

        Args:
        None

        Returns:
        - The user's balance as a float.
        """
        result_bal = self.accountAPI.get_account_balance()
        usdt_balance = Decimal(result_bal["data"][0]["details"][0]["availBal"])  # получаем значение ключа ccy по указанному пути
        balance = float(usdt_balance)
        print(f'Баланс: \n {result_bal}\n\n')
        return balance


    # Установка левериджа кросс позиций для отдельного инструмента
    def set_leverage_inst(self, instId, leverage, mgnMode):
        """Summary:
        Set leverage for a specific instrument.

        Explanation:
        This function sets the leverage for a specified instrument using the account API.

        Args:
        - instId: The ID of the instrument.
        - leverage: The leverage value to set.
        - mgnMode: The margin mode to use (cross or isolated).

        Returns:
        - The result of setting leverage for the specified instrument.
        """
        result = self.accountAPI.set_leverage(
            instId=instId,
            lever=leverage,
            mgnMode=mgnMode #cross или isolated
        )
        print(f'Установка левириджа {leverage}x, кросс для {instId}: \n{result}\n\n')


    # Установка левериджа для \изолированых позиций для шорт и лонг
    def set_leverage_short_long(self, instId, leverage, posSide, mgnMode):
        """Summary:
        Set leverage for isolated long and short positions.

        Explanation:
        This function sets the leverage for isolated long and short positions for a specified instrument using the account API.

        Args:
        - instId: The ID of the instrument.
        - leverage: The leverage value to set.
        - posSide: The position side (short or long).
        - mgnMode: The margin mode to use.

        Returns:
        - The result of setting leverage for isolated long and short positions for the specified instrument.
        """
        result = self.accountAPI.set_leverage(
            instId = instId,
            lever = leverage,
            posSide = posSide,
            mgnMode = mgnMode
        )
        print(f'Установка левериджа {leverage}x, для изолированных лонг {instId}: \n{result}\n\n')


    # Установка режима торговли
    def set_trading_mode(self):
        """Summary:
        Set the trading mode.

        Explanation:
        This function sets the trading mode to long and short positions using the account API.

        Args:
        None

        Returns:
        - The result of setting the trading mode.
        """
        result = self.accountAPI.set_position_mode(
            posMode="long_short_mode"
        )
        print(result)