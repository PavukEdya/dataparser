from abc import ABC, abstractmethod
from pandas import DataFrame


class BaseDataFrameSaver(ABC):

    @abstractmethod
    def save(self, file_path: str, dataframe: DataFrame):
        pass


class CSVDataFrameSaver(BaseDataFrameSaver):

    def __init__(self, sep: str):
        self.__sep = sep

    def save(self, file_path: str, dataframe: DataFrame):
        dataframe.to_csv(file_path.replace('\\','\\\\'), sep=self.__sep)


class ExcelDataFrameSaver(BaseDataFrameSaver):

    def __init__(self, sheet_name):
        self.__sheet_name = sheet_name

    def save(self, file_path: str, dataframe: DataFrame):
        dataframe.to_excel(file_path, self.__sheet_name)


class XMLDataFrameSaver(BaseDataFrameSaver):

    def save(self, file_path: str, dataframe: DataFrame):
        dataframe.to_xml(file_path)


class HTMLDataFrameSaver(BaseDataFrameSaver):
    
    def save(self, file_path: str, dataframe: DataFrame):
        dataframe.to_html(file_path)
