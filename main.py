import pandas as pd
from tabula import read_pdf
from collections import Counter
from prettytable import PrettyTable
from argparse import ArgumentParser

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
        json_list = read_pdf(result, multiple_tables=False, output_format='json', pages="all")
        for json in json_list:
            data = json['data']
            for row in data:
                for col in row:
                    if col['text'] != '':
                        roll_list.append(col['text'])
        return roll_list
        
class Analyzer(object):
    """docstring for Analyzer"""
    def __init__(self, roll_map, roll_list, year, friends):
        super(Analyzer, self).__init__()
        self._roll_map = roll_map
        self._roll_list = roll_list
        self._year = year
        self._friends = friends
        self._final_rolls, self._missing_rolls = self.get_final_list()
        final_list_df = pd.DataFrame(self._final_rolls)
        final_list_df['cgpa'] = pd.to_numeric(final_list_df['cgpa'])
        self._final_list = final_list_df
        self._valid_rolls = self.validate_rolls()
        friends_list = self.get_friends()

        print("\nTotal number of students : ", final_list_df.shape[0]+len(self._valid_rolls))
        print("Missing students : ", len(self._valid_rolls))
        print(self._valid_rolls)
        print("\n")
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(final_list_df.to_string(index=False))
        print("\n")

    def get_friends(self):
        friends_list = []
        for roll in self._friends:
            try:
                if roll in self._roll_list:
                    friends_list.append([roll, self._roll_map[roll]['name']])
            except:
                pass
        return friends_list

    def validate_rolls(self):
        valid_rolls = []
        for roll in self._missing_rolls:
            if len(roll) != 9:
                pass
            elif roll[:2].isdigit():
                if int(roll[:2]) < self._year:
                    valid_rolls.append(roll)
        return valid_rolls

    def get_final_list(self):
        final_list = []
        missing_rolls = []
        for roll in self._roll_list:
            try:
                roll_info = self._roll_map[roll]
                final_list.append({
                'roll_no': roll,
                'sex': roll_info['sex'],
                'name': roll_info['name'],
                'cgpa': roll_info['cgpa'],
                'hall': roll_info['hall']
                })
            except:
                missing_rolls.append(roll)
        return final_list, missing_rolls

    def get_statistics(self):
        statistics = {}
        statistics['cgpa_max'] = self._final_list['cgpa'].max()
        statistics['cgpa_min'] = self._final_list['cgpa'].min()
        statistics['cgpa_avg'] = self._final_list['cgpa'].mean()
        statistics['batch_list'] = dict(Counter([self._year-int(roll[:2]) for roll in list(self._final_list['roll_no'])+self._valid_rolls]))

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
        try:
            del statistics['hall_list']['Na']
        except:
            pass
        statistics['sex_list'] = dict(Counter(list(self._final_list['sex'])))
        try:
            statistics['sex_list']['M']
        except:
            statistics['sex_list']['M'] = 0
        try:
            statistics['sex_list']['F']
        except:
            statistics['sex_list']['F'] = 0
        return statistics


argparser = ArgumentParser()
argparser.add_argument("--file", type=str, default='test.pdf')
argparser.add_argument("--friends", type=str, default='friends.txt')
argparser.add_argument("--year", type=int, default=19)
args = argparser.parse_args()

result = args.file
friends = args.friends
placements_year = args.year

students_df = pd.read_csv('students.csv', names=['roll_no', 'sex', 'name', 'cgpa', 'hall'])
friends_df = pd.read_csv(friends, header=None)
friends_list = list(friends_df[0].values)

processer = Processer(students=students_df, result=result)
roll_map = processer.create_roll_map()
roll_list = processer.get_roll_list()

analyzer = Analyzer(roll_map=roll_map, roll_list=roll_list, year=placements_year, friends=friends_list)
statistics = analyzer.get_statistics()
friends = analyzer.get_friends()

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
table4 = PrettyTable()
table4.field_names = ["SEX", "Numbers", "Percent"]
sex_total = sum(list(statistics['sex_list'].values()))
for key in statistics['sex_list'].keys():
    value = statistics['sex_list'][key]
    table4.add_row([key, value, round(float(value)/sex_total*100, 1)])
print(table4)

if len(friends)!=0 :
    print("\nFriends in the list : \n")
    for friend in friends:
        print(friend[0], friend[1])
else:
    print("\nNo friends in the list! \n")
print("\n")


fig = plt.figure(figsize=(56,32))

ax=plt.subplot(2,2,1) 
labels = ['Male ('+str(statistics['sex_list']['M'])+')', 'Female ('+str(statistics['sex_list']['F'])+')']
sizes = [statistics['sex_list']['M'], statistics['sex_list']['F']]
ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['#ff580f', '#ff9c59', '#ffc99d'], shadow=False, startangle=90)
ax.axis('equal')

ax=plt.subplot(2,2,2) 
labels = ['B.Tech ('+str(statistics['batch_list']['btech'])+')', 'Dual ('+str(statistics['batch_list']['dual'])+')', 'M.Tech ('+str(statistics['batch_list']['mtech'])+')']
sizes = [statistics['batch_list']['btech'], statistics['batch_list']['dual'], statistics['batch_list']['mtech']]
ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['#ff580f', '#ff9c59', '#ffc99d'], shadow=False, startangle=90)
ax.axis('equal')

ax=plt.subplot(2,2,3) 
labels = list(statistics['dep_list'].keys())
sizes = [statistics['dep_list'][key] for key in statistics['dep_list'].keys()]
ax.bar(labels, sizes, color='#ff7e26')
for index, data in enumerate(sizes):
    ax.text(x=index, y=data+max(sizes)*0.02, s=data, horizontalalignment='center', fontdict=dict(fontsize=9))
ax.tick_params(axis='both', which='major', colors='k', labelsize=8)
ax.set_ylim([0, max(sizes)*1.1])
ax.yaxis.set_visible(False)

ax=plt.subplot(2,2,4) 
labels = list(statistics['hall_list'].keys())
sizes = [statistics['hall_list'][key] for key in statistics['hall_list'].keys()]
ax.bar(labels, sizes, color='#ff7e26')
for index, data in enumerate(sizes):
    ax.text(x=index, y=data+max(sizes)*0.02, s=data, horizontalalignment='center', fontdict=dict(fontsize=9))
ax.tick_params(axis='both', which='major', colors='k', labelsize=8)
ax.set_ylim([0, max(sizes)*1.1])
ax.yaxis.set_visible(False)

plt.show()