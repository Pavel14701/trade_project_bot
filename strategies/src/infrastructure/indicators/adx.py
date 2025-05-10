import pandas_ta as ta
import pandas as pd

from strategies.src.domain.entities import AdxConfigDM
from strategies.src.infrastructure._types import PriceDataFrame


class ADXTrend:
    def calculate(
        self, 
        data: PriceDataFrame, 
        config: AdxConfigDM
    ) -> pd.DataFrame:
        adx_ind = ta.adx(
            high=data.high_prices, 
            low=data.low_prices, 
            close=data.close_prices, 
            length=config.length, 
            lensig=config.lensig, 
            scalar=config.scalar,
            mamode=config.mamode,
            drift=config.drift, 
            offset=config.offset
        )
        if any(
            adx_ind.get(f"{indicator}_{config.length}") is None 
            for indicator in ["ADX", "DMP", "DMN"]
        ):
            raise ValueError(
                "Ошибка: отсутствуют необходимые данные ADX, DMP или DMN."
            )
        return pd.DataFrame(
            {
                "adx": adx_ind[f"ADX_{config.lensig}"],
                "dmp": adx_ind[f"DMP_{config.length}"],
                "dmn": adx_ind[f"DMN_{config.length}"],
            },
            index=data.index
        )

    def get_signal(self, adx_trigger: int, data: pd.DataFrame) -> bool:
        return int(data["adx"].iloc[-1]) >= adx_trigger