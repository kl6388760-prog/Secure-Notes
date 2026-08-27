import customtkinter as ctk
from tkinter import messagebox, Toplevel
import datetime
from storage import init_storage, load_notes, save_notes

ctk.set_appearance_mode("dark")  # тёмная тема
ctk.set_default_color_theme("blue")

class LoginWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Вход в Secure Notes")
        self.geometry("400x300")
        self.resizable(False, False)
        self.master = master
        self.password = None

        frame = ctk.CTkFrame(self)
        frame.pack(expand=True, fill="both", padx=30, pady=30)

        ctk.CTkLabel(frame, text="Введите мастер-пароль", font=("Segoe UI", 18)).pack(pady=(20,10))
        self.pwd_entry = ctk.CTkEntry(frame, show="*", width=250)
        self.pwd_entry.pack(pady=10)
        self.pwd_entry.bind("<Return>", lambda e: self.login())

        self.login_btn = ctk.CTkButton(frame, text="Войти", command=self.login, width=120)
        self.login_btn.pack(pady=10)

        self.info_label = ctk.CTkLabel(frame, text="", text_color="red")
        self.info_label.pack(pady=(5,0))

    def login(self):
        pwd = self.pwd_entry.get()
        if not pwd:
            self.info_label.configure(text="Пароль не может быть пустым")
            return
        # Проверяем, существует ли файл и можно ли расшифровать
        try:
            notes = load_notes(pwd)
            if notes is None:
                self.info_label.configure(text="Неверный пароль или повреждённые данные")
                return
            # Если файл пустой, создаём новый
            if notes == {}:
                save_notes({}, pwd)
            self.password = pwd
            self.destroy()
            self.master.deiconify()
            self.master.after(100, lambda: self.master.load_notes())
        except Exception as e:
            self.info_label.configure(text=f"Ошибка: {str(e)}")

class NotesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Secure Notes")
        self.geometry("900x600")
        self.withdraw()  # скрываем главное окно до входа

        init_storage()
        self.current_notes = {}
        self.current_id = None
        self.password = None

        # Элементы интерфейса
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Левая панель (список заметок)
        self.left_frame = ctk.CTkFrame(self, width=250)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.left_frame.grid_propagate(False)

        ctk.CTkLabel(self.left_frame, text="Мои заметки", font=("Segoe UI", 16, "bold")).pack(pady=(10,5))

        self.search_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Поиск...")
        self.search_entry.pack(pady=5, padx=10, fill="x")
        self.search_entry.bind("<KeyRelease>", self.filter_notes)

        self.listbox = ctk.CTkScrollableFrame(self.left_frame, fg_color="transparent")
        self.listbox.pack(pady=5, padx=10, fill="both", expand=True)

        # Кнопки управления заметками
        btn_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        btn_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(btn_frame, text="+ Новая", command=self.new_note, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🗑 Удалить", command=self.delete_note, width=80, fg_color="#a04141").pack(side="right", padx=5)

        # Правая панель (редактор)
        self.right_frame = ctk.CTkFrame(self, corner_radius=10)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.title_entry = ctk.CTkEntry(self.right_frame, placeholder_text="Заголовок заметки", font=("Segoe UI", 16))
        self.title_entry.grid(row=0, column=0, padx=15, pady=(15,5), sticky="ew")

        self.text_area = ctk.CTkTextbox(self.right_frame, wrap="word", font=("Segoe UI", 14))
        self.text_area.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")

        # Кнопка сохранения
        self.save_btn = ctk.CTkButton(self.right_frame, text="Сохранить заметку", command=self.save_current_note)
        self.save_btn.grid(row=2, column=0, padx=15, pady=10, sticky="e")

        # Связываем изменения с автосохранением (опционально)
        # self.title_entry.bind("<KeyRelease>", lambda e: self.save_current_note())
        # self.text_area.bind("<KeyRelease>", lambda e: self.save_current_note())

        # Запускаем окно входа
        self.login_window = LoginWindow(self)
        self.login_window.grab_set()

    def load_notes(self):
        self.password = self.login_window.password
        self.current_notes = load_notes(self.password)
        if self.current_notes is None:
            self.current_notes = {}
        self.refresh_list()

    def refresh_list(self, filter_text=""):
        for widget in self.listbox.winfo_children():
            widget.destroy()
        # Сортируем по дате (новые сверху)
        sorted_ids = sorted(self.current_notes.keys(), key=lambda k: self.current_notes[k].get("date", ""), reverse=True)
        for idx in sorted_ids:
            note = self.current_notes[idx]
            title = note.get("title", "Без заголовка")
            if filter_text and filter_text.lower() not in title.lower() and filter_text.lower() not in note.get("content", "").lower():
                continue
            btn = ctk.CTkButton(
                self.listbox,
                text=title,
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                command=lambda i=idx: self.load_note(i)
            )
            btn.pack(fill="x", pady=2)

    def filter_notes(self, event=None):
        text = self.search_entry.get()
        self.refresh_list(text)

    def new_note(self):
        new_id = str(datetime.datetime.now().timestamp())
        self.current_notes[new_id] = {
            "title": "Новая заметка",
            "content": "",
            "date": datetime.datetime.now().isoformat()
        }
        self.save_current_notes()
        self.refresh_list()
        self.load_note(new_id)

    def load_note(self, note_id):
        self.current_id = note_id
        note = self.current_notes[note_id]
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, note.get("title", ""))
        self.text_area.delete("0.0", "end")
        self.text_area.insert("0.0", note.get("content", ""))

    def save_current_note(self):
        if self.current_id is None:
            return
        title = self.title_entry.get().strip()
        content = self.text_area.get("0.0", "end-1c")
        if not title:
            title = "Без заголовка"
        self.current_notes[self.current_id]["title"] = title
        self.current_notes[self.current_id]["content"] = content
        self.current_notes[self.current_id]["date"] = datetime.datetime.now().isoformat()
        self.save_current_notes()
        self.refresh_list()

    def save_current_notes(self):
        save_notes(self.current_notes, self.password)

    def delete_note(self):
        if self.current_id is None:
            return
        if messagebox.askyesno("Удаление", "Удалить текущую заметку?"):
            del self.current_notes[self.current_id]
            self.save_current_notes()
            self.current_id = None
            self.title_entry.delete(0, "end")
            self.text_area.delete("0.0", "end")
            self.refresh_list()

    def on_closing(self):
        if self.current_id is not None:
            self.save_current_note()
        self.destroy()

if __name__ == "__main__":
    app = NotesApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
