import numpy as np
import pandas as pd
from scipy.signal import find_peaks  # type: ignore

from strategies.src.domain.entities import OrderBlockDetectorDM
from strategies.src.infrastructure._types import PriceDataFrame


class OrderBlockDetector:
    """
    Order Block Detector Using ZigZag Peaks.

    This class detects order blocks by identifying 
      **peaks** and **valleys** in price 
      data using the ZigZag pattern algorithm.

    Formula:
    1. Find **peaks** using `find_peaks()` applied 
      to **high prices**.
    2. Find **valleys** using `find_peaks()` applied 
      to **low prices**.
    3. Define peak prominence, threshold, and 
      distance to filter out weak signals.
    4. Store peak and valley locations in separate arrays.
    5. Return a DataFrame marking peaks 
      and valleys for further analysis.

    Usage:
    - Helps identify **key support 
      and resistance levels**.
    - Detects **potential reversal zones** for 
      price action traders.
    - Useful for refining entry and 
      exit points in trading strategies.
    """

    def zigzag_indicator(
        self, 
        data: PriceDataFrame, 
        config: OrderBlockDetectorDM
    ) -> pd.DataFrame:
        """
        Detects peaks and valleys in price data using 
          ZigZag pattern analysis.
        Args:
            data (PriceDataFrame): Market price 
              dataset containing high, low prices.
            config (OrderBlockDetectorDM): Configuration 
              settings for peak detection.
        Returns:
            pd.DataFrame: A DataFrame with marked peaks and valleys.
        """
        # Detect peaks (local maxima) in high prices
        peaks, _ = find_peaks(
            x=data.high_prices, 
            # Minimum peak height required
            height=config.height,         
            # Minimum threshold difference between neighboring values
            threshold=config.threshould,
            # Minimum separation distance between peaks
            distance=config.distance,       
            # Strength of peaks based on prominence
            prominence=config.peak_prominance,
            # Minimum width of peaks  
            width=config.width,             
            # Window length for peak detection
            wlen=config.wlen,               
            # Relative height for peak filtering
            rel_height=config.rel_height,   
            # Minimum plateau size for peak determination
            plateau_size=config.plateu_size 
        )
        # Detect valleys (local minima) in low prices
        valleys, _ = find_peaks(
            x=data.low_prices, 
            height=config.height,
            threshold=config.threshould,
            distance=config.distance,
            # Strength of valleys based on prominence
            prominence=config.valley_prominance,
            width=config.width,
            wlen=config.wlen,
            rel_height=config.rel_height,
            plateau_size=config.plateu_size
        )
        # Initialize arrays to store peak and valley values
        # Fill with NaN initially
        peaks_array = np.full_like(data.high_prices, np.nan)
        # Fill with NaN initially
        valleys_array = np.full_like(data.low_prices, np.nan)
        # Assign detected peak and valley values
        peaks_array[peaks] = data.high_prices[peaks]
        valleys_array[valleys] = data.low_prices[valleys]
        return pd.DataFrame(
            {"peaks": peaks_array, "valleys": valleys_array},
            index=data.index
        )
