import pandas as pd
import numpy as np
from numpy.typing import NDArray
import  pandas_ta as ta

from strategies.src.domain.entities import AvslConfigDM
from strategies.src.infrastructure._types import PriceDataFrame


class AVSL:
    def calculate_avsl(
        self,
        data: PriceDataFrame,
        config: AvslConfigDM
    ) -> pd.DataFrame:
        # Рассчитываем VWMA
        vw_ma_fast: pd.Series = ta.vwma(
            close=data.close_prices, 
            colume=data.volumes, 
            length=config.length_fast
        )
        vw_ma_slow: pd.Series = ta.vwma(
            close=data.close_prices, 
            volume=data.volume,
            length=config.length_slow
        )
        # Рассчитываем VPC
        vpc: pd.Series = vw_ma_slow - ta.sma(
            close=data.close_prices, 
            lenght=config.length_slow,
            talib=True
        )
        # Рассчитываем VPR
        vpr: pd.Series = vw_ma_fast / ta.sma(
            close=data.close_prices, 
            lenght=config.length_fast, 
            talib=True
        )
        # Рассчитываем VM
        vm: pd.Series = ta.sma(
            close=data.volumes, 
            length=config.length_fast, 
            talib=True
        ) / ta.sma(
            close=data.volumes, 
            length=config.length_slow,
            talib=True
        )
        #
        vpci: pd.Series = vpc * vpr * vm
        PriceV = self._price_fun()
        deviation = config.stand_div * vpci * vm
        avsl = ta.sma(
            close=data.low_prices-PriceV+deviation,
            timeperiod=self.length_slow, 
            talib=True
        )
        return pd.DataFrame({"avsl": avsl}, index=data.index)


    def _price_fun(
        self,
        data: PriceDataFrame,
        vpc: pd.Series,
        vpr: pd.Series,
        vpci: pd.Series,
    ) -> NDArray:
        PriceV = np.zeros_like(vpc)
        for i in range(len(vpc)):
            if np.isnan(vpci.iloc[i]):
                lenV = 0
            else:
                lenV = int(
                    round(abs(vpci.iloc[i] - 3))
                ) if vpc.iloc[i] < 0 else round(
                    vpci.iloc[i] + 3
                )
            VPCc = -1 if (
                vpc.iloc[i] > -1
            ) & (
                vpc.iloc[i] < 0
            ) else 1 if (
                vpc.iloc[i] < 1
            ) & (
                vpc.iloc[i] >= 0
            ) else vpc.iloc[i]
            Price = np.sum(data.low_prices.iloc[i - lenV + 1:i + 1] / VPCc / vpr.iloc[i - lenV + 1:i + 1]) if lenV > 0 else data.low_prices.iloc[i]
            PriceV[i] = Price / lenV / 100 if lenV > 0 else Price
        return PriceV
