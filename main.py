import sys
import pandas as pd
from tabula import read_pdf


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
            'sex' : row['sex'],
            'name' : row['name'],
            'cgpa' : row['cgpa']
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
    def __init__(self, roll_map, roll_list):
        super(Analyzer, self).__init__()
        self._roll_map = roll_map
        self._roll_list = roll_list


students = pd.read_csv('students.csv', names=['roll_no', 'sex', 'name', 'cgpa'])
result = sys.argv[1]

processer = Processer(students=students, result=result)
roll_map = processer.create_roll_map()
roll_list = processer.get_roll_list()

analyzer = Analyzer(roll_map=roll_map, roll_list=roll_list)
