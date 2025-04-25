# !!!! NOT TESTED

#libs
import pandas as pd, numpy as np, asyncio
from configs.load_settings import ConfigsProvider
from typing import Optional, Union
from concurrent.futures import ThreadPoolExecutor


class SmoothCicleRsi:
    def __init__(self, data:pd.DataFrame, return_pd:Optional[bool]=None) -> None:
        configs = ConfigsProvider().load_crsi_configs()
        self.domcycle = configs['crsi_domcycle'] #20
        self.vibration = configs['crsi_vibration'] #10
        self.leveling = configs['crsi_leveling'] #10.0
        self.data = data


    def calculate_crsi(self) -> Union[pd.DataFrame, dict]:
        cyclelen = self.domcycle // 2
        cyclicmemory = self.domcycle * 2
        up = pd.Series(np.maximum(self.data['Close'].diff(), 0)).rolling(window=cyclelen).mean()
        down = pd.Series(np.minimum(self.data['Close'].diff(), 0)).rolling(window=cyclelen).mean()
        rsi = 100 - 100 / (1 + up / down)
        torque = 2.0 / (self.vibration + 1)
        phasingLag = (self.vibration - 1) // 2
        crsi = np.zeros(len(self.data['Close']))
        for i in range(len(self.data['Close'])):
            if i < phasingLag:
                continue
            crsi[i] = torque * (2 * rsi[i] - rsi[i - phasingLag]) + (1 - torque) * (crsi[i - 1])
        lmax = np.max(crsi[:cyclicmemory])
        lmin = np.min(crsi[:cyclicmemory])
        mstep = (lmax - lmin) / 100
        aperc = self.leveling / 100
        db, ub = 0.0, 0.0
        for steps in range(101):
            testvalue = lmin + mstep * steps
            below = np.sum(crsi < testvalue)
            ratio = below / cyclicmemory
            if ratio >= aperc:
                db = testvalue
                break
        for steps in range(101):
            testvalue = lmax - mstep * steps
            above = np.sum(crsi >= testvalue)
            ratio = above / cyclicmemory
            if ratio >= aperc:
                ub = testvalue
                break
        return {crsi, db, ub}



    async def calculate_crsi_async(self) -> Union[pd.DataFrame, dict]:
        # sourcery skip: inline-immediately-returned-variable
        executor = ThreadPoolExecutor()
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, self.calculate_crsi)
        return result

    
            