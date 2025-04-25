#Info
INFO = {
    'get_candlesticks': {'method': 'GET', 'url': '/api/v5/market/candles?instId'},
    'get_account_balance': {'method': 'GET', 'url': '/api/v5/account/balance'},
    'set_leverage_inst': {'method': 'POST', 'url': '/api/v5/account/set-leverage'},
    'set_leverage_short_long': {'method': 'POST', 'url': '/api/v5/account/set-leverage'},
    'check_contract_price': {'method': 'GET', 'url': '/api/v5/account/instruments'},
    'get_last_price': {'method': 'GET', 'url': '/api/v5/market/ticker?instId='},
    'set_trading_mode': {'method': 'POST', 'url': '/api/v5/account/set-position-mode'}
}
TRADE = {
    'construct_market_order': {'method': 'POST', 'url': '/api/v5/trade/order'},
    'construct_stoploss_order': {'method': 'POST', 'url': '/api/v5/trade/order-algo'},
    'change_stoploss_order': {'method': 'POST', 'url': '/api/v5/trade/amend-algos'},
    'construct_takeprofit_order': {'method': 'POST', 'url': '/api/v5/trade/order-algo'},
    'change_takeprofit_order': {'method': 'POST', 'url': '/api/v5/trade/amend-algos'},
    'construct_limit_order': {'method': 'POST', 'url': '/api/v5/trade/order'},
    'check_position': {'method': 'GET', 'url': '/api/v5/trade/order'},
    'get_all_order_list': {'method': 'GET', 'url': '/api/v5/trade/orders-pending'},
    'get_all_opened_positions': {'method': 'GET', 'url': '/api/v5/account/positions'},
    'get_history': {'method': 'GET', 'url': '/api/v5/account/positions'}
}
#TIMEFRAMES FOR VALIDATE 
TIMEFRAMES  = (
    '1m', '3m', '5m', '15m', '30m', '1H', '2H', '4H',
    '6H', '12H', '1D', '2D', '3D', '1W', '1M' '3M',
    '6Hutc', '12Hutc', '1Dutc', '2Dutc', '3Dutc',
    '1Wutc', '1Mutc', '3Mutc'
)