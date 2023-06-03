import tkinter as tk  # Импорт модуля tkinter для создания графического интерфейса
from tkinter import messagebox, ttk  # Импорт классов messagebox и ttk из модуля tkinter
from tkinter import filedialog  # Импорт класса filedialog из модуля tkinter
from PIL import Image, ImageTk  # Импорт классов Image и ImageTk из модуля PIL
import random  # Импорт модуля random для работы со случайными числами

class GameOfLife:
    def __init__(self):
        self.boundary_type = "закольцованная"  # Начальное значение типа границы поля
        self.row_count = 50  # Количество строк на поле
        self.col_count = 50  # Количество столбцов на поле
        self.cell_size = 16  # Размер клетки на поле
        self.cells = [[0 for _ in range(self.col_count)] for _ in range(self.row_count)]  # Создание двумерного списка клеток
        self.buffer = [[0 for _ in range(self.col_count)] for _ in range(self.row_count)]  # Создание буферного двумерного списка клеток
        self.is_running = False  # Флаг состояния игры (запущена/остановлена)
        self.speed = 100  # Скорость игры (задержка между шагами в миллисекундах)
        self.generation_count = 0  # Счетчик поколений
        self.root = tk.Tk()  # Создание главного окна приложения

        # Настройка внешнего вида главного окна
        self.root.title("Игра \"Жизнь\"")
        self.root.resizable(False, False)  # Запрет изменения размера окна
        self.root.geometry("+550+50")  # Начальная позиция основного окна

        # Загрузка и изменение размера изображения значка игры "Жизнь"
        icon_image = Image.open("life_icon.png")
        icon_image = icon_image.resize((30, 30), Image.LANCZOS)
        self.icon = ImageTk.PhotoImage(icon_image)

        self.root.configure(bg="grey22")  # Задание фонового цвета главного окна

        self.label_style = ttk.Style()  # Создание объекта стиля для надписей
        self.label_style.configure("My.TLabel",  # имя стиля
                                    font="helvetica 13",  # шрифт
                                    foreground="white",  # цвет текста
                                    padding=5,  # отступы
                                    background="grey22")  # фоновый цвет

        self.style = ttk.Style()  # Создание объекта стиля для виджетов ttk
        self.style.configure("MainWindow.TFrame", background="white")  # настройка стиля фрейма
        self.style.configure("TButton", background="white", foreground="black",
                             font=("Helvetica", 13), width=20, padding=5)  # настройка стиля кнопок
        self.style.configure("TLabel", foreground="black", background="white", font=("Helvetica", 13))  # настройка стиля надписей
        self.style.configure("Title.TLabel", foreground="black", background="white",
                             font=("Helvetica", 13))  # настройка стиля названий

        self.root.update()  # Обновление главного окна (вызов всех обработчиков событий и перерисовка виджетов)

        self.title_label = ttk.Label(self.root, text="Жизнь", style="My.TLabel")  # Создание надписи "Жизнь"
        self.title_label.pack(side=tk.TOP,
                              pady=10)  # Размещение надписи в верхней части окна с отступом сверху 10 пикселей

        self.canvas = tk.Canvas(self.root, width=self.col_count * self.cell_size,
                                # Создание холста (поле) для отображения клеток игры
                                height=self.row_count * self.cell_size,
                                bg="black")  # Задание размеров холста и черного фона
        self.canvas.pack()  # Размещение холста в окне

        self.canvas.bind("<B1-Motion>",
                         self.handle_motion)  # Привязка обработчика движения мыши на холсте к функции handle_motion

        self.canvas.pack()  # Размещение холста в окне
        self.canvas.bind("<Button-1>",
                         self.handle_motion)  # Привязка обработчика нажатия левой кнопки мыши на холсте к функции handle_motion

        self.start_button = ttk.Button(self.root, text="Старт",
                                       command=self.start_game)  # Создание кнопки "Старт" с привязкой к функции start_game
        self.start_button.pack(side=tk.LEFT, padx=10)  # Размещение кнопки слева с отступом слева 10 пикселей

        self.stop_button = ttk.Button(self.root, text="Стоп",
                                      command=self.stop_game)  # Создание кнопки "Стоп" с привязкой к функции stop_game
        self.stop_button.pack(side=tk.LEFT, padx=10)  # Размещение кнопки слева с отступом слева 10 пикселей

        self.generation_label = ttk.Label(self.root, text="Поколение: 0",
                                          style="My.TLabel")  # Создание надписи "Поколение: 0"
        self.generation_label.pack(side=tk.LEFT,
                                   pady=10)  # Размещение надписи слева с отступом сверху и снизу 10 пикселей

        self.menu_button = ttk.Button(self.root, text="Меню",
                                      command=self.show_menu)  # Создание кнопки "Меню" с привязкой к функции show_menu
        self.menu_button.pack(side=tk.RIGHT, padx=10)  # Размещение кнопки справа с отступом справа 10 пикселей

        self.menu_window = None  # Инициализация переменной, хранящей ссылку на окно меню

        self.draw_board()  # Вызов функции для отрисовки начального состояния игрового поля

    def return_to_menu(self):
        if self.menu_window is not None and self.menu_window.winfo_exists():
            self.menu_window.destroy()  # Закрытие окна меню, если оно уже открыто
        self.show_menu()  # Открытие окна меню

    def clear_board(self):
        for i in range(self.row_count):
            for j in range(self.col_count):
                self.cells[i][j] = 0  # Установка значения клетки в 0 (очистка поля)
        self.generation_count = 0  # Сброс счетчика поколений в 0
        self.is_running = False  # Установка флага is_running в False
        self.draw_board()  # Перерисовка игрового поля

    def random_fill(self):
        for i in range(self.row_count):
            for j in range(self.col_count):
                self.cells[i][j] = random.choice([0, 1])  # Заполнение поля случайными значениями 0 или 1
        self.draw_board()  # Перерисовка игрового поля

    def handle_click(self, event):
        row = event.y // self.cell_size  # Определение номера строки, на которой был совершен клик
        col = event.x // self.cell_size  # Определение номера столбца, на котором был совершен клик
        if row < self.row_count and col < self.col_count:
            self.cells[row][col] = 1 - self.cells[row][
                col]  # Инвертирование значения клетки (0 становится 1, 1 становится 0)
            self.draw_cell(row, col)  # Перерисовка измененной клетки

    def handle_motion(self, event):
        row = event.y // self.cell_size  # Определение номера строки, на которой происходит движение мыши
        col = event.x // self.cell_size  # Определение номера столбца, на котором происходит движение мыши
        if row < self.row_count and col < self.col_count:
            self.cells[row][col] = 1  # Установка значения клетки в 1 (активация клетки)
            self.draw_cell(row, col)  # Перерисовка измененной клетки

    def start_game(self):
        if not self.is_running:
            if self.generation_count == 0:  # Проверка счетчика поколений
                self.generation_count = 0  # Сброс счетчика поколений в 0
            self.is_running = True  # Установка флага is_running в True
            self.evolve()  # Запуск эволюции игры

    def stop_game(self):
        self.is_running = False  # Установка флага is_running в False

    def count_neighbours(self, row, col):
        count = 0  # Инициализация счетчика соседей
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if self.boundary_type == "закольцованная":  # Проверка типа границы (закольцованная)
                    nb_row = (
                                         row + i) % self.row_count  # Определение номера строки соседней клетки с учетом закольцованности
                    nb_col = (
                                         col + j) % self.col_count  # Определение номера столбца соседней клетки с учетом закольцованности
                    count += self.cells[nb_row][nb_col]  # Увеличение счетчика соседей, если соседняя клетка активна
                elif self.boundary_type == "открытая":  # Проверка типа границы (открытая)
                    nb_row = row + i  # Определение номера строки соседней клетки
                    nb_col = col + j  # Определение номера столбца соседней клетки
                    if 0 <= nb_row < self.row_count and 0 <= nb_col < self.col_count:
                        count += self.cells[nb_row][nb_col]  # Увеличение счетчика соседей, если соседняя клетка активна
        return count  # Возврат количества активных соседей

    def evolve(self):
        no_changes = True  # Флаг для отслеживания изменений в клетках
        for i in range(self.row_count):
            for j in range(self.col_count):
                neighbours = self.count_neighbours(i, j)  # Подсчет количества соседей клетки
                if self.cells[i][j] == 1:  # Если клетка активна
                    if neighbours < 2 or neighbours > 3:  # Если количество соседей меньше 2 или больше 3
                        self.buffer[i][j] = 0  # Установить значение клетки в 0 (клетка умирает)
                        if self.buffer[i][j] != self.cells[i][j]:  # Проверка на изменение клетки
                            no_changes = False  # Установить флаг no_changes в False (были изменения)
                    else:
                        self.buffer[i][j] = 1  # Установить значение клетки в 1 (клетка остается живой)
                        if self.buffer[i][j] != self.cells[i][j]:  # Проверка на изменение клетки
                            no_changes = False  # Установить флаг no_changes в False (были изменения)
                else:  # Если клетка неактивна
                    if neighbours == 3:  # Если количество соседей равно 3
                        self.buffer[i][j] = 1  # Установить значение клетки в 1 (клетка оживает)
                        if self.buffer[i][j] != self.cells[i][j]:  # Проверка на изменение клетки
                            no_changes = False  # Установить флаг no_changes в False (были изменения)
                    else:
                        self.buffer[i][j] = 0  # Установить значение клетки в 0 (клетка остается мертвой)
                        if self.buffer[i][j] != self.cells[i][j]:  # Проверка на изменение клетки
                            no_changes = False  # Установить флаг no_changes в False (были изменения)

        self.cells, self.buffer = self.buffer, self.cells  # Заменить текущее состояние клеток на следующее

        self.generation_count += 1  # Увеличить счетчик поколений
        self.generation_label["text"] = f"Поколение: {self.generation_count}"  # Обновить надпись с номером поколения

        self.draw_board()  # Перерисовать игровое поле

        if not any(any(row) for row in
                   self.cells) or no_changes:  # Проверка на отсутствие изменений или всех мертвых клеток
            self.generation_count = 0  # Сбросить счетчик поколений
        else:
            if self.is_running:
                self.root.after(self.speed, self.evolve)  # Запустить следующую эволюцию через заданное время

    def draw_board(self):
        self.canvas.delete("all")  # Удалить все элементы на холсте
        for i in range(self.row_count):
            for j in range(self.col_count):
                if self.cells[i][j] == 1:  # Если клетка активна
                    self.draw_cell(i, j)  # Нарисовать активную клетку на холсте

    def draw_cell(self, row, col):
        x1 = col * self.cell_size  # Вычислить координату x левого верхнего угла клетки на холсте
        y1 = row * self.cell_size  # Вычислить координату y левого верхнего угла клетки на холсте
        x2 = x1 + self.cell_size  # Вычислить координату x правого нижнего угла клетки на холсте
        y2 = y1 + self.cell_size  # Вычислить координату y правого нижнего угла клетки на холсте
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="lime",
                                     outline="black")  # Нарисовать прямоугольник-клетку на холсте с заданными координатами

    def show_menu(self):
        if self.menu_window is not None and self.menu_window.winfo_exists():
            self.menu_window.destroy()

        self.menu_window = tk.Toplevel(self.root)  # Создание нового окна для меню
        self.menu_window.attributes("-alpha", 0.92)  # Установить прозрачность окна
        self.menu_window.title("Меню")  # Установить заголовок окна
        self.menu_window.resizable(False, False)  # Запретить изменение размеров окна
        self.menu_window.geometry(
            f"{self.root.winfo_width()}x{self.root.winfo_height()}+{self.root.winfo_x()}+{self.root.winfo_y()}")  # Установить размеры и позицию окна

        menu_icon = ttk.Label(self.menu_window,
                              image=self.icon)  # Создание и добавление значка игры "Жизнь" в правый верхний угол окна "Меню"
        menu_icon.pack(anchor="ne", padx=10, pady=10)

        self.style.configure("Menu.TFrame", background="gray")  # Конфигурирование стиля для фрейма окна меню
        self.menu_frame = ttk.Frame(self.menu_window,
                                    style="Menu.TFrame")  # Создание фрейма окна меню с заданным стилем
        self.menu_frame.pack()  # Упаковка фрейма

        self.menu_window.update()

        speed_label = ttk.Label(self.menu_window, text="Скорость (мс):")  # Создание надписи "Скорость (мс):"
        self.speed_label_var = tk.StringVar()
        self.speed_label_var.set(f"{self.speed} мс")  # Установка значения переменной скорости в надпись
        speed_label_value = ttk.Label(self.menu_window,
                                      textvariable=self.speed_label_var)  # Создание надписи со значением скорости
        speed_label_value.pack(pady=15)
        speed_label.pack()
        speed_scale = ttk.Scale(self.menu_window, from_=1000, to=100, length=150,
                                command=self.set_speed)  # Создание ползунка для выбора скорости
        speed_scale.set(self.speed)  # Установка значения ползунка в текущую скорость
        speed_scale.pack(pady=15)

        self.boundary_label = ttk.Label(self.menu_window,
                                        text="Тип границы поля:")  # Создание надписи "Тип границы поля:"
        self.boundary_label.pack(pady=15)

        self.boundary_combobox = ttk.Combobox(self.menu_window, values=["закольцованная",
                                                                        "открытая"])  # Создание выпадающего списка для выбора типа границы
        self.boundary_combobox.set(self.boundary_type)  # Установка значения выпадающего списка в текущий тип границы
        self.boundary_combobox.configure(state="readonly")  # Запретить редактирование выпадающего списка
        self.boundary_combobox.pack(pady=15)

        self.boundary_combobox.bind("<<ComboboxSelected>>",
                                    self.set_boundary_type)  # Привязка обработчика события выбора пункта в выпадающем списке

        rules_button = ttk.Button(self.menu_window, text="Правила игры",
                                  command=self.show_rules)  # Создание кнопки "Правила игры" с обработчиком нажатия
        rules_button.pack(pady=15)

        save_button = ttk.Button(self.menu_window, text="Сохранить шаблон",
                                 command=self.save_template)  # Создание кнопки "Сохранить шаблон" с обработчиком нажатия
        save_button.pack(pady=15)

        load_button = ttk.Button(self.menu_window, text="Загрузить шаблон",
                                 command=self.load_template)  # Создание кнопки "Загрузить шаблон" с обработчиком нажатия
        load_button.pack(pady=15)

        patterns_button = ttk.Button(self.menu_window, text="Шаблоны",
                                     command=self.show_patterns)  # Создание кнопки "Шаблоны" с обработчиком нажатия
        patterns_button.pack(pady=15)

        random_button = ttk.Button(self.menu_window, text="Случайное заполнение",
                                   command=self.random_fill)  # Создание кнопки "Случайное заполнение" с обработчиком нажатия
        random_button.pack(pady=15)

        clear_button = ttk.Button(self.menu_window, text="Очистить поле",
                                  command=self.clear_board)  # Создание кнопки "Очистить поле" с обработчиком нажатия
        clear_button.pack(pady=15)

        exit_button = ttk.Button(self.menu_window, text="Выход",
                                 command=self.exit_game)  # Создание кнопки "Выход" с обработчиком нажатия
        exit_button.pack(side=tk.BOTTOM, pady=15)

        play_button = ttk.Button(self.menu_window, text="Играть",
                                 command=self.return_to_game)  # Создание кнопки "Играть" с обработчиком нажатия
        play_button.pack(side=tk.BOTTOM, pady=15)

    def set_boundary_type(self, event):
        self.boundary_type = self.boundary_combobox.get()  # Получить выбранный тип границы из выпадающего списка
        self.draw_board()  # Перерисовать игровое поле с новым типом границы

    def show_rules(self):
        self.menu_window.update()
        width = self.menu_window.winfo_width()
        height = self.menu_window.winfo_height()

        rules_window = tk.Toplevel(self.menu_window)  # Создание нового окна "Правила игры"
        rules_window.title("Правила игры")
        rules_window.geometry(f"{width}x{height}")
        rules_window.resizable(False, False)

        # Создание и добавление значка игры "Жизнь" в правый верхний угол окна "Правила игры"
        rules_icon = ttk.Label(rules_window, image=self.icon)
        rules_icon.pack(anchor="ne", padx=10, pady=10)

        rules_window.transient(self.menu_window)
        rules_window.geometry(
            f"{self.menu_window.winfo_width()}x{self.menu_window.winfo_height()}+{self.menu_window.winfo_x()}+{self.menu_window.winfo_y()}")

        rules_label = tk.Label(rules_window, text="Правила игры \"Жизнь\":\n\n"
                                                  "1. Любая живая клетка с меньше чем двумя соседями погибает от одиночества.\n"
                                                  "2. Любая живая клетка с более чем тремя соседями погибает от перенаселения.\n"
                                                  "3. Любая живая клетка с двумя или тремя соседями продолжает жить на следующем шаге.\n"
                                                  "4. Любая мертвая клетка с ровно тремя соседями становится живой на следующем шаге.\n",
                               wraplength=width, font=("Arial", 16))
        rules_label.pack(expand=True, fill=tk.BOTH)

        back_button = ttk.Button(rules_window, text="Назад",
                                 command=self.return_to_menu)  # Создание кнопки "Назад" с обработчиком нажатия
        back_button.pack(pady=10)

    def set_speed(self, speed):
        self.speed = int(float(speed))  # Установить новое значение скорости, полученное из ползунка
        self.speed_label_var.set(f"{self.speed} мс")  # Обновить значение переменной скорости в надписи

    def save_template(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[
            ("Text Files", "*.txt")])  # Открыть диалоговое окно для выбора файла для сохранения шаблона
        if filename:
            with open(filename, "w") as file:
                for row in self.cells:
                    file.write(
                        "".join(str(cell) for cell in row) + "\n")  # Сохранить текущее состояние игрового поля в файл
            messagebox.showinfo("Сохранение шаблона",
                                "Шаблон успешно сохранен.")  # Показать информационное сообщение об успешном сохранении шаблона

    def load_template(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt")])  # Открыть диалоговое окно для выбора файла для загрузки шаблона
        if filename:
            with open(filename, "r") as file:
                lines = file.readlines()
                for i, line in enumerate(lines):
                    if i >= self.row_count:
                        break
                    for j, char in enumerate(line.strip()):
                        if j >= self.col_count:
                            break
                        self.cells[i][j] = int(char)  # Загрузить состояние клеток из файла и обновить игровое поле
            self.draw_board()  # Перерисовать игровое поле
            messagebox.showinfo("Загрузка шаблона",
                                "Шаблон успешно загружен.")  # Показать информационное сообщение об успешной загрузке шаблона

    def show_patterns(self):
        patterns_window = tk.Toplevel(self.menu_window)  # Создание нового окна "Шаблоны"
        patterns_window.title("Шаблоны")
        patterns_window.geometry(f"{self.root.winfo_width()}x{self.root.winfo_height()}")
        patterns_window.resizable(False, False)

        patterns_window.transient(self.menu_window)
        patterns_window.geometry(
            f"{self.menu_window.winfo_width()}x{self.menu_window.winfo_height()}+{self.menu_window.winfo_x()}+{self.menu_window.winfo_y()}")

        # Создание и добавление значка игры "Жизнь" в правый верхний угол окна "Шаблоны"
        patterns_icon = ttk.Label(patterns_window, image=self.icon)
        patterns_icon.pack(anchor="ne", padx=10, pady=10)

        pattern1_button = ttk.Button(patterns_window, text="Глайдер",
                                     command=self.load_pattern1)  # Создание кнопки "Глайдер" с обработчиком нажатия
        pattern1_button.pack(pady=10)

        pattern2_button = ttk.Button(patterns_window, text="Карусель",
                                     command=self.load_pattern2)  # Создание кнопки "Карусель" с обработчиком нажатия
        pattern2_button.pack(pady=10)

        pattern3_button = ttk.Button(patterns_window, text="Столкновение",
                                     command=self.load_pattern3)  # Создание кнопки "Столкновение" с обработчиком нажатия
        pattern3_button.pack(pady=10)

        back_button = ttk.Button(patterns_window, text="Назад",
                                 command=self.return_to_menu)  # Создание кнопки "Назад" с обработчиком нажатия
        back_button.pack(side=tk.BOTTOM, pady=10)

    def load_pattern1(self):
        # Здесь можно определить свой шаблон или использовать готовый
        pattern = [[0, 0, 0, 0, 0],
                   [0, 0, 1, 0, 0],
                   [0, 0, 0, 1, 0],
                   [0, 1, 1, 1, 0],
                   [0, 0, 0, 0, 0]]

        for i in range(min(len(pattern), self.row_count)):
            for j in range(min(len(pattern[i]), self.col_count)):
                self.cells[i][j] = pattern[i][j]
                # Загрузить состояние клеток из шаблона и обновить игровое поле

        self.draw_board()
        # Перерисовать игровое поле

    def load_pattern2(self):
        # Здесь можно определить свой шаблон или использовать готовый
        pattern = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0],
                   [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                   [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
                   [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
                   [0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        for i in range(min(len(pattern), self.row_count)):
            for j in range(min(len(pattern[i]), self.col_count)):
                self.cells[i][j] = pattern[i][j]
                # Загрузить состояние клеток из шаблона и обновить игровое поле

        self.draw_board()
        # Перерисовать игровое поле

    def load_pattern3(self):
        # Здесь можно определить свой шаблон или использовать готовый
        pattern = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        for i in range(min(len(pattern), self.row_count)):
            for j in range(min(len(pattern[i]), self.col_count)):
                self.cells[i][j] = pattern[i][j]
                # Загрузить состояние клеток из шаблона и обновить игровое поле

        self.draw_board()
        # Перерисовать игровое поле

    def exit_game(self):
        self.root.destroy()

    def return_to_game(self):
        if self.menu_window is not None and self.menu_window.winfo_exists():
            self.menu_window.destroy()

        self.root.deiconify()

if __name__ == "__main__":
    game = GameOfLife()
    game.root.mainloop()