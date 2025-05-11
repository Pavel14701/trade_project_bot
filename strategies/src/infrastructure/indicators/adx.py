import pandas_ta as ta
import pandas as pd

from strategies.src.domain.entities import AdxConfigDM
from strategies.src.infrastructure._types import PriceDataFrame


class ADXTrend:
    """
    Average Directional Index (ADX) Trend Indicator Implementation.
    The ADX measures the strength of a trend and is 
    composed of three components:
    - **ADX**: Indicates the trend strength 
      (values above 25 suggest a strong trend).
    - **DMP (+DI)**: Positive directional movement 
      (upward trend indicator).
    - **DMN (-DI)**: Negative directional movement 
      (downward trend indicator).
    Formula:
    1. Compute **True Range (TR)**, which reflects market volatility.
    2. Calculate the **Directional Movement (+DM / -DM)** based on 
      high/low price action.
    3. Apply **Moving Averages** to smooth +DM, -DM values.
    4. Compute **ADX** as an exponentially smoothed average 
      of the Directional Index.
    Usage:
    - Helps traders determine if a trend is strong 
      enough to justify entering a trade.
    - Can be combined with other trend indicators 
      (e.g., moving averages) for confirmation.
    """

    def calculate_adx(
        self, 
        data: PriceDataFrame, 
        config: AdxConfigDM
    ) -> pd.DataFrame:
        """
        Computes the ADX, DMP (+DI), and DMN (-DI) trend indicators.
        Args:
            data (PriceDataFrame): Price dataset containing 
              high, low, and close prices.
            config (AdxConfigDM): Configuration for ADX 
              (length, smoothing factors, drift, offset).
        Returns:
            pd.DataFrame: A DataFrame containing ADX, DMP, and DMN trend values.
        Raises:
            ValueError: If the ADX calculation returns missing 
              values for any required component.
        """
        # Compute ADX and its components using pandas-ta
        adx_ind = ta.adx(
            high=data.high_prices,
            low=data.low_prices,
            close=data.close_prices,
            length=config.length,
            # Signal length for ADX smoothing
            lensig=config.lensig,
            # Scaling factor for values
            scalar=config.scalar,  
            # Moving average mode (e.g., EMA, SMA)
            mamode=config.mamode,  
            drift=config.drift,
            offset=config.offset
        )
        #  Validate if all required components exist
        if missing_indicators := [
            indicator
            for indicator in ["ADX", "DMP", "DMN"]
            if adx_ind.get(f"{indicator}_{config.length}") is None
        ]:
            raise ValueError(
                f"""Error: Missing required ADX components: 
                {', '.join(missing_indicators)}."""
            )
        # Return structured DataFrame
        return pd.DataFrame(
            {
                "adx": adx_ind[f"ADX_{config.lensig}"],
                "dmp": adx_ind[f"DMP_{config.length}"],
                "dmn": adx_ind[f"DMN_{config.length}"],
            },
            index=data.index
        )

    def get_signal(self, adx_trigger: int, data: pd.DataFrame) -> bool:
        """
        Determines whether the trend strength exceeds a defined threshold.
        Args:
            adx_trigger (int): Minimum ADX value required to confirm a trend.
            data (pd.DataFrame): DataFrame containing ADX values.
        Returns:
            bool: True if ADX exceeds the threshold, False otherwise.
        """
        return int(data["adx"].iloc[-1]) >= adx_trigger
