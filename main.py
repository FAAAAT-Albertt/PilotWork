import tkinter as tk
from tkinter import messagebox
import math
import copy
from db import select_groups, select_disciplines, select_coaches, update_disciplines, select_hours_week_couple, insert_schudle, select_faculty_schudle, select_weeks_less
import random

direction_id = str(input("Введите ID: "))

weeks_per_semester = select_weeks_less(direction_id)
# сколько часов каждой дисциплины в неделю
occupied_teachers = {day: [] for day in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]}

# кол-во занятий и их видов, которые нужно выработать за 2 недели
hours_per_week = {}
hours_per_semester = select_disciplines(direction_id)
for discipline, data in hours_per_semester.items():
    hours_per_week[discipline] = {vid: round(data_vid[0] / weeks_per_semester) for vid, data_vid in data.items() if "" not in data_vid}

pass
# среднее кол-во пар в день
def average_lessons():

    teatchers = select_coaches(direction_id)
    less_week = 0
    summ_days = 0
    sum_state_couple = 0
    for data in teatchers.values():
        if data[2][0] == None:
            summ_days += 6
            continue

        elif "," in data[2][0]:
            data[2] = data[2][0].split(",")
            summ_days += (6 - len(data[2]))

        else:
            summ_days += (6 - len(data[2]))

    for quantity in hours_per_week.values():
        for nums in quantity.values():
            less_week += nums

    average_less_week = round(round(less_week / round(summ_days / len(teatchers))) / 2)

    return average_less_week


def check_qniq(group, day, classes, count, view, room, groups_occupied):

    mas_check = []
    # получение индекса нужной группы
    count_interval = 0
    for key in groups_occupied.keys():
        if key == group:
            break

        else:
            count_interval += 1

    count_check = 0
    for key, data in groups_occupied.items():
        if count_interval == count_check:
            count_check += 1
            continue
        else:
            if data[day] == []:
                mas_check.append(True)
            else:
                try:
                    if len(room) > 1:
                        for i in room:
                            if str(i) in data[day][count]:
                                mas_check.append(False)
                                continue
                            else:
                                mas_check.append(True)
                                room = i
                                break
                    else:
                        if str(room) in data[day][count]:
                            mas_check.append(False)

                    if classes in data[day][count] and view in data[day][count] and view not in "Лекция":
                        mas_check.append(False)
                    else:
                        mas_check.append(True)
                except Exception as ex:
                    i = ex
                    mas_check.append(True)

        count_check += 1

    if False not in mas_check:
        if type(room) == list and len(room) > 1:
            return True, random.choice(room)
        else:
            return True, room
    else:
        return False, ""


# функция для прохода по всем дням и группам
def create_timetable():
    students = select_groups(direction_id)
    ave_num = average_lessons()
    occupied_teachers_temp = {day: [] for day in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]}

    # выявление кол-ва занятий под чет/нечет неделю
    for i in range(2):
        if i == 0:
            view_week = "Нечет"
            groups_occupied = {group: {"Понедельник": [], "Вторник": [], "Среда": [], "Четверг": [], "Пятница": [], "Суббота": []} for group in select_groups(direction_id).keys()}
            hours_per_week_temp = hours_per_week.copy()
            for sub, data in hours_per_week_temp.items():
                for name in data.keys():
                    data[name] = round(data[name] / 2)

            # обновление кол-ва пар в неделю в таблице бд
            update_disciplines(hours_per_week)
            for day, day_less in occupied_teachers_temp.items():

                for group, day_walk in students.items():

                    if day in day_walk: # не учатся
                        continue

                    else: # учатся
                        # составление расписания на день
                        create_schudle(ave_num, day, group, groups_occupied)

            insert_schudle(groups_occupied, view_week)

        else:
            view_week = "Чет"
            groups_occupied = {group: {"Понедельник": [], "Вторник": [], "Среда": [], "Четверг": [], "Пятница": [], "Суббота": []} for group in select_groups(direction_id).keys()}
            for sub, data in hours_per_week_temp.items():
                for name in data.keys():
                    data[name] -= round(data[name] / 2)

             # обновление кол-ва пар в неделю в таблице бд
            update_disciplines(hours_per_week)
            for day, day_less in occupied_teachers_temp.items():

                for group, day_walk in students.items():

                    if day in day_walk: # не учатся
                        continue

                    else: # учатся
                        # составление расписания на день
                        create_schudle(ave_num, day, group, groups_occupied)

            insert_schudle(groups_occupied, view_week)


def create_schudle(ave_num, day, group, groups_occupied) -> None:

    teatchers = select_coaches(direction_id)
    for key, teatcher in teatchers.items():
        for i in [1, 2]:
            if "," in str(teatcher[i][0]):
                teatcher[i] = [item.strip() for item in teatcher[i][0].split(",")]

    # здесь должна быть функция апдейт из бд, которая скажет, сколько пар на неделе нужно
    count = 0
    for i in range(ave_num):
        hours_week_couple = select_hours_week_couple(direction_id)
        hours_per_week_temp = True_counter_hours(hours_week_couple, group, groups_occupied)
        for classes, views in hours_week_couple.items():
            for view in views:
                if hours_week_couple[classes][view] == 0:
                    continue
                else:
                    for teatcher in teatchers.values():
                        if classes in teatcher[0] and view in teatcher[1] and day not in teatcher[2] and select_faculty_schudle(day, hours_per_semester[classes][view][1]):
                            # проверка на кол-во пар + плюс на нужду в дисциплине на неделе + проверка на уникальность дня!
                            check = check_qniq(group, day, classes, count, view, hours_per_semester[classes][view][1], groups_occupied)
                            if count < (ave_num + 1) and hours_week_couple[classes][view] > 0 and check[0]:
                                # проверка на нужду в виде мультимедии
                                if hours_per_semester[classes][view][2] == 1:
                                    new_classes = classes + "/" + f"{view}/{check[1]}каб/Мультимедия"
                                    groups_occupied[group][day].append(new_classes)
                                    count += 1

                                else:
                                    new_classes = classes + "/" + f"{view}/{check[1]}каб"
                                    groups_occupied[group][day].append(new_classes)
                                    count += 1


# считает верный остаток пар на неделе
def True_counter_hours(hours_week_couple, group, groups_occupied):
    views = ["Лекция", "Лабораторная", "Практика"]
    for key, data in groups_occupied.items():
        if key == group:
            for day, subjects in data.items():  # subjects это список
                for subject in subjects:  # итерация по списку
                    name_sub = subject.split("/")[0]
                    for view in views:
                        if view in subject:
                            hours_week_couple[name_sub][view] -= 1

    return hours_per_week


create_timetable()

pass