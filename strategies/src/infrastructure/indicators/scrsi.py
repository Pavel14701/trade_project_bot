import pandas as pd
import numpy as np

from strategies.src.domain.entities import ScrsiConfigDM
from strategies.src.infrastructure._types import PriceDataFrame


class SmoothCicleRsi:
    def calculate_crsi(
            self, 
            data: PriceDataFrame,
            config: ScrsiConfigDM
        ) -> pd.DataFrame:
        cyclelen = config.domcycle // 2
        cyclicmemory = config.domcycle * 2
        up = pd.Series(
            np.maximum(data.close_prices.diff(), 0)
        ).rolling(window=cyclelen).mean()
        down = pd.Series(
            np.minimum(data.close_prices.diff(), 0)
        ).rolling(window=cyclelen).mean()
        rsi = 100 - 100 / (
            1 + np.divide(
                up, down, out=np.zeros_like(up),
                where=down != 0
            )
        )
        rsi = np.clip(rsi, 0, 100)
        rsi_scaled = (rsi - 50) * 2
        torque = 2.0 / (config.vibration + 1)
        phasingLag = (config.vibration - 1) // 2
        crsi = np.zeros_like(rsi_scaled)
        mask = np.arange(len(rsi_scaled)) >= phasingLag
        crsi[mask] = torque * (
            2 * rsi_scaled[mask] - np.roll(rsi_scaled, phasingLag)[mask]
        ) + (1 - torque) * np.roll(crsi, 1)[mask]
        crsi_clean = crsi[~np.isnan(crsi)]
        db = float(
            np.percentile(
                crsi_clean[:cyclicmemory], 
                config.leveling
            ) if len(
                crsi_clean[:cyclicmemory]
            ) > 0 else -100
        )
        ub = float(
            np.percentile(
                crsi_clean[:cyclicmemory], 100 - config.leveling
            ) if len(
                crsi_clean[:cyclicmemory]
            ) > 0 else 100
        )
        crsi = crsi.flatten()
        rsi_scaled = rsi_scaled.flatten()
        return pd.DataFrame({  
            'CRSI Scaled': rsi_scaled,  
            'Lower Bound': db,  
            'Upper Bound': ub
        }, index=data.index)
