from abc import ABC, abstractmethod

import pandas as pd 
from pandas import DataFrame


class BaseDataFrameLoader(ABC):
    
    @abstractmethod
    def load(self,file_path:str)->DataFrame:
        pass
    
class CSVDataframeLoader(BaseDataFrameLoader):
    
    def __init__(self,sep):
        self.__sep = sep
    
    def load(self, file_path: str) -> DataFrame:
        return pd.read_csv(filepath_or_buffer=file_path, sep=self.__sep)
 