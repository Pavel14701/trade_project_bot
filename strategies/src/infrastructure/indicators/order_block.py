import numpy as np
import pandas as pd
from scipy.signal import find_peaks  # type: ignore

from strategies.src.domain.entities import OrderBlockDetectorDM
from strategies.src.infrastructure._types import PriceDataFrame


class OrderBlockDetector:
    def zigzag_indicator(
        self, 
        data: PriceDataFrame, 
        config: OrderBlockDetectorDM
    ) -> pd.DataFrame:
        peaks, _ = find_peaks(
            x=data.high_prices, 
            height=config.height,
            threshold=config.threshould,
            distance=config.distance,
            prominence=config.peak_prominance,
            width=config.width,
            wlen=config. wlen,
            rel_height=config.rel_height,
            plateau_size=config.plateu_size
        )
        valleys, _ = find_peaks(
            x=data.low_prices, 
            height=config.height,
            threshold=config.threshould,
            distance=config.distance,
            prominence=config.valley_prominance,
            width=config.width,
            wlen=config. wlen,
            rel_height=config.rel_height,
            plateau_size=config.plateu_size
        )
        peaks_array = np.full_like(data.high_prices, np.nan)
        valleys_array = np.full_like(data.low_prices, np.nan)
        peaks_array[peaks] = data.high_prices[peaks]
        valleys_array[valleys] = data.low_prices[valleys]
        return pd.DataFrame(
            {"peaks": peaks_array, "valleys": valleys_array},
            index=data.index
        )