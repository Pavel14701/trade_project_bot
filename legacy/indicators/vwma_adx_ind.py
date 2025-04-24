#libs
from concurrent.futures import ThreadPoolExecutor
import asyncio, numpy as np, pandas as pd, matplotlib.pyplot as plt
#configs
from configs.load_settings import ConfigsProvider


class VWMAADXIndicator:
    def __init__(self, data: pd.DataFrame):
        settings = ConfigsProvider().load_vwma_adx_configs()
        self.vwma_lenghts = settings['vwma_adx_vwma_lenghts']
        self.adx_period = settings['vwma_adx_adx_period']
        self.adx_threshold = settings['vwma_adx_adx_threshold']
        self.adx_smooth = settings['vwma_adx_adx_smooth']
        self.adx_di_period = settings['vwma_adx_di_period']#14
        self.data = data


    def calculate_vwma_adx(self):
        self.data["UpMove"] = self.data["High"].diff()
        self.data["DownMove"] = self.data["Low"].diff()
        self.data["+DM"] = np.where((self.data["UpMove"] > self.data["DownMove"]) \
            & (self.data["UpMove"] > 0), self.data["UpMove"], 0)
        self.data["-DM"] = np.where((self.data["DownMove"] > self.data["UpMove"]) \
            & (self.data["DownMove"] > 0), self.data["DownMove"], 0)
        self.data["+DM_Smooth"] = self.data["+DM"].ewm(span=self.adx_di_period, adjust=False).mean()
        self.data["-DM_Smooth"] = self.data["-DM"].ewm(span=self.adx_di_period, adjust=False).mean()
        self.data["ATR"] = self.data["Close"].diff().abs().ewm(span=self.adx_di_period, adjust=False).mean()
        self.data["+DI"] = self.data["+DM_Smooth"] / self.data["ATR"] * 100
        self.data["-DI"] = self.data["-DM_Smooth"] / self.data["ATR"] * 100
        self.data["DX"] = np.abs(self.data["+DI"] - self.data["-DI"]) / (self.data["+DI"] + self.data["-DI"]) * 100
        self.data["ADX"] = self.data["DX"].ewm(span=self.adx_period, adjust=False).mean()
        self.data["ADX_Smooth"] = self.data["ADX"].ewm(span=self.adx_smooth, adjust=False).mean()
        self.data["ADX_Strong_Trend"] = self.data["ADX_Smooth"] > self.adx_threshold
        self.data["ADX_Peak"] = self.data["ADX_Smooth"].where((self.data["ADX_Smooth"].shift(1)\
            < self.data["ADX_Smooth"]) & (self.data["ADX_Smooth"].shift(-1)\
                < self.data["ADX_Smooth"])).ffill(limit=1)
        self.data["ADX_Trough"] = self.data["ADX_Smooth"].where((self.data["ADX_Smooth"].shift(1)\
            > self.data["ADX_Smooth"]) & (self.data["ADX_Smooth"].shift(-1)\
                > self.data["ADX_Smooth"])).ffill(limit=1)
        self.data["ADX_Trend"] = np.nan
        self.data.loc[self.data["ADX_Peak"].notna(), "ADX_Trend"] = self.data["ADX_Peak"]
        self.data.loc[self.data["ADX_Trough"].notna(), "ADX_Trend"] = self.data["ADX_Trough"]
        self.data["ADX_Trend"] = self.data["ADX_Trend"].interpolate(method="linear")
        WMAV = []
        for i in range(self.vwma_lenghts, len(self.data)):
            data_n = self.data.iloc[i-self.vwma_lenghts:i]
            numerator = (data_n["Volume"] * data_n["Close"] * data_n["ADX_Trend"]).sum()
            denominator = (data_n["Volume"] * data_n["ADX_Trend"]).sum()
            WMAV.append(numerator / (denominator + 1e-9))
        self.data["WMAV"] = np.nan
        self.data.loc[self.data.index[self.vwma_lenghts:], "WMAV"] = WMAV
        return self.data


    async def calculate_vwma_adx_async(self) -> pd.DataFrame:
        # sourcery skip: inline-immediately-returned-variable
        executor = ThreadPoolExecutor()
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, self.calculate_vwma_adx)
        return result


    def create_vizualization_vwma_adx(self):
        self.calculate_vwma_adx()
        plt.figure(figsize=(10, 6))
        plt.plot(self.data.index, self.data["Close"], label="Price", color='black')
        plt.plot(self.data.index, self.data["WMAV"], label="WMAV", color='grey')
        plt.plot(self.data.index[self.data["ADX_Strong_Trend"]],self.data["WMAV"][self.data["ADX_Strong_Trend"]], label="Strong Trend", color='red')
        plt.title("Price with WMAV and ADX Trendline")
        plt.xlabel("Date")
        plt.ylabel("USD")
        plt.legend()
        plt.show()
