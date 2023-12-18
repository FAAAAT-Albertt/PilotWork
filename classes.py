import tkinter as tk
from tkinter import ttk
from db import test_get, insert_disciplines, insert_teachers, insert_groups_start, get_id


def raise_frame(frame):
    frame.tkraise()

def generate_disciplines_content(frame):
    # Словарь для хранения ссылок на виджеты
    widgets = {
        "fields": {},
        "disciplines": []
    }

    container = tk.Canvas(frame)
    container.pack(side="left", fill="both", expand=True)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=container.yview)
    scrollbar.pack(side="right", fill="y")
    container.configure(yscrollcommand=scrollbar.set)

    disciplines_content_frame = ttk.Frame(container)
    container.create_window((0, 0), window=disciplines_content_frame, anchor="nw")

    # Области ввода
    fields = ["Факультет", "Направление", "Количество групп", "Количество учебных недель", "Количество дисциплин"]
    for idx, field in enumerate(fields, start=0):
        label = ttk.Label(disciplines_content_frame, text=f"{field}:")
        label.grid(row=idx, column=0, padx=5, pady=5)

        entry = ttk.Entry(disciplines_content_frame)
        entry.grid(row=idx, column=1, padx=5, pady=5)

        # Сохраняем ссылку на виджет
        widgets["fields"][field] = entry

    disciplines_container = ttk.Frame(disciplines_content_frame)
    disciplines_container.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

    # Функция для создания строки
    def create_row(row_num, parent, label_text):
        widgets_row = {
            "check": None,
            "entry": None,
            "multimedia": None,
            "cabinet": None
        }

        check_var = tk.IntVar()
        checkbutton = ttk.Checkbutton(parent, text=label_text, variable=check_var)
        checkbutton.grid(row=row_num, column=0, padx=5, pady=5)
        widgets_row["check"] = check_var

        cabinet_entry = ttk.Entry(parent)
        cabinet_entry.grid(row=row_num, column=3, padx=5, pady=5)
        widgets_row["cabinet"] = cabinet_entry

        entry = ttk.Entry(parent)
        entry.grid(row=row_num, column=1, padx=5, pady=5)
        widgets_row["entry"] = entry

        multimedia_var = tk.IntVar()
        multimedia_checkbutton = ttk.Checkbutton(parent, text="Мультимедия", variable=multimedia_var)
        multimedia_checkbutton.grid(row=row_num, column=2, padx=5, pady=5)
        widgets_row["multimedia"] = multimedia_var

        return widgets_row

    # Функция для генерации полей дисциплин
    def generate_disciplines_fields():
        for child in disciplines_container.winfo_children():
            child.destroy()
        widgets["disciplines"].clear()

        num = int(discipline_count_entry.get())
        for idx in range(num):
            discipline_widgets = {
                "name": None,
                "lecture": None,
                "practice": None,
                "lab": None
            }

            discipline_frame = ttk.Frame(disciplines_container)
            discipline_frame.grid(row=idx, column=0, sticky="ew", padx=5, pady=5)

            ttk.Label(discipline_frame, text=f"Дисциплина {idx+1}:").grid(row=0, column=0, padx=5, pady=5)
            discipline_entry = ttk.Entry(discipline_frame)
            discipline_entry.grid(row=0, column=1, padx=5, pady=5)

            discipline_widgets["name"] = discipline_entry
            discipline_widgets["lecture"] = create_row(1, discipline_frame, "Лекция")
            discipline_widgets["practice"] = create_row(2, discipline_frame, "Практика")
            discipline_widgets["lab"] = create_row(3, discipline_frame, "Лабораторная")

            widgets["disciplines"].append(discipline_widgets)

    discipline_count_entry = ttk.Entry(disciplines_content_frame)
    discipline_count_entry.grid(row=4, column=1, padx=5, pady=5)
    generate_button = ttk.Button(disciplines_content_frame, text="Создать области для дисциплин", command=generate_disciplines_fields)
    generate_button.grid(row=4, column=2, padx=5, pady=5)

    # Функция для извлечения всех данных
    def extract_data():
        data = {
            "fields": {k: v.get() for k, v in widgets["fields"].items()},
            "disciplines": []
        }
        for discipline in widgets["disciplines"]:
            discipline_data = {
                "name": discipline["name"].get(),
                "lecture": {
                    "checked": discipline["lecture"]["check"].get(),
                    "text": discipline["lecture"]["entry"].get(),
                    "multimedia": discipline["lecture"]["multimedia"].get(),
                    "cabinet": discipline["lecture"]["cabinet"].get()  # извлечение данных о кабинете
                },
                "practice": {
                    "checked": discipline["practice"]["check"].get(),
                    "text": discipline["practice"]["entry"].get(),
                    "multimedia": discipline["practice"]["multimedia"].get(),
                    "cabinet": discipline["practice"]["cabinet"].get()  # извлечение данных о кабинете
                },
                "lab": {
                    "checked": discipline["lab"]["check"].get(),
                    "text": discipline["lab"]["entry"].get(),
                    "multimedia": discipline["lab"]["multimedia"].get(),
                    "cabinet": discipline["lab"]["cabinet"].get()  # извлечение данных о кабинете
                }
            }
            data["disciplines"].append(discipline_data)
        insert_disciplines(data)

    populate_button = ttk.Button(disciplines_content_frame, text="Заполнить", command=extract_data)
    populate_button.grid(row=7, column=0, columnspan=3, padx=5, pady=5)

def generate_schedule_content(frame):

    def on_show_schedule():
        group_name = group_entry.get()
        schedule = test_get(group_name)

        # Очищаем предыдущие результаты
        for widget in result_frame.winfo_children():
            widget.destroy()

        if not schedule:
            ttk.Label(result_frame, text="Группа не найдена").pack(pady=5)
        else:
            for entry in schedule:
                ttk.Label(result_frame, text=str(entry)).pack(pady=5)

    # Canvas и скроллбар
    canvas = tk.Canvas(frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=scrollbar.set)

    main_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=main_frame, anchor="nw")

    # Центрирование виджетов
    input_frame = ttk.Frame(main_frame)
    input_frame.pack(pady=20, padx=20)

    ttk.Label(input_frame, text="Введите группу:").pack(pady=10)
    group_entry = ttk.Entry(input_frame, width=20)
    group_entry.pack(pady=10)

    show_button = ttk.Button(input_frame, text="Показать расписание", command=on_show_schedule)
    show_button.pack(pady=20)

    # Фрейм для отображения результатов
    result_frame = ttk.Frame(main_frame)
    result_frame.pack(pady=20, padx=20, fill=tk.X)


def generate_groups_content(frame):
    # Контейнер для групп
    groups_container = ttk.Frame(frame)
    groups_container.pack(padx=5, pady=5, fill="x")

    # Область ввода направления
    ttk.Label(groups_container, text="Направление:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    direction_entry = ttk.Entry(groups_container)
    direction_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w", columnspan=3)

    # Ввод количества групп
    ttk.Label(groups_container, text="Количество групп:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    group_input_frame = ttk.Frame(groups_container)
    group_input_frame.grid(row=1, column=1, padx=5, pady=5, sticky="w", columnspan=3)
    num_groups_entry = ttk.Entry(group_input_frame)
    num_groups_entry.pack(side="left")

    groups_widgets = {}

    # Переместим определение функции generate_groups_fields перед созданием кнопки
    def generate_groups_fields():
        # Удалим дочерние элементы начиная с 2-й строки (т.к. 0 и 1 строки содержат направление и кол-во групп)
        for child in groups_container.grid_slaves():
            if int(child.grid_info()["row"]) > 1 and child != populate_button:
                child.destroy()

        num_groups = int(num_groups_entry.get())
        for idx in range(num_groups):
            # Название группы
            ttk.Label(groups_container, text=f"Группа {idx+1}:").grid(row=idx+2, column=0, padx=5, pady=5)
            group_name_entry = ttk.Entry(groups_container)
            group_name_entry.grid(row=idx+2, column=1, padx=5, pady=5)
            groups_widgets[idx] = {"name": group_name_entry}

            # Неучебные дни
            ttk.Label(groups_container, text="Неучебные дни:").grid(row=idx+2, column=2, padx=5, pady=5)
            non_study_days_entry = ttk.Entry(groups_container)
            non_study_days_entry.grid(row=idx+2, column=3, padx=5, pady=5)
            groups_widgets[idx]["non_study_days"] = non_study_days_entry

    # Теперь создадим кнопку
    generate_button = ttk.Button(group_input_frame, text="Создать области", command=generate_groups_fields)
    generate_button.pack(side="right")

    # Кнопка для заполнения данных
    def extract_data():
        data = {
            "direction": direction_entry.get(),
            "groups": []
        }
        for idx in range(int(num_groups_entry.get())):
            group_data = {
                "name": groups_widgets[idx]["name"].get(),
                "non_study_days": groups_widgets[idx]["non_study_days"].get()
            }
            data["groups"].append(group_data)
        insert_groups_start(data)

    populate_button = ttk.Button(groups_container, text="Заполнить", command=extract_data)
    populate_button.grid(row=1000, column=0, columnspan=4, padx=5, pady=20)


def generate_get_id_content(frame):
    ttk.Label(frame, text="Введите имя направления: ").pack(pady=10, padx=10)

    id_entry = ttk.Entry(frame, width=20)
    id_entry.pack(pady=10)

    def fetch_id():
        id_value = id_entry.get()
        fetched_data = f"Данные ID: {get_id(id_value)}"
        ttk.Label(frame, text=fetched_data).pack(pady=10)

    fetch_button = ttk.Button(frame, text="Получить", command=fetch_id)
    fetch_button.pack(pady=10)


def generate_teachers_content(frame):

    def add_teachers_fields():
        # Удаляем старые поля, если они были
        for widget in teachers_frame.winfo_children():
            widget.destroy()

        try:
            num_teachers = int(num_teachers_entry.get())
            for _ in range(num_teachers):
                # Создаем горизонтальный фрейм для каждого преподавателя
                teacher_frame = ttk.Frame(teachers_frame)

                            # Область ввода имени преподавателя
                ttk.Label(teacher_frame, text="Имя преподователя:").pack(side=tk.LEFT, padx=5)
                ttk.Entry(teacher_frame, width=20).pack(side=tk.LEFT, padx=5)

                # Область ввода предмета
                ttk.Label(teacher_frame, text="Предмет:").pack(side=tk.LEFT, padx=5)
                ttk.Entry(teacher_frame, width=20).pack(side=tk.LEFT, padx=5)

                # Область ввода нерабочих дней
                ttk.Label(teacher_frame, text="Нерабочие дни:").pack(side=tk.LEFT, padx=5)
                ttk.Entry(teacher_frame, width=20).pack(side=tk.LEFT, padx=5)

                # Область ввода вида предмета
                ttk.Label(teacher_frame, text="Вид предмета:").pack(side=tk.LEFT, padx=5)
                ttk.Entry(teacher_frame, width=20).pack(side=tk.LEFT, padx=5)

                # Добавляем горизонтальный фрейм в вертикальный фрейм
                teacher_frame.pack(pady=5)

        except ValueError:
            ttk.Label(teachers_frame, text="Введите корректное количество преподавателей!").pack()

    # Область ввода направления
    direction_frame = ttk.Frame(frame)
    direction_frame.pack(pady=10)

    ttk.Label(direction_frame, text="Направление:").pack(side=tk.LEFT, padx=5)
    direction_entry = ttk.Entry(direction_frame, width=20)
    direction_entry.pack(side=tk.LEFT, padx=5)

    # Область ввода количества преподавателей
    num_teachers_frame = ttk.Frame(frame)
    num_teachers_frame.pack(pady=10)

    ttk.Label(num_teachers_frame, text="Количество преподавателей:").pack(side=tk.LEFT, padx=5)
    num_teachers_entry = ttk.Entry(num_teachers_frame, width=5)
    num_teachers_entry.pack(side=tk.LEFT, padx=5)

    # Кнопка для добавления областей ввода для преподавателей
    add_button = ttk.Button(num_teachers_frame, text="Добавить", command=add_teachers_fields)
    add_button.pack(side=tk.LEFT, padx=5)

    # Фрейм для областей ввода преподавателей
    teachers_frame = ttk.Frame(frame)
    teachers_frame.pack(pady=10)

    data_dict = {}  # словарь, в который будут записываться данные

    def populate_data():
        direction = direction_entry.get()
        teachers = []

        for child in teachers_frame.winfo_children():
            teacher_name = child.winfo_children()[1].get()
            subject = child.winfo_children()[3].get()
            off_days = child.winfo_children()[5].get()
            subject_type = child.winfo_children()[7].get()

            teachers.append({
                "name": teacher_name,
                "subject": subject,
                "off_days": off_days,
                "subject_type": subject_type
            })

        data_dict["direction"] = direction
        data_dict["teachers"] = teachers

        insert_teachers(data_dict)


    populate_button = ttk.Button(frame, text="Заполнить", command=populate_data)
    populate_button.pack(pady=5)


root = tk.Tk()
root.title("Меню")
root.geometry("600x700")

menu_frame = ttk.Frame(root)
menu_frame.pack(side=tk.TOP, fill=tk.X)

btn_disciplines = ttk.Button(menu_frame, text="Дисциплины", command=lambda: raise_frame(disciplines_frame))
btn_disciplines.pack(side=tk.LEFT, fill=tk.X, expand=True)

btn_teachers = ttk.Button(menu_frame, text="Преподаватели", command=lambda: raise_frame(teachers_frame))
btn_teachers.pack(side=tk.LEFT, fill=tk.X, expand=True)

btn_schedule = ttk.Button(menu_frame, text="Расписание", command=lambda: raise_frame(schedule_frame))
btn_schedule.pack(side=tk.LEFT, fill=tk.X, expand=True)

btn_groups = ttk.Button(menu_frame, text="Группы", command=lambda: raise_frame(groups_frame))
btn_groups.pack(side=tk.LEFT, fill=tk.X, expand=True)

btn_get_id = ttk.Button(menu_frame, text="Получить ID", command=lambda: raise_frame(get_id_frame))
btn_get_id.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Создаем фреймы
disciplines_frame = ttk.Frame(root)
disciplines_frame.place(x=0, y=50, relwidth=1, relheight=1)
generate_disciplines_content(disciplines_frame)

teachers_frame = ttk.Frame(root)
teachers_frame.place(x=0, y=50, relwidth=1, relheight=1)
generate_teachers_content(teachers_frame)

schedule_frame = ttk.Frame(root)
schedule_frame.place(x=0, y=50, relwidth=1, relheight=1)
generate_schedule_content(schedule_frame)

groups_frame = ttk.Frame(root)
groups_frame.place(x=0, y=50, relwidth=1, relheight=1)
generate_groups_content(groups_frame)

get_id_frame = ttk.Frame(root)
get_id_frame.place(x=0, y=50, relwidth=1, relheight=1)
generate_get_id_content(get_id_frame)


raise_frame(disciplines_frame)
raise_frame(teachers_frame)
raise_frame(schedule_frame)
raise_frame(groups_frame)

root.mainloop()
