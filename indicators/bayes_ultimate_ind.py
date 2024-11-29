import pandas as pd, numpy as np, pandas_ta as ta
from configs.load_settings import ConfigsProvider
from abc import ABC
import concurrent.futures
from baselogs.custom_logger import create_logger


# TEST OK
class BayesUtils(ABC):
    def nz(self, df:pd.Series) -> pd.Series:
        return df.replace([0, 1.0], [np.finfo(float).eps, 1.0 - np.finfo(float).eps])  # Replace zero with 1 to avoid division errors and delete 100% probability


    def nz_df(self, df:pd.DataFrame) -> pd.DataFrame:
        return df.map(lambda x: np.finfo(float).eps if x == 0 else (1 - np.finfo(float).eps if x == 1 else x))


    def calculate_probabilities_with_divergence(self, signal:pd.Series, divergence:pd.Series, confirmation_coef:float, negation_coef:float) -> pd.Series:
        probabilities = signal.rolling(window=self.bayes_period).apply(lambda x: np.sum(x) / self.bayes_period)
        divergences = divergence.rolling(window=self.bayes_period).apply(lambda x: np.any(x))
        adjusted_probabilities = self.nz(probabilities * np.where(divergences, confirmation_coef, negation_coef))
        return adjusted_probabilities


    def calc_aroon_probs_with_divs(self, signal: pd.Series, divergence: pd.Series, weak_trend: pd.Series, trend: pd.Series, strong_trend: pd.Series) -> pd.Series:
        weights = [0.9, 1.1, 1.2, 1.3, 1.0]
        probabilities = signal.rolling(window=self.bayes_period).apply(lambda x: np.sum(x) / self.bayes_period)
        divergences = divergence.rolling(window=self.bayes_period).apply(lambda x: np.any(x)).astype(bool).values
        weakness = weak_trend.rolling(window=self.bayes_period).apply(lambda x: np.any(x)).astype(bool).values
        on_trend = trend.rolling(window=self.bayes_period).apply(lambda x: np.any(x)).astype(bool).values
        on_strong_trend = strong_trend.rolling(window=self.bayes_period).apply(lambda x: np.any(x)).astype(bool).values
        conditions = [weakness, on_trend, on_strong_trend, divergences]
        choices = [weights[0], weights[1], weights[2], weights[3]]
        final_prob = self.nz(probabilities * np.select(conditions, choices, default=weights[4]))
        return final_prob


# TEST OK
class BayesRsiOscillator(BayesUtils, ABC):
    def __init__(self, data:pd.DataFrame, settings:dict, neutral_threshold:pd.Series) -> None:
        self.rsi_length = settings['rsi_length']
        self.rsi_divergences = settings['rsi_divergences'] #bool
        self.bayes_period = settings['bayes_period'] #20
        self.neutral_threshold = neutral_threshold
        self.data = data
        BayesUtils.__init__(self)


    def calc_rsi(self) -> pd.DataFrame:
        results = {}
        self.rsi = ta.rsi(self.data['Close'], self.rsi_length, talib=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                'rsi_probs1': executor.submit(self.__rsi_probs),
                'rsi_probs2': executor.submit(self.__rsi50_probs)
            }
            for name, future in futures.items():
                result = future.result()
                results[name] = result
        rsi_probs = pd.concat([results['rsi_probs1'], results['rsi_probs2']], axis=1)
        return self.nz_df(rsi_probs)

    def __rsi_probs(self) -> pd.DataFrame:
        rsi_probs1 = pd.DataFrame(index=self.data.index, columns=[
            'prob_rsi_overbought', 'prob_rsi_oversold', 'prob_rsi_neutral'])
        rsi_probs1[:] = np.nan  # Fill with NaN initially
        if self.rsi_divergences:
            # Calculate probabilities with divergences
            rsi_probs1 = self.__find_rsi_divergences(rsi_probs1)
        else:
            # Calculate basic probabilities
            rsi_probs1['prob_rsi_overbought'] = self.rsi.rolling(window=self.bayes_period).apply(lambda window: np.mean(window > 80), raw=False)
            rsi_probs1['prob_rsi_oversold'] = self.rsi.rolling(window=self.bayes_period).apply(lambda window: np.mean(window < 20), raw=False)
            rsi_probs1['prob_rsi_neutral'] = self.rsi.rolling(window=self.bayes_period).apply(lambda window: np.mean((window >= 20) & (window <= 80)), raw=False)
        return rsi_probs1


    def __rsi50_probs(self) -> pd.DataFrame:
        rsi_probs2 = pd.DataFrame(index=self.data.index, columns=[
            'probs_above_50', 'probs_below_50'])
        rsi_probs2[:] = np.nan  # Fill with NaN initially
        # Определяем текущее состояние и длительность
        state_above_50 = self.rsi > 50
        state_below_50 = self.rsi < 50
        # Рассчитываем вероятности, используя лямбда-функцию прямо в apply
        _prob_above_50 = state_above_50.rolling(window=self.bayes_period).apply(
            lambda window: np.mean(window) * self.neutral_threshold[window.index[-1]], raw=False
        )
        _prob_below_50 = state_below_50.rolling(window=self.bayes_period).apply(
            lambda window: np.mean(window) * self.neutral_threshold[window.index[-1]], raw=False
        )
        # Normalization
        all_probs_50 = _prob_above_50 + _prob_below_50
        rsi_probs2['prob_above_50'] = _prob_above_50 / all_probs_50
        rsi_probs2['prob_below_50'] =  _prob_below_50 / all_probs_50
        return rsi_probs2


    def __find_rsi_divergences(self, rsi_probs1:pd.DataFrame) -> None:
        # Find local extrema
        price_peaks = self.data['High'].rolling(window=2).apply(np.argmax) == 1
        price_troughs = self.data['Low'].rolling(window=2).apply(np.argmin) == 1
        rsi_peaks = self.rsi.rolling(window=2).apply(np.argmax) == 1
        rsi_troughs = self.rsi.rolling(window=2).apply(np.argmin) == 1
        # Find divergences
        bullish_divergence = (price_troughs & rsi_peaks) & (self.data['High'] < self.data['High'].shift(1)) & (self.rsi > self.rsi.shift(1))
        bearish_divergence = (price_peaks & rsi_troughs) & (self.data['Low'] > self.data['Low'].shift(1)) & (self.rsi < self.rsi.shift(1))
        # Нахождение двойных дивергенций
        double_bullish_divergence = bullish_divergence.rolling(window=2).sum() == 2
        double_bearish_divergence = bearish_divergence.rolling(window=2).sum() == 2
        # Adjust probabilities based on divergences
        weight_confirmed = 0.7
        weight_unconfirmed = 1.0 - weight_confirmed
        weight_strong_confirmed = 0.9
        # Применение скользящего окна и вычисление вероятностей
        _prob_rsi_overbought = self.rsi.rolling(window=self.bayes_period).apply(lambda window: np.mean(window > 80), raw=False)
        _prob_rsi_oversold = self.rsi.rolling(window=self.bayes_period).apply(lambda window: np.mean(window < 20), raw=False)
        _prob_rsi_neutral = self.rsi.rolling(window=self.bayes_period).apply(lambda window: np.mean((window >= 20) & (window <= 80)), raw=False)
        # Adjust probabilities based on divergences
        adjusted_prob_rsi_overbought = self.nz(_prob_rsi_overbought * np.where(
            double_bullish_divergence, weight_strong_confirmed, 
            np.where(bullish_divergence, weight_confirmed, weight_unconfirmed)
        ))
        adjusted_prob_rsi_oversold = self.nz(_prob_rsi_oversold * np.where(
            double_bearish_divergence, weight_strong_confirmed, 
            np.where(bearish_divergence, weight_confirmed, weight_unconfirmed)
        ))
        no_divergence = ~(bullish_divergence | bearish_divergence)
        single_divergence = (bullish_divergence | bearish_divergence) & ~(double_bullish_divergence | double_bearish_divergence)
        adjusted_prob_rsi_neutral = self.nz(_prob_rsi_neutral * np.where(
            no_divergence, weight_strong_confirmed, 
            np.where(single_divergence, weight_confirmed, weight_unconfirmed)
        ))
        #Normalization
        all_probs_rsi = adjusted_prob_rsi_overbought  + adjusted_prob_rsi_oversold + adjusted_prob_rsi_neutral
        rsi_probs1['prob_rsi_neutral'] = adjusted_prob_rsi_neutral / all_probs_rsi
        rsi_probs1['prob_rsi_oversold'] = adjusted_prob_rsi_oversold / all_probs_rsi
        rsi_probs1['prob_rsi_overbought'] = adjusted_prob_rsi_overbought / all_probs_rsi
        return rsi_probs1



# TEST OK
class BayesMacdOscillator(BayesUtils, ABC):
    def __init__(self, data:pd.DataFrame, settings:dict, volatility_coef:pd.Series):
        self.macd_fast, self.macd_slow, self.macd_signal = settings['macd_fast'], settings['macd_slow'], settings['macd_signal']
        self.bayes_period = settings['bayes_period'] #20
        self.vol_coef = volatility_coef
        self.data = data
        BayesUtils.__init__(self)


    def calc_macd(self):
        results = {}
        macd_ind = ta.macd(self.data['Close'], fast=self.macd_fast, slow=self.macd_slow, signal=self.macd_signal,
            talib=True)
        self.macd_line = macd_ind[f'MACD_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}']
        self.macd_signal = macd_ind[f'MACDs_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}']
        self.macd_histogram = self.macd_line - self.macd_signal
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                'probs1': executor.submit(self.__calc_prob_macd_hist),
                'probs2': executor.submit(self.__macd_signals)
            }
            for name, future in futures.items():
                result = future.result()
                results[name] = result
        macd_probs = pd.concat([results['probs1'], results['probs2']], axis=1)
        #self.__combine_hist_probabilities(macd_probs)
        return self.nz_df(macd_probs)


    def __macd_signals(self) -> pd.DataFrame:
        macd_probs1 = pd.DataFrame(index=self.data.index, columns=['prob_fall', 'prob_rise'])
        macd_signals = pd.Series(np.where(self.macd_line > self.macd_signal, 1, np.where(self.macd_line < self.macd_signal, -1, 0)), self.macd_line.index)
        # Инициализация вероятностей и расчет адаптивного alpha
        prob_rise = [0.5]
        prob_fall = [0.5]
        # Обновление вероятностей
        for i in range(1, len(self.vol_coef)):
            signal = macd_signals.iloc[i]
            alpha_value = self.vol_coef.iloc[i]
            updated_prob_rise, updated_prob_fall = self.__update_probabilities_macd(prob_rise[-1], prob_fall[-1], signal, alpha_value)
            prob_rise.append(updated_prob_rise)
            prob_fall.append(updated_prob_fall)  # Вероятности должны суммироваться до 1
        _prob_rise = pd.Series(prob_rise, index=macd_probs1.index)
        _prob_fall = pd.Series(prob_fall, index=macd_probs1.index)
        #Normalization
        all_probs = _prob_fall + _prob_rise 
        macd_probs1['prob_rise'] = _prob_rise / all_probs
        macd_probs1['prob_fall'] = _prob_fall / all_probs
        return macd_probs1


    def __update_probabilities_macd(self, prob_rise, prob_fall, signal, alpha):
        # Экспоненциальное сглаживание
        updated_prob_rise = alpha * prob_rise + (1 - alpha) * (1 if signal == 1 else 0)
        updated_prob_fall = alpha * prob_fall + (1 - alpha) * (1 if signal == -1 else 0)
        return updated_prob_rise, updated_prob_fall


    def __calc_prob_macd_hist(self) -> None:
        macd_probs2 = pd.DataFrame(index=self.data.index, columns=[
            'prob_histogram_above_zero', 'prob_histogram_below_zero',
            'prob_histogram_falling', 'prob_histogram_rising',
            'prob_histogram_strong_falling', 'prob_histogram_strong_rising',
            'prob_histogram_below_zero', 'prob_histogram_above_zero',
            'combined_probability'])
        # Вероятность гистограммы выше/ниже нуля   
        macd_probs2['prob_histogram_above_zero'] = self.macd_histogram.rolling(window=self.bayes_period).apply(lambda x: (x > 0).mean()).iloc[-1]
        macd_probs2['prob_histogram_below_zero'] = self.macd_histogram.rolling(window=self.bayes_period).apply(lambda x: (x < 0).mean()).iloc[-1]
        # Вероятность роста/падения гистограммы за период self.bayes
        histogram_diff = self.macd_histogram.diff()
        macd_probs2['prob_histogram_rising'] = histogram_diff.rolling(window=self.bayes_period).apply(lambda x: (x > 0).mean()).iloc[-1]
        macd_probs2['prob_histogram_falling'] = histogram_diff.rolling(window=self.bayes_period).apply(lambda x: (x < 0).mean()).iloc[-1]
        # Расчет стандартного отклонения изменений гистограммы
        std_histogram_diff = histogram_diff.rolling(window=self.bayes_period).std().iloc[-1]
        # Вероятность сильного роста/падения гистограммы (например, изменение больше одного стандартного отклонения)
        macd_probs2['prob_histogram_strong_rising'] = np.mean(histogram_diff > std_histogram_diff)
        macd_probs2['prob_histogram_strong_falling'] = np.mean(histogram_diff < -std_histogram_diff)
        return macd_probs2


    # КАКАЯ ТО ХУЙНЯ
    def __combine_hist_probabilities(self):
        # Пример весов, подлежащих настройке
        weights = [0.2, 0.3, 0.3, 0.1, 0.1]
        weighted_probs = [
            p * w for p, w in zip(
                [
                    self.macd_probs['prob_histogram_below_zero'], self.macd_probs['prob_histogram_rising'],
                    self.macd_probs['prob_histogram_falling'], self.macd_probs['prob_histogram_strong_rising'],
                    self.macd_probs['prob_histogram_strong_falling']
                    ],
                weights
                )
            ]
        self.macd_probs['combined_probability'] = sum(weighted_probs)


# TEST OK
class BayesBBOscillator(BayesUtils, ABC):
    def __init__(self, data:pd.DataFrame, settings:dict) -> None:
        self.bb_sma_period, self.bb_stddev_mult = settings['bb_sma_period'], settings['bb_stddev_mult'] #20 #2.5
        self.bayes_period = settings['bayes_period'] #20
        self.data = data
        BayesUtils.__init__(self)


    def calc_bb(self) -> pd.DataFrame:
        results_bb = {}
        bbands_ind = ta.bbands(self.data['Close'], self.bb_sma_period, self.bb_stddev_mult, talib=True)
        self.bb_upper = bbands_ind[f'BBU_{self.bb_sma_period}_{self.bb_stddev_mult}']
        self.bb_basis = bbands_ind[f'BBM_{self.bb_sma_period}_{self.bb_stddev_mult}']
        self.bb_lower = bbands_ind[f'BBL_{self.bb_sma_period}_{self.bb_stddev_mult}']
        self.bb_per = bbands_ind[f'BBP_{self.bb_sma_period}_{self.bb_stddev_mult}']
        self.bb_band = bbands_ind[f'BBB_{self.bb_sma_period}_{self.bb_stddev_mult}']
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
            'first': executor.submit(self.__calc_probs_bb),
            'second': executor.submit(self.__calc_percbb_bandwidth)
            }
            for name, future in futures.items():
                result = future.result()
                results_bb[name] = result
        return pd.concat([results_bb['first'], results_bb['second']], axis=1)



    def __calc_probs_bb(self) -> pd.DataFrame:
        # ADD % AND BANDWIDTH ??? +++
        #CALC PROB
        bb_data1 = pd.DataFrame(index=self.data.index, columns=[
            'prob_bb_upper', 'prob_bb_lower', 'prob_bb_basis_up',
            'prob_bb_basis_down', 'prob_up_bb_basis', 'prob_down_bb_basis'
            ])
        bb_data1[:] = np.nan  # Fill with NaN initially
        bb_data1['prob_bb_upper'] = self.data['Close'].rolling(window=self.bayes_period).apply(lambda x: np.sum(x <= self.bb_upper.loc[x.index[-1]]) / self.bayes_period)
        bb_data1['prob_bb_lower'] = self.data['Close'].rolling(window=self.bayes_period).apply(lambda x: np.sum(x >= self.bb_lower.loc[x.index[-1]]) / self.bayes_period)
        bb_data1['prob_bb_basis_up']= self.data['Close'].rolling(window=self.bayes_period).apply(lambda x: np.sum(x > self.bb_basis.loc[x.index[-1]]) / self.bayes_period)
        bb_data1['prob_bb_basis_down'] = self.data['Close'].rolling(window=self.bayes_period).apply(lambda x: np.sum(x <= self.bb_basis.loc[x.index[-1]]) / self.bayes_period)
        bb_data1['prob_up_bb_basis'] = bb_data1.apply(lambda row: (row['prob_bb_basis_up'] / (row['prob_bb_basis_up'] + row['prob_bb_basis_down']) if (row['prob_bb_basis_up'] + row['prob_bb_basis_down']) != 0 else 0), axis=1)
        bb_data1['prob_down_bb_basis'] = bb_data1.apply(lambda row: (row['prob_bb_basis_down'] / (row['prob_bb_basis_down'] + row['prob_bb_basis_up']) if (row['prob_bb_basis_down'] + row['prob_bb_basis_up']) != 0 else 0), axis=1)
        return self.nz_df(bb_data1)
    
    
    def __calc_percbb_bandwidth(self):
        bb_data2 = pd.DataFrame(index=self.data.index, columns=[
            'prob_bbp_overbought', 'prob_bbp_oversold', 'prob_bbp_neutral',
            'prob_bbb_high_vol', 'prob_bbb_low_vol', 'prob_bbb_increasing',
            'prob_bbb_decreasing'])
        bb_data2[:] = np.nan  # Fill with NaN initially
        # Calculate probabylities for every signal
        bb_data2 = bb_data2.assign(prob_bbp_overbought = lambda x: (self.bb_per > 1).rolling(window=self.bayes_period).mean())
        bb_data2 = bb_data2.assign(prob_bbp_oversold = lambda x: (self.bb_per < 0).rolling(window=self.bayes_period).mean())
        bb_data2 = bb_data2.assign(prob_bbp_neutral = lambda x: ((self.bb_per >= 0) & (self.bb_per <= 1)).rolling(window=self.bayes_period).mean())
        bb_data2 = bb_data2.assign(prob_bbb_high_volat = lambda x: (self.bb_band > 0.1).rolling(window=self.bayes_period).mean())
        bb_data2 = bb_data2.assign(prob_bbb_low_volat = lambda x: (self.bb_band <= 0.1).rolling(window=self.bayes_period).mean())
        bb_data2 = bb_data2.assign(prob_bbb_increasing = lambda x: ((self.bb_band.diff() > 0).astype(int)).rolling(window=self.bayes_period).mean())
        bb_data2 = bb_data2.assign(prob_bbb_decreasing = lambda x: ((self.bb_band.diff() < 0).astype(int)).rolling(window=self.bayes_period).mean())
        return self.nz_df(bb_data2)


# TEST OK
class BayesAOACOscillator(BayesUtils, ABC):
    def __init__(self, data:pd.DataFrame, settings:dict, volatility_coef:pd.Series) -> None:
        self.ao_fast, self.ao_slow = settings['ao_fast'], settings['ao_slow']  #5 #34
        self.ac_fast, self.ac_slow = settings['ac_fast'], settings['ac_slow'] #5 #34
        self.ma_ac_ao_period = settings['ma_ac_ao_period'] #13
        self.bayes_period = settings['bayes_period'] #20
        self.volatility_coef = volatility_coef
        self.data = data
        BayesUtils.__init__(self)


    def __calc_ao(self) -> pd.Series:
        return ta.sma(self.data['hl2'], self.ao_fast, True) - ta.sma(self.data['hl2'], self.ao_slow, True)


    def __calc_x_sma1_hl2(self) -> pd.Series:
        return ta.sma(self.data['hl2'], self.ac_fast, True)


    def __calc_x_sma2_hl2(self):
        return ta.sma(self.data['hl2'], self.ac_slow, True)


    def calc_ao_ac(self) -> None:
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                'ao': executor.submit(self.__calc_ao),
                'x_sma1_hl2': executor.submit(self.__calc_x_sma1_hl2),
                'x_sma2_hl2': executor.submit(self.__calc_x_sma2_hl2)
            }
            for name, future in futures.items():
                result = future.result()
                results[name] = result
        self.ao = results['ao']
        x_sma1_sma2 = results['x_sma1_hl2'] - results['x_sma2_hl2']
        x_sma_hl2 = ta.sma(x_sma1_sma2, self.ac_fast, True)
        self.ac = x_sma1_sma2 - x_sma_hl2
        # ACAO VWMA calculation
        self.ac_ao = (self.ac + self.ao) / 2
        pv = self.ac_ao * self.data['Volume']
        self.ma_ac_ao = ta.sma(pv, self.ma_ac_ao_period, True) / ta.sma(self.data['Volume'], self.ma_ac_ao_period, True)
        self.__create_ao_ac_conditions()
        return self.__calc_ac_ao_probs()


    def __create_ao_ac_conditions(self) -> None:
        # AC & AO Conditions
        self.ac_is_blue = self.ac > self.ac.shift(1)  # Use shift for previous values
        self.ac_is_red = ~self.ac_is_blue
        self.ao_is_green = self.ao > self.ao.shift(1)   # Calculate price change for AO
        self.ao_is_red = ~self.ao_is_green
        self.ac_ao_is_bullish = self.ac_is_blue & self.ao_is_green
        self.ac_ao_is_bearish = self.ac_is_red & self.ao_is_red
        self.ac_ao_is_neutral = ~(self.ac_is_blue & self.ao_is_green) & ~(self.ac_is_red & self.ao_is_red)
        self.ac_ao_color_index = pd.Series(np.where(self.ac_ao_is_bullish, 1, np.where(self.ac_ao_is_bearish, -1, 0)), self.ac_ao_is_bearish.index)


    def __calc_ac_ao_probs(self) -> None:
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                'ao': executor.submit(self.__calc_probs_ao),
                'ac_ao': executor.submit(self.__calc_probs_ma_ac_ao)
            }
            for name, future in futures.items():
                result = future.result()
                results[name] = result
        return pd.concat([results['ao'], results['ac_ao']], axis=1)


    def __calc_probs_ma_ac_ao(self):
        probs_ac_ao1 = pd.DataFrame(index = self.data.index, columns = [
            'ac_ao_ma_prob_up', 'ac_ao_ma_prob_down', 'ac_ao_ma_prob_neutral'
        ])
        _ac_ao_ma_prob_up = self.ac_ao_is_bullish.rolling(window=self.bayes_period).mean()
        _ac_ao_ma_prob_down = self.ac_ao_is_bearish.rolling(window=self.bayes_period).mean()
        _ac_ao_ma_prob_neutral = self.ac_ao_is_neutral.rolling(window=self.bayes_period).mean()
        #Normalization
        _sum_probs = self.nz(_ac_ao_ma_prob_up + _ac_ao_ma_prob_down + _ac_ao_ma_prob_neutral)
        probs_ac_ao1['ac_ao_ma_prob_up'] = self.nz(_ac_ao_ma_prob_up / _sum_probs)
        probs_ac_ao1['ac_ao_ma_prob_down'] = self.nz(_ac_ao_ma_prob_down / _sum_probs)
        probs_ac_ao1['ac_ao_ma_prob_neutral'] = self.nz(_ac_ao_ma_prob_neutral / _sum_probs)
        return probs_ac_ao1


    def __calc_probs_ao(self):
        probs_ac_ao2 = pd.DataFrame(index = self.data.index, columns = [
            'prob_ao_positive', 'prob_ao_negative', 'prob_ao_neutral'
        ])
        rolling_window = self.ao.rolling(window=self.bayes_period)
        std_ao = ta.stdev(self.ao, self.bayes_period, talib=True)
        _prob_ao_positive = rolling_window.apply(lambda x: np.sum(x >= std_ao.loc[x.index] * self.volatility_coef.loc[x.index]) / self.bayes_period)
        _prob_ao_negative = rolling_window.apply(lambda x: np.sum(x <= std_ao.loc[x.index] * self.volatility_coef.loc[x.index]) / self.bayes_period)
        _prob_ao_neutral = rolling_window.apply(lambda x: np.sum((x > std_ao.loc[x.index] * self.volatility_coef.loc[x.index]) & (x < std_ao.loc[x.index] * self.volatility_coef.loc[x.index])) / self.bayes_period)
        # Normalization
        sum_probs = self.nz(_prob_ao_positive + _prob_ao_negative + _prob_ao_neutral)
        probs_ac_ao2['prob_ao_positive'] = self.nz(_prob_ao_positive / sum_probs)
        probs_ac_ao2['prob_ao_negative'] = self.nz(_prob_ao_negative / sum_probs)
        probs_ac_ao2['prob_ao_neutral'] = self.nz(_prob_ao_neutral / sum_probs)
        return probs_ac_ao2


# TEST OK
class BayesAlligatorOscillator(BayesUtils, ABC):
    def __init__(self, data:pd.DataFrame, settings:dict):
        self.lips_length, self.teeth_length, self.jaw_length = settings['lips_length'], settings['teeth_length'], settings['jaw_length'] #5 #8 #13
        self.lips_offset, self.teeth_offset, self.jaw_offset = settings['lips_offset'], settings['teeth_offset'], settings['jaw_offset']  #3 #5 #8
        self.bayes_period = settings['bayes_period'] #20
        self.data = data
        BayesUtils.__init__(self)


    def __calc_lips(self) -> None:
        self.lips = ta.smma(self.data['hl2'], self.lips_length, talib=True, offset=self.lips_offset)


    def __calc_teeth(self) -> None:
        self.teeth = ta.smma(self.data['hl2'], self.teeth_length, talib=True, offset=self.teeth_offset)


    def __calc_jaw(self) -> None:
        self.jaw = ta.smma(self.data['hl2'], self.jaw_length, talib=True, offset=self.jaw_offset)


    def calc_alligator(self) -> pd.DataFrame:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(self.__calc_lips),
                executor.submit(self.__calc_teeth),
                executor.submit(self.__calc_jaw)
            ]
            for future in futures:
                    future.result()
        return self.__calc_probs_alligator()


    def __calc_probs_alligator(self) -> pd.DataFrame:
        # Define uptrend and downtrend conditions
        uptrend_condition = (self.teeth > self.lips) & (self.jaw > self.teeth)
        downtrend_condition = (self.jaw < self.teeth) & (self.teeth < self.lips)
        neutral_condition = ~(uptrend_condition | downtrend_condition)
        # Calculate probabilities
        allig_probs = pd.DataFrame(None, self.data.index)
        allig_probs['prob_alligator_uptrend'] = self.nz(uptrend_condition.rolling(window=self.bayes_period).mean())
        allig_probs['prob_alligator_downtrend'] = self.nz(downtrend_condition.rolling(window=self.bayes_period).mean())
        allig_probs['prob_alligator_neutral'] = self.nz(neutral_condition.rolling(window=self.bayes_period).mean())
        # Assessing trend strength
        allig_probs['trend_strength'] = ta.rsi(abs(self.jaw - self.lips) / self.jaw , self.bayes_period, talib=True)
        return allig_probs


# TEST OK
class BayesianADXOscillator(BayesUtils, ABC):
    def __init__(self, data:pd.DataFrame, settings:dict) -> None:
        self.data = data
        self.bayes_period = settings['bayes_period'] #20
        self.adx_length = settings['adx_length'] #14
        self.adx_threshold = settings['adx_triger'] #25
        BayesUtils.__init__(self)


    def calc_adx(self) -> pd.DataFrame:
        adx_probs = pd.DataFrame(index=self.data.index, columns = ['prob_adx_up', 'prob_adx_down', 'prob_adx_neutral'])
        adx = ta.adx(self.data['High'], self.data['Low'], self.data['Close'], length=self.adx_length, talib=True)
        adx_line = adx[f'ADX_{self.adx_length}']
        adx_dmp = adx[f'DMP_{self.adx_length}']
        adx_dmn = adx[f'DMN_{self.adx_length}']
        # Генерируем условия для сигналов
        _prob_adx_strong_trend:pd.Series = adx_line > self.adx_threshold
        _prob_adx_neutral_trend = ~ _prob_adx_strong_trend
        _prob_adx_up = (adx_dmp > adx_dmn).replace(False, pd.NA).ffill().fillna(False).infer_objects(copy=False)
        _prob_adx_down = (adx_dmp < adx_dmn).replace(False, pd.NA).ffill().fillna(False).infer_objects(copy=False)
        prob_adx_up_strong = _prob_adx_up.rolling(window=self.bayes_period).apply(lambda window: np.mean(window) if _prob_adx_strong_trend.loc[window.index[-1]] else 0, raw=False)
        prob_adx_down_strong = _prob_adx_down.rolling(window=self.bayes_period).apply(lambda window: np.mean(window) if _prob_adx_strong_trend.loc[window.index[-1]] else 0, raw=False)
        prob_adx_neutral = _prob_adx_neutral_trend.rolling(window=self.bayes_period).apply(lambda window: np.mean(window), raw=False)
        #Normalization 
        all_probs = prob_adx_up_strong + prob_adx_down_strong + prob_adx_neutral
        adx_probs['prob_adx_up'] = prob_adx_up_strong / all_probs
        adx_probs['probs_adx_down'] = prob_adx_down_strong / all_probs
        adx_probs['probs_adx_neutral'] = prob_adx_neutral / all_probs
        return self.nz_df(adx_probs)


# TEST OK
class BayesMesaAdaptiveMAOscillator(BayesUtils, ABC):
    def __init__(self, data: pd.DataFrame, settings: dict) -> None:
        self.fastlimit:float = settings['mesa_fastlimit'] #0.5
        self.slowlimit:float = settings['mesa_slowlimit'] #0.05
        self.bayes_period:int = settings['bayes_period']
        self.data = data
        BayesUtils.__init__(self)


    def calc_mama(self) -> pd.DataFrame:
        probs_mama = pd.DataFrame(index=self.data.index, columns=['prob_mama_up', 'prob_mama_down'])
        mama_ind = ta.mama(self.data['Close'], fastlimit=self.fastlimit, slowlimit=self.slowlimit, talib=True)
        weight_confirmate:float = 0.6
        weught_unconfirmate:float = 1 - weight_confirmate
        mama = mama_ind[f"MAMA_{self.fastlimit}_{self.slowlimit}"]
        fama = mama_ind[f"FAMA_{self.fastlimit}_{self.slowlimit}"]
        _bullish_cross = (mama > fama) & (mama.shift(1) <= fama.shift(1))
        _bearish_cross = (mama < fama) & (mama.shift(1) >= fama.shift(1))
        _bullish_signal = _bullish_cross.astype(float).replace(0, pd.NA).ffill().bfill().astype(bool)
        _bearish_signal = _bearish_cross.astype(float).replace(0, pd.NA).ffill().bfill().astype(bool)
        _bullish_divergence = (self.data['Close'] < self.data['Close'].rolling(window=self.bayes_period).min()) & (mama > mama.rolling(window=self.bayes_period).min())
        _bearish_divergence = (self.data['Close'] > self.data['Close'].rolling(window=self.bayes_period).max()) & (mama < mama.rolling(window=self.bayes_period).max())
        _prob_up = self.calculate_probabilities_with_divergence(_bullish_signal, _bullish_divergence, weight_confirmate, weught_unconfirmate)
        _prob_down = self.calculate_probabilities_with_divergence(_bearish_signal, _bearish_divergence, weight_confirmate, weught_unconfirmate)
        # Normalization
        all_probs = _prob_up + _prob_down
        probs_mama['prob_mama_up'] = self.nz(_prob_up / all_probs)
        probs_mama['prob_mama_down'] = self.nz(_prob_down / all_probs)
        probs_mama.to_csv('mama_probs.csv', sep='\t', decimal=',', index=True, encoding='utf-8')
        return probs_mama


# TEST OK
class BayesAroonOscilator(BayesUtils, ABC):
    def __init__(self, data:pd.DataFrame, settings:dict) -> None:
        self.length = settings['aroon_length'] #14
        self.bayes_period = settings['bayes_period']
        self.data = data
        BayesUtils.__init__(self)


    def calc_aroon(self) -> pd.DataFrame:
        results = {}
        aroon = ta.aroon(self.data['High'], self.data['Low'], length=self.length, talib=True)
        aroon_u = aroon[f'AROONU_{self.length}']
        aroon_d = aroon[f'AROOND_{self.length}']
        aroon_osc = aroon[f'AROONOSC_{self.length}']
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                'aroon_u_d': executor.submit(self.__calc_probs_aroon_u_d, aroon_u, aroon_d),
                'aroon_osc': executor.submit(self.__calc_probs_aroon_osc, aroon_osc)
            }
            for name, future in futures.items():
                result = future.result()
                results[name] = result
        aroon_probs = pd.concat([results['aroon_u_d'], results['aroon_osc']], axis=1)
        return aroon_probs


    def __calc_probs_aroon_u_d(self, aroon_u:pd.Series, aroon_d:pd.Series) -> pd.DataFrame:
        aroon_probs1 = pd.DataFrame(index=self.data.index, columns=[
            '',
        ])
        _bullish_cross = (aroon_d > aroon_u) & (aroon_d.shift(1) <= aroon_u.shift(1))
        _bearish_cross = (aroon_u > aroon_d) & (aroon_u.shift(1) <= aroon_d.shift(1))
        _bullish_signal = _bullish_cross.ffill() & (aroon_d > aroon_u)
        _bearish_signal = _bearish_cross.ffill() & (aroon_u > aroon_d)
        _bullish_trend = (aroon_u > 30) & (aroon_u < 70)
        _bearish_trend = (aroon_d > 30) & (aroon_d < 70)
        _neutral = (aroon_u < 30) & (aroon_d < 30)
        _strong_uptrend = aroon_u > 70
        _strong_downtrend = aroon_d > 70
        _weak_uptrend = aroon_u < 30
        _weak_downtrend = aroon_d < 30
        _bullish_divergence = (self.data['Low'] < self.data['Low'].shift(1)) & (aroon_u > aroon_u.shift(1))
        _bearish_divergence = (self.data['High'] > self.data['High'].shift(1)) & (aroon_d > aroon_d.shift(1))
        _prob_aroon_up = self.calc_aroon_probs_with_divs(_bullish_signal, _bullish_divergence, _weak_uptrend, _bullish_trend, _strong_uptrend)
        _prob_aroon_down = self.calc_aroon_probs_with_divs(_bearish_signal, _bearish_divergence, _weak_downtrend, _bearish_trend, _strong_downtrend)
        _prob_aroon_neutral = _neutral.rolling(window=self.bayes_period).apply(lambda x: np.sum(x) / self.bayes_period)
        all_probs = _prob_aroon_down  + _prob_aroon_neutral + _prob_aroon_up
        aroon_probs1['prob_aroon_up'] = _prob_aroon_up / all_probs
        aroon_probs1['prob_aroon_down'] = _prob_aroon_down / all_probs
        aroon_probs1['prob_aroon_neutral'] = _prob_aroon_neutral / all_probs
        return aroon_probs1


    def __calc_probs_aroon_osc(self, aroon_osc:pd.Series) -> pd.DataFrame:
        aroon_probs2 = pd.DataFrame(index=self.data.index, columns=['prob_aroon_up_osc', 'prob_aroon_down_osc'])
        weight_confirmed = 0.7
        weight_unconfirmed = 1.0 - weight_confirmed
        _bullish_cross_osc = (aroon_osc> 0) & (aroon_osc.shift(1) <= 0)
        _bearish_cross_osc = (aroon_osc< 0) & (aroon_osc.shift(1) >= 0)
        _bullish_signal = _bullish_cross_osc.ffill() & (aroon_osc > 0)
        _bearish_signal = _bearish_cross_osc.ffill() & (aroon_osc < 0)
        _bullish_divergence_osc = (self.data['Close'] < self.data['Close'].shift(1)) & (aroon_osc> aroon_osc.shift(1))
        _bearish_divergence_osc = (self.data['Close'] > self.data['Close'].shift(1)) & (aroon_osc< aroon_osc.shift(1))
        _prob_aroon_up_osc = self.calculate_probabilities_with_divergence(_bullish_signal, _bullish_divergence_osc, weight_confirmed, weight_unconfirmed)
        _prob_aroon_down_osc = self.calculate_probabilities_with_divergence(_bearish_signal, _bearish_divergence_osc, weight_confirmed, weight_unconfirmed)
        #Normalization
        all_probs = _prob_aroon_down_osc + _prob_aroon_up_osc
        aroon_probs2['prob_aroon_up_osc'] = self.nz(_prob_aroon_up_osc / all_probs)
        aroon_probs2['prob_aroon_down_osc'] = self.nz(_prob_aroon_down_osc / all_probs)
        return aroon_probs2


class BayesianUltimateOscillator(BayesRsiOscillator, BayesMacdOscillator, BayesBBOscillator,
                                 BayesAOACOscillator, BayesAlligatorOscillator, BayesianADXOscillator,
                                 BayesMesaAdaptiveMAOscillator, BayesAroonOscilator):
    def __init__(self, data:pd.DataFrame) -> None:
        settings = ConfigsProvider().load_baes_ultimate_osc_configs()#20 #USE FOR MESA
        self.bayes_period = settings['bayes_period'] #20
        self.data = data
        self.__prepare_data()
        BayesRsiOscillator.__init__(self, data, settings, self.vol_coef)
        BayesMacdOscillator.__init__(self, data, settings, self.vol_coef)
        BayesBBOscillator.__init__(self, data, settings)
        BayesAOACOscillator.__init__(self, data, settings, self.vol_coef)
        BayesAlligatorOscillator.__init__(self, data, settings)
        BayesianADXOscillator.__init__(self, data, settings)
        BayesMesaAdaptiveMAOscillator.__init__(self, data, settings)
        BayesAroonOscilator.__init__(self, data, settings)
        self.logger = create_logger('BayessianUltimateOscillator')


    def __prepare_data(self) -> None:
        self.data['hl2'] = (self.data['High'].values + self.data['Low'].values) / 2
        # Calculate thresold based on ATR
        self.atr = ta.atr(self.data['High'], self.data['Low'], self.data['Close'], length=14, talib=True)
        rsi_atr = ta.rsi(self.atr, 3, talib=True)
        self.vol_coef = rsi_atr / 100


    def create_signals(self) -> pd.DataFrame:
        try:
            self.__prepare_data()
            self.__calculate_in_parallel()
            #self.__calc_bayesians_last()
            #print(f'prime_prob:\n{self.prime_prob}\n\n')
            #self.ac_ao_ma_prob_up.to_csv('data_with_tab_up.csv', sep='\t', decimal=',', index=True, encoding='utf-8')
        except Exception as e:
            self.logger.error(f'{e}')
            raise e


    def __calculate_in_parallel(self) -> None:
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                'rsi': executor.submit(self.calc_rsi),
                'bb': executor.submit(self.calc_bb),
                'ao_ac': executor.submit(self.calc_ao_ac),
                'alligator': executor.submit(self.calc_alligator),
                'macd': executor.submit(self.calc_macd),
                'adx': executor.submit(self.calc_adx),
                'aroon': executor.submit(self.calc_aroon),
                #'mama': executor.submit(self.calc_mama)
            }
            # Ждем завершения всех задач и собираем результаты
            for name, future in futures.items():
                try:
                    result = future.result()
                    results[name] = result
                    print(f"Task {name} completed with result: {result}")
                    self.logger.info(f"Task {name} completed with result: {result}")
                except Exception as e:
                    self.logger.error(f"Task {name} generated an exception: {e}")
        self.__process_results(results)


    def __process_results(self, results:dict):
        for indicator, probs in results.items():
            if not probs.empty:
                setattr(self, f"{indicator}_probs", probs)



    #Всё под нож
    def __calc_bayesians_last(self) -> None:
        # need to add ma_ao_ac probs
        total_rsi_probs = BayesUtils.nz(self.rsi_probs['prob_rsi_overbought'].loc[-1] + self.rsi_probs['prob_rsi_neutral'].loc[-1] + self.rsi_probs['prob_rsi_oversold'].loc[-1])
        prob_rsi_overbought = BayesUtils.nz(self.rsi_probs['prob_rsi_overbought'].loc[-1] / total_rsi_probs)
        prob_rsi_oversold = BayesUtils.nz(self.rsi_probs['prob_rsi_oversold'].loc[-1] / total_rsi_probs)
        prob_rsi_neutral = BayesUtils.nz(self.rsi_probs['prob_rsi_neutral'].loc[-1] / total_rsi_probs)
        # Calculate sigma probabilities (replace with your specific logic)
        sigma_probs_down_bb = BayesUtils.nz((self.data['prob_up_bb_basis'].iloc[-1] * self.prob_ao_positive.iloc[-1]) / 
                                    ((self.data['prob_up_bb_basis'].iloc[-1] * self.prob_ao_positive.iloc[-1]) + 
                                        ((1 - self.data['prob_up_bb_basis'].iloc[-1]) * (1 - self.prob_ao_positive.iloc[-1]))))
        sigma_probs_up_bb = BayesUtils.nz((self.data['prob_bb_upper'].iloc[-1] * self.data['prob_bb_basis_down'].iloc[-1] * self.prob_ao_negative.iloc[-1]) / 
                                    ((self.data['prob_bb_upper'].iloc[-1] * self.data['prob_bb_basis_down'].iloc[-1] * self.prob_ao_negative.iloc[-1]) + 
                                    ((1 - self.data['prob_bb_upper'].iloc[-1]) * (1 - self.data['prob_bb_basis_down'].iloc[-1]) * (1 - self.prob_ao_negative.iloc[-1]))))



#TEST
from api.okx_info import OKXInfoFunctions
from datasets.utils.dataframe_utils import prepare_many_data_to_append_db, create_dataframe
result = OKXInfoFunctions('BTC-USDT-SWAP', '1d', 300).get_market_data(use_class_length=True)
pr_data = prepare_many_data_to_append_db(result)
data = create_dataframe(pr_data)
BayesianUltimateOscillator(data).create_signals()