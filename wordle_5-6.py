import tkinter as tk
from tkinter import messagebox, ttk
import random
from collections import defaultdict
import urllib.request
import re
import os
import json

class WordleGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Wordle на русском")
        self.root.geometry("450x550")
        self.root.resizable(False, False)
        
        # Настройки игры
        self.word_length = 5  # По умолчанию
        self.max_attempts = 6
        self.words_cache = {
            5: "wordle_words_5.json",
            6: "wordle_words_6.json"
        }
        
        # Цвета для интерфейса
        self.bg_color = "#f0f0f0"
        self.root.config(bg=self.bg_color)
        
        # Запуск меню выбора режима
        self.setup_mode_selection()
    
    def setup_mode_selection(self):
        """Экран выбора режима игры"""
        self.clear_window()
        
        title = tk.Label(self.root, text="Выберите режим", 
                        font=("Arial", 20), bg=self.bg_color)
        title.pack(pady=20)
        
        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(pady=10)
        
        # Кнопки выбора режима
        modes = [
            (5, "5 букв", "#6aaa64"),
            (6, "6 букв", "#8fbc8f")
        ]
        
        for length, text, color in modes:
            tk.Button(btn_frame, text=text, width=15, height=2,
                     command=lambda l=length: self.start_game(l),
                     font=("Arial", 14), bg=color, fg="white").pack(pady=10)
    
    def start_game(self, word_length):
        """Инициализация новой игры"""
        self.word_length = word_length
        self.WORDS = self.load_words(word_length)
        
        if not self.WORDS:
            # Резервные словари
            backup_words = {
                5: ["яблок", "столб", "речка", "ветер", "каска", "лампа", 
                    "метро", "норма", "океан", "пирог", "рубин", "салат",
                    "танец", "улица", "фонарь", "хобби", "цветок", "штора",
                    "щука", "эмаль", "юноша", "якорь"],
                6: ["абзац", "автограф", "береза", "ветер", "горшок", 
                    "дерево", "ежевика", "жалюзи", "заря", "избушка",
                    "качели", "лампа", "метро", "норма", "очки", "пирог"]
            }
            self.WORDS = backup_words.get(word_length, backup_words[5])
            messagebox.showwarning("Внимание", "Используется локальный словарь")
        
        self.target_word = random.choice(self.WORDS).lower()
        self.attempts = 0
        self.current_guess = ""
        self.used_letters = defaultdict(set)
        
        self.setup_game_ui()
        self.center_window()
        self.root.focus_set()
    
    def load_words(self, word_length):
        """Загрузка и кэширование словаря"""
        cache_file = self.words_cache[word_length]
        
        # Пробуем загрузить из кэша
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    words = json.load(f)
                    return [w for w in words if len(w) == word_length]
            except:
                pass
        
        # Загрузка из интернета
        try:
            urls = [
                "https://raw.githubusercontent.com/danakt/russian-words/master/russian.txt",
                "https://raw.githubusercontent.com/Harrix/Russian-Nouns/main/dist/russian_nouns.txt"
            ]
            
            words = set()
            pattern = fr'\b[а-яё]{{{word_length}}}\b'
            
            for url in urls:
                try:
                    with urllib.request.urlopen(url, timeout=3) as response:
                        text = response.read().decode('utf-8')
                        found_words = re.findall(pattern, text.lower())
                        words.update(found_words)
                except:
                    continue
            
            if words:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(list(words), f, ensure_ascii=False)
                return list(words)
            
        except Exception as e:
            print(f"Ошибка загрузки словаря: {e}")
        
        return None
    
    def setup_game_ui(self):
        """Настройка игрового интерфейса"""
        self.clear_window()
        
        # Заголовок
        title_text = f"WORDLE - {self.word_length} букв"
        title_label = tk.Label(self.root, text=title_text, 
                             font=("Arial", 16, "bold"), 
                             bg=self.bg_color, fg="#333")
        title_label.pack(pady=10)
        
        # Кнопка возврата
        tk.Button(self.root, text="← Меню", command=self.setup_mode_selection,
                 font=("Arial", 10), bg="#d3d6da").pack(anchor="nw", padx=10, pady=5)
        
        # Подсказка управления
        controls_label = tk.Label(self.root, 
                                text="Вводите буквы с клавиатуры\nEnter - проверить\nBackspace - удалить", 
                                font=("Arial", 10), bg=self.bg_color)
        controls_label.pack(pady=5)
        
        # Игровая сетка
        self.grid_frame = tk.Frame(self.root, bg=self.bg_color)
        self.grid_frame.pack(pady=10)
        
        self.cells = []
        for row in range(self.max_attempts):
            row_cells = []
            for col in range(self.word_length):
                cell = tk.Label(self.grid_frame, text="", width=3, height=1, 
                              font=("Arial", 20), relief="solid", borderwidth=1,
                              bg="white", fg="black")
                cell.grid(row=row, column=col, padx=3, pady=3)
                row_cells.append(cell)
            self.cells.append(row_cells)
        
        # Кнопки управления
        control_frame = tk.Frame(self.root, bg=self.bg_color)
        control_frame.pack(pady=10)
        
        tk.Button(control_frame, text="Enter", width=10, 
                 command=self.submit_guess, bg="#6aaa64", fg="white").pack(side="left", padx=5)
        
        tk.Button(control_frame, text="Del", width=10, 
                 command=self.delete_letter, bg="#787c7e", fg="white").pack(side="left", padx=5)
        
        # Привязка клавиш
        self.root.bind("<Key>", self.handle_key_press)
    
    def handle_key_press(self, event):
        """Обработка ввода с клавиатуры"""
        char = event.char.lower()
        
        # Русские буквы
        if 'а' <= char <= 'я' or char == 'ё':
            self.add_letter(char)
        # Английская раскладка (автоконвертация)
        elif char in self.eng_to_rus:
            self.add_letter(self.eng_to_rus[char])
        elif event.keysym == "BackSpace":
            self.delete_letter()
        elif event.keysym == "Return":
            self.submit_guess()
    
    # Словарь для конвертации английской раскладки в русскую
    eng_to_rus = {
        'f': 'а', ',': 'б', 'd': 'в', 'u': 'г', 'l': 'д', 't': 'е',
        '`': 'ё', ';': 'ж', 'p': 'з', 'b': 'и', 'q': 'й', 'r': 'к',
        'k': 'л', 'v': 'м', 'y': 'н', 'j': 'о', 'g': 'п', 'h': 'р',
        'c': 'с', 'n': 'т', 'e': 'у', 'a': 'ф', '[': 'х', 'w': 'ц',
        'x': 'ч', 'i': 'ш', 'o': 'щ', ']': 'ъ', 's': 'ы', 'm': 'ь',
        "'": 'э', '.': 'ю', 'z': 'я'
    }
    
    def add_letter(self, letter):
        """Добавление буквы в текущую попытку"""
        if len(self.current_guess) < self.word_length:
            self.current_guess += letter
            row = self.attempts
            col = len(self.current_guess) - 1
            self.cells[row][col].config(text=letter.upper())
    
    def delete_letter(self):
        """Удаление последней буквы"""
        if len(self.current_guess) > 0:
            row = self.attempts
            col = len(self.current_guess) - 1
            self.cells[row][col].config(text="")
            self.current_guess = self.current_guess[:-1]
    
    def submit_guess(self):
        """Проверка введенного слова"""
        if len(self.current_guess) != self.word_length:
            messagebox.showwarning("Ошибка", f"Слово должно быть из {self.word_length} букв!")
            return
        
        if self.current_guess not in self.WORDS:
            messagebox.showwarning("Ошибка", "Такого слова нет в словаре!")
            return
        
        feedback = self.check_guess()
        self.update_colors(feedback)
        
        if self.current_guess == self.target_word:
            self.highlight_win()
            messagebox.showinfo("Победа!", f"Вы угадали слово {self.target_word.upper()}!")
            self.root.after(2000, self.root.destroy)
            return
        
        self.attempts += 1
        self.current_guess = ""
        
        if self.attempts >= self.max_attempts:
            self.reveal_answer()
            messagebox.showinfo("Конец игры", f"Загаданное слово: {self.target_word.upper()}")
            self.root.after(2000, self.root.destroy)
    
    def check_guess(self):
        """Анализ введенного слова"""
        feedback = []
        target_list = list(self.target_word)
        
        # Проверка точных совпадений
        for i in range(self.word_length):
            if self.current_guess[i] == self.target_word[i]:
                feedback.append("green")
                target_list[i] = None
            else:
                feedback.append("gray")
        
        # Проверка букв в слове, но не на месте
        for i in range(self.word_length):
            if feedback[i] != "green" and self.current_guess[i] in target_list:
                feedback[i] = "yellow"
                target_list[target_list.index(self.current_guess[i])] = None
        
        return feedback
    
    def update_colors(self, feedback):
        """Обновление цветов клеток"""
        row = self.attempts
        for col in range(self.word_length):
            self.cells[row][col].config(bg=feedback[col])
    
    def highlight_win(self):
        """Анимация победы"""
        row = self.attempts
        for _ in range(3):
            for col in range(self.word_length):
                self.cells[row][col].config(bg="white")
            self.root.update()
            self.root.after(150)
            for col in range(self.word_length):
                self.cells[row][col].config(bg="green")
            self.root.update()
            self.root.after(150)
    
    def reveal_answer(self):
        """Показ правильного ответа"""
        for col in range(self.word_length):
            self.cells[self.attempts][col].config(
                text=self.target_word[col].upper(),
                bg="#6aaa64",
                fg="white"
            )
    
    def clear_window(self):
        """Очистка окна"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def center_window(self):
        """Центрирование окна"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')

if __name__ == "__main__":
    root = tk.Tk()
    game = WordleGame(root)
    root.mainloop()
