import gspread
from db import get_schudle_for_gspread
import datetime

group_input = str(input("Введите группу: "))
gc = gspread.service_account(filename="cred.json")
sh = gc.open("study")
sh.values_clear("A1:N30")

all_data = get_schudle_for_gspread(group_input)

dict_sorted = {"Нечет": {
                            "Понедельник": [],
                            "Вторник": [],
                            "Среда": [],
                            "Четверг": [],
                            "Пятница": [],
                            "Суббота": []
},
                "Чет": {
                            "Понедельник": [],
                            "Вторник": [],
                            "Среда": [],
                            "Четверг": [],
                            "Пятница": [],
                            "Суббота": []

}}


for one_data in all_data:
    dict_sorted[one_data[6]][one_data[7]].append(f"{one_data[2]}/{one_data[3]}/{one_data[4]}")



for index, value in enumerate(dict_sorted.items()):
    if index == 0:
        sh.values_update("A1", params={'valueInputOption': 'RAW'}, body={'values': [[value[0]]]})
        for enum, days in enumerate(value[1]):
            list_cell = ["A", "B", "C", "D", "E", "F", "G"]
            sh.values_update(f"{list_cell[enum]}2", params={'valueInputOption': 'RAW'}, body={'values': [[days]]})
            if value[1][days] == []:
                continue
            else:
                k = 3
                for less in value[1][days]:
                    sh.values_update(f'{list_cell[enum]}{str(k)}', params={'valueInputOption': 'RAW'}, body={'values': [[less]]})
                    k += 1

    else:
        sh.values_update("H1", params={'valueInputOption': 'RAW'}, body={'values': [[value[0]]]})
        for enum, days in enumerate(value[1]):
            list_cell = ["H", "I", "J", "K", "L", "M", "N"]
            sh.values_update(f"{list_cell[enum]}2", params={'valueInputOption': 'RAW'}, body={'values': [[days]]})
            if value[1][days] == []:
                continue
            else:
                k = 3
                for less in value[1][days]:
                    sh.values_update(f'{list_cell[enum]}{str(k)}', params={'valueInputOption': 'RAW'}, body={'values': [[less]]})
                    k += 1
pass