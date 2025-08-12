import tkinter as tk
from tkinter import messagebox
import random
from collections import defaultdict
import re
import urllib.request
import os
import json

class WordleGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Wordle на русском")
        self.root.geometry("400x500")  # Более компактный размер
        self.root.resizable(False, False)
        self.WORDS = self.load_words()
        if not self.WORDS:
            # Резервный список, если не удалось загрузить
            self.WORDS = ["яблок", "столб", "речка", "ветер", "каска", "лампа",
                         "метро", "норма", "океан", "пирог", "рубин", "салат",
                         "танец", "улица", "фонарь", "хобби", "цветок", "штора",
                         "щука", "эмаль", "юноша", "якорь"]
            messagebox.showwarning("Внимание", "Используется локальный словарь")
        
        self.target_word = random.choice(self.WORDS).lower()
        self.attempts = 0
        self.max_attempts = 6
        self.current_guess = ""
        self.used_letters = defaultdict(set)
        
        self.setup_ui()
        self.center_window()
        self.root.focus_set()  # Устанавливаем фокус на окно
        
    def load_words(self):
        """Загрузка словаря с кэшированием в локальный файл"""
        cache_file = "wordle_words_cache.json"
        
        # Пробуем загрузить из кэша
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass  # Если кэш поврежден, загрузим заново
        
        # Если кэша нет, загружаем из интернета
        try:
            urls = [
                "https://raw.githubusercontent.com/danakt/russian-words/master/russian.txt",
                "https://raw.githubusercontent.com/Harrix/Russian-Nouns/main/dist/russian_nouns.txt"
            ]
            
            words = set()
            
            for url in urls:
                try:
                    with urllib.request.urlopen(url, timeout=3) as response:
                        text = response.read().decode('utf-8')
                        found_words = re.findall(r'\b[а-яё]{5}\b', text.lower())
                        words.update(found_words)
                except:
                    continue
            
            if words:
                # Сохраняем в кэш
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(list(words), f, ensure_ascii=False)
                return list(words)
            
        except Exception as e:
            print(f"Ошибка загрузки словаря: {e}")
        
        return None

        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
    
    def setup_ui(self):
        bg_color = "#f0f0f0"
        self.root.config(bg=bg_color)
        
        # Заголовок
        title_label = tk.Label(self.root, text="WORDLE", font=("Arial", 20, "bold"), 
                             bg=bg_color, fg="#333")
        title_label.pack(pady=10)
        
        # Подсказка по управлению
        controls_label = tk.Label(self.root, 
                                text="Вводите буквы с клавиатуры\nEnter - проверить\nBackspace - удалить", 
                                font=("Arial", 10), 
                                bg=bg_color)
        controls_label.pack(pady=5)
        
        # Сетка для букв
        self.grid_frame = tk.Frame(self.root, bg=bg_color)
        self.grid_frame.pack(pady=10)
        
        self.cells = []
        for row in range(6):
            row_cells = []
            for col in range(5):
                cell = tk.Label(self.grid_frame, text="", width=3, height=1, 
                              font=("Arial", 20), 
                              relief="solid", borderwidth=1,
                              bg="white", fg="black")
                cell.grid(row=row, column=col, padx=3, pady=3)
                row_cells.append(cell)
            self.cells.append(row_cells)
        
        # Кнопки управления (можно использовать вместо клавиш)
        control_frame = tk.Frame(self.root, bg=bg_color)
        control_frame.pack(pady=10)
        
        tk.Button(control_frame, text="Enter (Проверить)", width=15, height=1,
                 font=("Arial", 10), command=self.submit_guess,
                 bg="#6aaa64", fg="white").pack(side="left", padx=5)
        
        tk.Button(control_frame, text="Del (Удалить)", width=15, height=1,
                 font=("Arial", 10), command=self.delete_letter,
                 bg="#787c7e", fg="white").pack(side="left", padx=5)
        
        # Привязка клавиш
        self.root.bind("<Key>", self.handle_key_press)
    
    def handle_key_press(self, event):
        """Обработка ввода с клавиатуры"""
        char = event.char.lower()
        
        # Русские буквы
        if 'а' <= char <= 'я' or char == 'ё':
            self.add_letter(char)
        # Английская раскладка (автоматическая конвертация в русские)
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
        if len(self.current_guess) < 5:
            self.current_guess += letter
            row = self.attempts
            col = len(self.current_guess) - 1
            self.cells[row][col].config(text=letter.upper())
    
    def delete_letter(self):
        if len(self.current_guess) > 0:
            row = self.attempts
            col = len(self.current_guess) - 1
            self.cells[row][col].config(text="")
            self.current_guess = self.current_guess[:-1]
    
    def submit_guess(self):
        if len(self.current_guess) != 5:
            messagebox.showwarning("Ошибка", "Слово должно быть из 5 букв!")
        
        
        feedback = self.check_guess()
        self.update_colors(feedback)
        
        if self.current_guess == self.target_word:
            self.highlight_win()
            messagebox.showinfo("Победа!", f"Вы угадали слово {self.target_word.upper()} за {self.attempts + 1} попыток!")
            self.root.destroy()
            return
        
        self.attempts += 1
        self.current_guess = ""
        
        if self.attempts >= self.max_attempts:
            self.reveal_answer()
            messagebox.showinfo("Конец игры", f"Загаданное слово: {self.target_word.upper()}")
            self.root.destroy()
    
    def check_guess(self):
        feedback = []
        target_list = list(self.target_word)
        
        # Проверка точных совпадений
        for i in range(5):
            if self.current_guess[i] == self.target_word[i]:
                feedback.append("green")
                target_list[i] = None
            else:
                feedback.append("gray")
        
        # Проверка букв в слове, но не на месте
        for i in range(5):
            if feedback[i] != "green" and self.current_guess[i] in target_list:
                feedback[i] = "yellow"
                target_list[target_list.index(self.current_guess[i])] = None
        
        return feedback
    
    def update_colors(self, feedback):
        row = self.attempts
        for col in range(5):
            color = feedback[col]
            self.cells[row][col].config(bg=color)
    
    def highlight_win(self):
        """Анимация победы - мигание угаданного слова"""
        row = self.attempts
        for _ in range(3):
            for col in range(5):
                self.cells[row][col].config(bg="white")
            self.root.update()
            self.root.after(150)
            for col in range(5):
                self.cells[row][col].config(bg="green")
            self.root.update()
            self.root.after(150)
    
    def reveal_answer(self):
        """Показывает правильный ответ при проигрыше"""
        for col in range(5):
            self.cells[self.attempts][col].config(
                text=self.target_word[col].upper(),
                bg="#6aaa64",
                fg="white"
            )

if __name__ == "__main__":
    root = tk.Tk()
    game = WordleGame(root)
    root.mainloop()
