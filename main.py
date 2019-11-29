import sys
import math
import pandas as pd
from tabula import read_pdf
from collections import Counter


class Processer(object):
    """docstring for Processer"""
    def __init__(self, students, result):
        super(Processer, self).__init__()
        self._students = students
        self._result = result

    def create_roll_map(self):
        roll_map = {}
        for index, row in self._students.iterrows():
            roll_map[row['roll_no']] = {
            'sex': row['sex'],
            'name': row['name'],
            'cgpa': row['cgpa'],
            'hall': row['hall']
            }
        return roll_map

    def get_roll_list(self):
        roll_list = []
        json = read_pdf(self._result, output_format='json')
        json = json[0]
        data = json['data']
        for row in data:
            for col in row:
                roll_list.append(col['text'])
        return roll_list
        
class Analyzer(object):
    """docstring for Analyzer"""
    def __init__(self, roll_map, roll_list, year):
        super(Analyzer, self).__init__()
        self._roll_map = roll_map
        self._roll_list = roll_list
        self._year = year
        final_list_df = pd.DataFrame(self.get_final_list())
        final_list_df['cgpa'] = pd.to_numeric(final_list_df['cgpa'])
        self._final_list = final_list_df

    def get_final_list(self):
        final_list = []
        for roll in self._roll_list:
            roll_info = self._roll_map[roll]
            final_list.append({
            'roll_no': roll,
            'sex': roll_info['sex'],
            'name': roll_info['name'],
            'cgpa': roll_info['cgpa'],
            'hall': roll_info['hall']
            })
        return final_list

    def get_statistics(self):
        statistics = {}
        statistics['cgpa_max'] = self._final_list['cgpa'].max()
        statistics['cgpa_min'] = self._final_list['cgpa'].min()
        statistics['cgpa_avg'] = self._final_list['cgpa'].mean()
        statistics['batch_list'] = dict(Counter([self._year-int(roll[:2]) for roll in self._final_list['roll_no']]))
        try:
            statistics['batch_list']['btech'] = statistics['batch_list'].pop(3)
        except:
            statistics['batch_list']['btech'] = 0
        try:
            statistics['batch_list']['dual'] = statistics['batch_list'].pop(4)
        except:
            statistics['batch_list']['dual'] = 0
        try:
            statistics['batch_list']['mtech'] = statistics['batch_list'].pop(1)
        except:
            statistics['batch_list']['mtech'] = 0
        statistics['dep_list'] = dict(Counter([roll[2:4] for roll in self._final_list['roll_no']]))
        statistics['hall_list'] = dict(Counter(list(self._final_list['hall'])))
        statistics['sex_list'] = dict(Counter(list(self._final_list['sex'])))
        return statistics


students = pd.read_csv('students.csv', names=['roll_no', 'sex', 'name', 'cgpa', 'hall'])
result = sys.argv[1]
placements_year = 19

processer = Processer(students=students, result=result)
roll_map = processer.create_roll_map()
roll_list = processer.get_roll_list()

analyzer = Analyzer(roll_map=roll_map, roll_list=roll_list, year=placements_year)
statistics = analyzer.get_statistics()