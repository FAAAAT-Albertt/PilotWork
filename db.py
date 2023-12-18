import sqlite3
from datetime import datetime

connection = sqlite3.connect('data.db')
cursor = connection.cursor()

# получение дисциплин и их параметров
def select_disciplines(direction_id):
    try:
        cursor.execute("""SELECT * FROM Дисциплины WHERE direction_id=?""", (direction_id, ))
        rows = cursor.fetchall()
        hours_per_semester = {}

        # Словарь для соответствия индексов и ключей.
        keys_map = {
            4: ("Лекция", 3, 14),
            8: ("Практика", 7, 15),
            12: ("Лабораторная", 11, 16)
        }

        for row in rows:
            discipline_data = {}
            for index, (key, prev_index, next_index) in keys_map.items():
                # Проверяем, является ли объект строкой и содержит ли он запятую.
                if isinstance(row[index], str) and "," in row[index]:
                    items = [item.strip() for item in row[index].split(",")]
                else:
                    items = row[index]
                discipline_data[key] = [row[prev_index], items, row[next_index]]

            hours_per_semester[row[1]] = discipline_data

        connection.commit()
    except Exception as ex:
        print(ex)


    return hours_per_semester

# обновление кол-ва пар на две недели для дисциплин
def update_disciplines(hours_per_week):
    try:
        for discipline, values in hours_per_week.items():
            lecture = values.get('Лекция', 0)
            practice = values.get('Практика', 0)
            lab = values.get('Лабораторная', 0)

            sql_execute = """
                UPDATE Дисциплины
                SET lecture_week_couple = ?, practice_week_couple = ?, labratory_week_couple = ?
                WHERE name = ?
            """

            cursor.execute(sql_execute, (lecture, practice, lab, discipline))

        connection.commit()

    except Exception as ex:
        connection.rollback()
        print(ex)

# получение кол-ва групп
def select_groups(direction_id):
    try:
        groups = {}
        cursor.execute("""SELECT * FROM Группы WHERE direction_id=?""", (direction_id, ))
        rows = cursor.fetchall()
        for row in rows:
            groups[row[2]] = [row[3]]
        connection.commit()

    except Exception as ex:
        print(ex)


    return groups

# получение преподователей из таблицы
def select_coaches(direction_id):
    try:
        coaches = {}
        cursor.execute("""SELECT * FROM Преподователи WHERE direction_id=?""", (direction_id, ))
        rows = cursor.fetchall()
        for row in rows:
            coaches[row[2]] = [row[3], [row[5]], [row[4]]]

        connection.commit()

    except Exception as ex:
        print(ex)

    return coaches


def select_hours_week_couple(direction_id):
    couple = {}
    try:
        cursor.execute("""SELECT * FROM Дисциплины WHERE direction_id=?""", (direction_id, ))
        rows = cursor.fetchall()
        for row in rows:
            couple[row[1]] = {"Лекция": row[5],
                              "Практика": row[9],
                              "Лабораторная": row[13]}
        connection.commit()

    except Exception as ex:
        print(ex)

    return couple


# добавить расписание в базу
def insert_schudle(groups_occupied, view_week):
    try:
        get_direction_id = "SELECT direction_id FROM Группы WHERE name_group=(?)"
        sql_execute = """INSERT INTO Расписание (direction_id, name_group, subject, view_subject, office, multimedia, view_week, day) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""

        for group, schudles in groups_occupied.items():
            cursor.execute(get_direction_id, (group,))
            direction_id = cursor.fetchone()[0]

            for day, subjects in schudles.items():
                for subject in subjects:
                    data = subject.split("/")
                    if len(data) == 3:
                        name, view, room = data
                        multi = ""
                        sql_params = (direction_id, group, name, view, room, multi, view_week, day)
                    else:
                        name, view, room, multi = data
                        sql_params = (direction_id, group, name, view, room, multi, view_week, day)

                    cursor.execute(sql_execute, sql_params)
                    connection.commit()



    except Exception as ex:
        print(ex)


def select_faculty_schudle(day, room):
    try:
        if type(room) == list:
            for r in room:
                sql_params = r
                cursor.execute("SELECT * FROM Расписание WHERE office=?", (f"{sql_params}каб", ))
                source = cursor.fetchall()
                if source == []:
                    return True
                else:
                    for s in source:
                        if day == s[7]:
                            return False
        else:
            sql_params = str(room)

            cursor.execute("SELECT * FROM Расписание WHERE office=?", (f"{sql_params}каб", ))
            source = cursor.fetchall()

            if source == []:
                return True
            else:
                for s in source:
                    if day == s[7]:
                        return False

    except Exception as ex:
        print(ex)

# вывод расписания в интерфейс
def test_get(group):
    try:
        cursor.execute("SELECT * FROM Расписание WHERE name_group=?", (group, ))
        schudle = cursor.fetchall()

    except Exception as ex:
        print(ex)

    return schudle

# заполнить данные для составления расписания
def insert_disciplines(data):
    try:
        cursor.execute("SELECT name FROM Факультет")
        faculties = cursor.fetchall()
        connection.commit()

        faculty = data['fields']['Факультет']
        direction = data['fields']['Направление']
        groups = data['fields']['Количество групп']
        less_weeks = data['fields']['Количество учебных недель']

        if faculty not in faculties:
            cursor.execute("INSERT INTO Факультет (name) VALUES (?)", (faculty, ))
            connection.commit()

            cursor.execute("SELECT id FROM Факультет WHERE name=?", (faculty, ))
            dir_id = cursor.fetchone()[0]
            connection.commit()

        cursor.execute("SELECT name FROM Направление")
        directions = cursor.fetchall()
        connection.commit()

        if direction in directions:
            print("Расписание для этого направления уже существует")
            return groups, less_weeks

        else:
            cursor.execute("INSERT INTO Направление (faculty_id, name) VALUES (?, ?)", (dir_id, direction))
            connection.commit()

            for discipline in data['disciplines']:
                sql_params = (dir_id, discipline['name'], discipline['lecture']['checked'], discipline['lecture']['text'], discipline['lecture']['cabinet'], discipline['practice']['checked'], discipline['practice']['text'], discipline['practice']['cabinet'], discipline['lab']['checked'], discipline['lab']['text'], discipline['lab']['cabinet'], discipline['lecture']['multimedia'], discipline['practice']['multimedia'], discipline['lab']['multimedia'])
                cursor.execute("INSERT INTO Дисциплины (direction_id, name, lecture, hours_lecture, lecture_offices, practice, hours_practice, practice_offices, laboratory, hours_laboratory, laboratory_offices, multimedia_lecture, multimedia_practice, multimedia_laboratory) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", sql_params)
                connection.commit()

            cursor.execute("INSERT INTO Семестр (direction_id, groups, less_weeks) VALUES (?, ?, ?)", (dir_id, groups, less_weeks))
            connection.commit()

    except Exception as ex:
        print(ex)

# заполнить преподователей для состовления расписания
def insert_teachers(data):
    try:
        cursor.execute("SELECT faculty_id FROM Направление WHERE name=?", (data['direction'], ))
        dir_id = cursor.fetchone()[0]
        connection.commit()

        for teacher in data['teachers']:
            cursor.execute("INSERT INTO Преподователи (direction_id, name, subject, weekend_days, view_subject) VALUES (?, ?, ?, ?, ?)", (dir_id, teacher['name'], teacher['subject'], teacher['off_days'], teacher['subject_type']))
            connection.commit()

    except Exception as ex:
        print(ex)

# заполнить группы для составления расписания
def insert_groups_start(data):
    try:
        cursor.execute("SELECT faculty_id FROM Направление WHERE name=?", (data['direction'], ))
        dir_id = cursor.fetchone()[0]
        connection.commit()

        for group in data['groups']:
            cursor.execute("INSERT INTO Группы(direction_id, name_group, weekend_days) VALUES (?, ?, ?)", (dir_id, group['name'], group['non_study_days']))
            connection.commit()

    except Exception as ex:
        print(ex)

# получить кол-во учебных недель
def select_weeks_less(direction_id):
    try:

        cursor.execute("SELECT less_weeks FROM Семестр WHERE direction_id=?", (direction_id, ))
        data = cursor.fetchone()[0]

    except Exception as ex:
        print(ex)
    return data

# получить айди для состовления расписания
def get_id(name):
    try:
        cursor.execute("SELECT faculty_id FROM Направление WHERE name=?", (name, ))
        id = cursor.fetchone()[0]

    except Exception as ex:
        print(ex)

    return id



def get_schudle_for_gspread(name_group):
    "форматирование расписания в гугл таблицу"
    try:
        sql_execute = "SELECT * FROM Расписание WHERE name_group=?"
        cursor.execute(sql_execute, (name_group, ))
        data_schudle = cursor.fetchall()

    except Exception as ex:
        print(ex)

    return data_schudle
