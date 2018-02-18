from geopy.distance import vincenty
from netCDF4 import Dataset
from datetime import datetime, timedelta
from sklearn.neighbors import KNeighborsRegressor
from itertools import product
from math import floor, ceil


class IndexPredictor:
    """Predicts the positional indices of the weather file given the latitude and longitude.
    """

    def __init__(self, lats, longs, index_1_reg=None, index_2_reg=None):
        """Creates a new IndexPredictor using the given latitude and longitude 2D arrays.

        :param lats: Array from indices to latitudes
        :param longs: Array from indices to longitudes
        """
        self._v = vincenty()
        self._lat = lats
        self._lon = longs

        x = None
        if index_1_reg is not None:
            self.index_1_reg = index_1_reg
        else:
            x = [(lats[i, j], longs[i, j]) for i, j in product(range(lats.shape[0]), range(lats.shape[1]))]
            index_1_y = [i for i, j in product(range(lats.shape[0]), range(lats.shape[1]))]
            self.index_1_reg = KNeighborsRegressor(n_neighbors=1, metric=self._v.measure)
            self.index_1_reg.fit(x, index_1_y)
        if index_2_reg is not None:
            self.index_2_reg = index_2_reg
        else:
            if x is None:
                x = [(lats[i, j], longs[i, j]) for i, j in product(range(lats.shape[0]), range(lats.shape[1]))]
            index_2_y = [j for i, j in product(range(lats.shape[0]), range(lats.shape[1]))]
            self.index_2_reg = KNeighborsRegressor(n_neighbors=1, metric=self._v.measure)
            self.index_2_reg.fit(x, index_2_y)

    def predict(self, x, n: int=5):
        """Predicts the indices of the given latitudes and longitudes.

        :param x: Array of latitude, longitude pairs.
        :param n: Local search range. Increasing it will increase accuracy but will take longer.
        :return:
        """
        return [self._search_neighborhood(int(i), int(j), n, loc[0], loc[1])
                for i, j, loc in zip(self.index_1_reg.predict(x), self.index_2_reg.predict(x), x)]

    def _valid_index(self, i: int, j: int):
        return 0 <= i < self._lat.shape[0] and 0 <= j < self._lat.shape[1]

    def _search_neighborhood(self, i: int, j: int, n: int, lat: float, lon: float):
        cutoff = 70
        best = (i, j)
        best_dist = self._v.measure((self._lat[i, j], self._lon[i, j]), (lat, lon))
        for di in range(-n, n + 1):
            for dj in range(-n, n + 1):
                i_new = i + di
                j_new = j + dj
                if self._valid_index(i_new, j_new):
                    dist = self._v.measure((self._lat[i_new, j_new], self._lon[i_new, j_new]), (lat, lon))
                    if dist < best_dist:
                        best = (i_new, j_new)
                        best_dist = dist
        if best_dist > cutoff:
            return None
        return best


class WeatherModel:
    """Wrapper class for weather file.
    """

    def __init__(self, tke: Dataset, uwnd: Dataset, vwnd: Dataset, hgt: Dataset, index_predictor: IndexPredictor=None):
        """Creates a new WeatherModel with the given file that returns the given attribute.

        :param file: File to return the data from.
        """
        self._start_date = datetime(year=1800, month=1, day=1, hour=0, minute=0, second=0)
        self._tke = tke
        self._uwnd = uwnd
        self._vwnd = vwnd
        self._hgt = hgt
        self._min_time = self._start_date + timedelta(hours=self._tke['time'].actual_range[0])
        self._max_time = self._start_date + timedelta(hours=self._tke['time'].actual_range[1])
        self._max_level, self._min_level = self._tke['level'].actual_range
        if index_predictor is None:
            self._index_predictor = IndexPredictor(self._tke['lat'], self._tke['lon'])
        else:
            self._index_predictor = index_predictor

    def get_weather(self, lat: float, lon: float, height: float, time: datetime):
        """Returns the given attribute at the given coordinates, which may be interpolated from multiple values.

        :param lat: Latitude of value to return.
        :param lon: Longitude of value to return.
        :param height: Height in meters.
        :param time: Time of value to return.
        :return: tke, uwnd and vwnd at the given coordinates.
        """
        lat = (lat + 90) % 180 - 90
        lon = (lon + 180) % 360 - 180

        if time < self._min_time or time > self._max_time:
            return None
        indices = self._index_predictor.predict([(lat, lon)])[0]
        if indices is None:
            return None
        i, j = indices

        start_time = self._start_date + timedelta(hours=self._tke['time'][0])
        end_time = self._start_date + timedelta(hours=self._tke['time'][-1])
        time_ind_exact = (self._tke['time'].shape[0] - 1) * (time - start_time).total_seconds() \
                         / (end_time - start_time).total_seconds()
        time_ind_low = floor(time_ind_exact)
        time_ind_high = ceil(time_ind_exact)
        time_ind_coeff_1 = 1 if time_ind_low == time_ind_high else float(time_ind_exact - time_ind_low) \
                                                                   / float(time_ind_high - time_ind_low)
        time_ind_coeff_2 = 1 - time_ind_coeff_1

        hgt_min = min(self._hgt['hgt'][time_ind_low, 0, i, j], self._hgt['hgt'][time_ind_high, 0, i, j])
        hgt_max = max(self._hgt['hgt'][time_ind_low, -1, i, j], self._hgt['hgt'][time_ind_high, -1, i, j])

        if height > hgt_max or height < hgt_min:
            return None

        height_ind_high = -1
        height_ind_low = -1
        for l in range(self._hgt['hgt'].shape[1]):
            if self._hgt['hgt'][time_ind_low, l, i, j] > height:
                height_ind_high = l + 1
                height_ind_low = l
                break

        level_slope = self._hgt['hgt'][time_ind_low, height_ind_high, i, j] -\
            self._hgt['hgt'][time_ind_low, height_ind_low, i, j]
        level_ind_exact = float((height - self._hgt['hgt'][time_ind_low, height_ind_low, i, j])) / level_slope
        level_ind_low = floor(level_ind_exact)
        level_ind_high = ceil(level_ind_exact)
        level_ind_coeff_1 = 1 if level_ind_low == level_ind_high else float(level_ind_exact - level_ind_low)\
            / float(level_ind_high - level_ind_low)
        level_ind_coeff_2 = 1 - level_ind_coeff_1

        """
        level_ind_exact = float((self._tke['level'].shape[0] - 1) * (level - self._tke['level'][0]))\
            / float((self._tke['level'][self._tke['level'].shape[0] - 1] - self._tke['level'][0]))
        level_ind_low = floor(level_ind_exact)
        level_ind_high = ceil(level_ind_exact)
        level_ind_coeff_1 = 1 if level_ind_low == level_ind_high else float(level_ind_exact - level_ind_low)\
            / float(level_ind_high - level_ind_low)
        level_ind_coeff_2 = 1 - level_ind_coeff_1
        """

        tke = level_ind_coeff_1 * time_ind_coeff_1 * self._tke['tke'][time_ind_low, level_ind_low, i, j]\
               + level_ind_coeff_1 * time_ind_coeff_2 * self._tke['tke'][time_ind_high, level_ind_low, i, j]\
               + level_ind_coeff_2 * time_ind_coeff_1 * self._tke['tke'][time_ind_low, level_ind_high, i, j]\
               + level_ind_coeff_2 * time_ind_coeff_2 * self._tke['tke'][time_ind_high, level_ind_high, i, j]
        uwnd = level_ind_coeff_1 * time_ind_coeff_1 * self._uwnd['uwnd'][time_ind_low, level_ind_low, i, j] \
              + level_ind_coeff_1 * time_ind_coeff_2 * self._uwnd['uwnd'][time_ind_high, level_ind_low, i, j] \
              + level_ind_coeff_2 * time_ind_coeff_1 * self._uwnd['uwnd'][time_ind_low, level_ind_high, i, j] \
              + level_ind_coeff_2 * time_ind_coeff_2 * self._uwnd['uwnd'][time_ind_high, level_ind_high, i, j]
        vwnd = level_ind_coeff_1 * time_ind_coeff_1 * self._vwnd['vwnd'][time_ind_low, level_ind_low, i, j] \
              + level_ind_coeff_1 * time_ind_coeff_2 * self._vwnd['vwnd'][time_ind_high, level_ind_low, i, j] \
              + level_ind_coeff_2 * time_ind_coeff_1 * self._vwnd['vwnd'][time_ind_low, level_ind_high, i, j] \
              + level_ind_coeff_2 * time_ind_coeff_2 * self._vwnd['vwnd'][time_ind_high, level_ind_high, i, j]

        return tke, uwnd, vwnd
