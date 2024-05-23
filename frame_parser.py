from abc import ABC, abstractmethod
import re
from typing import Any, Callable, Generator
from pandas import DataFrame
import pandas as pd
import datetime
from pandas.arrays import PeriodArray


class BaseDateIntervalParser(ABC):

    @abstractmethod
    def parse(self, dataframe, start_date=None, end_date=None) -> DataFrame:
        pass

    def _try_transform_string_column_to_date(self, dataframe: DataFrame, col_name: str):
        df = dataframe
        df[col_name] = df[col_name].apply(self._date_from_string)
        return df

    def _date_from_string(self, value):
        date_format = '%Y-%m-%d'
        pattern = r'[12]\d{3}-[01]\d-[0-3]\d'
        return datetime.datetime.strptime(re.search(pattern, str(value))[0], date_format)

    def _groupby_with_value_converter(self,
                                      dataframe: DataFrame,
                                      filed: str,
                                      converter: Callable[[Any], Any],
                                      replace_col: bool = False,
                                      additinal_name='_'):
        new_name = filed + ('' if replace_col else additinal_name)
        dataframe_copy = dataframe.copy()
        dataframe_copy[new_name] = dataframe_copy[filed].apply(converter)
        return dataframe_copy.groupby(new_name)


class GPActivityParser(BaseDateIntervalParser):

    def parse(self, dataframe, start_date=None, end_date=None):
        dataframe_with_date = self._try_transform_string_column_to_date(
            dataframe, 'actualized_at')
        if start_date is None or end_date is None:
            start_date = dataframe_with_date['actualized_at'].min()
            end_date = dataframe_with_date['actualized_at'].max()
        result = pd.concat([self.__dataframe_by_date(dataframe_with_date, day)
                           for day in pd.date_range(start_date, end_date, freq='D')])
        return DataFrame({'Дата': result['date'], 'Корпус': result['address_'], 'Кол-во активных квартир': result['count']})

    def __dataframe_by_date(self, dataframe: DataFrame, day: datetime.datetime):
        df = dataframe
        df[df['actualized_at'] >= day]
        address_groups = self._groupby_with_value_converter(
            df, 'address', self.__address_convert)
        result = address_groups.size().reset_index(name='count')
        result['date'] = day
        return result

    def __address_convert(self, value: str):
        waste_info = r'\,?\s+(подъезд|квартира).+'
        return re.sub(waste_info, '', str(value))

    def _iterate_days(self, start_date, end_date) -> Generator[datetime.datetime, None, None]:
        current_date = start_date
        while current_date <= end_date:
            yield current_date
            current_date += datetime.timedelta(days=1)


class RoomActivityParser(BaseDateIntervalParser):

    MONTH = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
             'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

    def parse(self, dataframe, start_date=None, end_date=None) -> DataFrame:
        dataframe_with_date = self._try_transform_string_column_to_date(
            dataframe, 'actualized_at')
        if start_date is None or end_date is None:
            start_date = dataframe_with_date['actualized_at'].min()
            end_date = dataframe_with_date['actualized_at'].max()
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        months = date_range.to_series().dt.to_period('M').unique().tolist()
        result = pd.concat([self.__dataframe_by_month(
            dataframe_with_date, month) for month in months])
        return DataFrame({'Дата': result['month'], 'Комнат': result['room_count'], 'Кол-во активных квартир': result['count']})

    def __dataframe_by_month(self, dataframe: DataFrame, month: PeriodArray):
        df = dataframe
        start_date = month.to_timestamp().to_datetime64()
        end_date = (month.to_timestamp() +
                    pd.offsets.MonthEnd(0)).to_datetime64()
        df_by_interval = df.loc[(df['actualized_at'] > start_date) & (
            df['actualized_at'] <= end_date)]
        room_groups = df_by_interval.groupby('room_count')
        result = room_groups.size().reset_index(name='count')
        result['month'] = f'{self.__month_str(month.to_timestamp().month)} {str(month.to_timestamp().year)}'
        return result

    def __month_str(self, index: int):
        return self.MONTH[index - 1]
