from datetime import datetime
import os
import numpy as np
from dataframe_loader import CSVDataframeLoader
from frame_parser import GPActivityParser, RoomActivityParser
from dataframe_saver import CSVDataFrameSaver, XMLDataFrameSaver, ExcelDataFrameSaver, HTMLDataFrameSaver
import easygui
import matplotlib.pyplot as plt

from validator import Validator


class App:

    TIP = 'Введите q чтобы прекратить работу'
    FILE_TIP_TEXT = 'Выберете файл' 
    DATE_TIP_TEXT = ('Выберети начальную и конечную даты, и файл для парса, \n'
                     'или оставтьте пустыми, тогда возьмутся даты из файла')
    DATE_ERROR = 'Неверная дата формат гггг-мм-дд'

    MENU_CHOICE = ('0: выгрузить таблицу по корпсум\n'
                   '1: показать график по комнатам')

    MENU_ERROR = 'Неверыйн выбор'

    TABLE_SAVE_FORMAT = ('Выберите формат выгрузки\n'
                         '0: csv\n'
                         '1: xlsx\n'
                         '2: xml\n'
                         '3: html\n')

    def __init__(self) -> None:
        self.__run = False
        self.__sep = '\t'
    
    def __choice_saver(self , s):
        if s== '0':
            CSVDataFrameSaver(self.__sep).save(self._path('f.csv'),self.__df)
        elif s == '1':
            ExcelDataFrameSaver(self.__input('Введите название листа')).save(self._path('f.xlsx'),self.__df),
        elif s == '2':
            XMLDataFrameSaver().save(self._path('f.xml') ,self.__df)
        else:
            HTMLDataFrameSaver().save(self._path('f.html'),self.__df)
        

    
    def _path(self,name):
        return os.path.join(self.__input('путь до дериктории'),self.__input('имя файла'))

    def run(self):
        self.__run = True
        self.__print_tip(self.TIP)
        self.__print_tip(self.FILE_TIP_TEXT)
        input_file = easygui.fileopenbox(
            default="\\*.csv", filetypes=["\\*.csv"])
        self.__df = CSVDataframeLoader(self.__sep).load(input_file)
        self.__print_tip(self.DATE_TIP_TEXT)
        self.__start_date = self.__input_date('Дата начала')
        self.__end_date = self.__input_date('Дата конца')
        self.__show_menu()
        

    def __print_tip(self, tip):
        print(tip)

    def __show_menu(self):
        self.__print_tip(self.MENU_CHOICE)
        while self.__run:
            choice = self.__input()
            if self.__is_valid_op_choice(choice):
                if choice == '0':
                    self.__save_table()
                else:
                    self.__show_graphic()
                    

    def __save_table(self):
        self.__print_tip(self.TABLE_SAVE_FORMAT)
        while self.__run:
            choice = self.__input()
            if self.__is_valid_saver_choice(choice):
                self.__df = GPActivityParser().parse(self.__df,self.__start_date,self.__end_date)
                self.__choice_saver(choice)
                self.__run = False
                
    def __show_graphic(self):
        self.__df = RoomActivityParser().parse(self.__df,self.__start_date,self.__end_date)
        fig, ax = plt.subplots()
        for room_count in self.__df['Комнат'].unique():
            room_data = self.__df[self.__df['Комнат'] == room_count]
            ax.plot(room_data['Дата'], room_data['Кол-во активных квартир'],
                    label=f'{room_count} комнат')
        ax.set_title('Описывает зависимость популярности от кол-во комнат в каждый месяц',fontsize=9)
        ax.set_xlabel('Месяц', fontsize=9)
        ax.set_ylabel('Количество объявленйи', fontsize=12)
        for tick in ax.get_xticklabels():
            tick.set_rotation(30)
            tick.set_fontsize(6)

        ax.legend()
        plt.show()
        pass
        

    def __input(self, input_text=None):
        val = input('' if input_text is None else input_text + ': ')
        if val == 'q':
            self.__run = False
        else:
            return val

    def __is_valid_saver_choice(self, choice):
        return choice in ['0', '1', '2', '3']

    def __is_valid_op_choice(self, choice):
        return choice in ['0', '1']

    def __input_date(self, input_text) -> datetime:
        while self.__run:
            date = self.__input(input_text)
            if self.__valid_date(date):
                return self._parse_date(date)

    def __valid_date(self, text: str) -> bool:
        return Validator.try_parse_date(text) or text == ''

    def _parse_date(self, text: str):
        if text == '':
            return None
        return Validator.try_parse_date(text)


if __name__ == '__main__':
    App().run()

