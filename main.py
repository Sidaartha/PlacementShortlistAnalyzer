import sys
import pandas as pd
from tabula import read_pdf
from collections import Counter
from prettytable import PrettyTable

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
plt.style.use('ggplot')

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

        print("\nTotal number of students : ", final_list_df.shape[0])
        print("\n")
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(final_list_df.to_string(index=False))
        print("\n")

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

print("----- STATISTICS -----\n")
table1 = PrettyTable()
table1.field_names = ["Metrics", "Values"]
table1.add_row(["Max CGPA", round(statistics['cgpa_max'], 2)])
table1.add_row(["Min CGPA", round(statistics['cgpa_min'], 2)])
table1.add_row(["Avg CGPA", round(statistics['cgpa_avg'], 2)])
table1.add_row(["B.Tech", statistics['batch_list']['btech']])
table1.add_row(["Dual", statistics['batch_list']['dual']])
table1.add_row(["M.Tech", statistics['batch_list']['mtech']])
print(table1)

print("\n---- DEPARTMENTS ----\n")
table2 = PrettyTable()
table2.field_names = ["Department", "Numbers", "Percent"]
dep_total = sum(list(statistics['dep_list'].values()))
for key in statistics['dep_list'].keys():
    value = statistics['dep_list'][key]
    table2.add_row([key, value, round(float(value)/dep_total*100, 1)])
print(table2)

print("\n------- HALL -------\n")
table3 = PrettyTable()
table3.field_names = ["Hall", "Numbers", "Percent"]
hall_total = sum(list(statistics['hall_list'].values()))
for key in statistics['hall_list'].keys():
    value = statistics['hall_list'][key]
    table3.add_row([key, value, round(float(value)/hall_total*100, 1)])
print(table3)

print("\n------- GENDER -------\n")
table3 = PrettyTable()
table3.field_names = ["SEX", "Numbers", "Percent"]
sex_total = sum(list(statistics['sex_list'].values()))
for key in statistics['sex_list'].keys():
    value = statistics['sex_list'][key]
    table3.add_row([key, value, round(float(value)/sex_total*100, 1)])
print(table3)

# df=pd.DataFrame([[1, 2], [3, 4], [4, 3], [2, 3]])
# fig = plt.figure(figsize=(14,8))
# for i in df.columns:
#     ax=plt.subplot(2,2,i+1) 
#     df[[i]].plot(ax=ax)
# plt.show()