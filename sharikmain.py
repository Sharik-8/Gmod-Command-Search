import tkinter as tk
from tkinter import ttk
import json
from tkinter import messagebox

class GModCommandHelper:
    def __init__(self, root):
        self.root = root
        self.root.title("GMod Command Helper Pro v1.1 — Помощник по консоли (2025)")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2b2b2b")
        
        # Стиль для тёмной темы
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#2b2b2b")
        style.configure("TLabel", background="#2b2b2b", foreground="#ffffff")
        style.configure("TEntry", fieldbackground="#404040", foreground="#ffffff")
        style.configure("Treeview", background="#404040", foreground="#ffffff", fieldbackground="#404040")
        style.configure("Treeview.Heading", background="#505050", foreground="#ffffff")
        style.map("Treeview", background=[("selected", "#606060")])
        
        # Данные команд (из Valve Wiki 2025, + примеры спавна)
        self.commands = [
            {"command": "+menu", "description": "Открывает спавн-меню (Q по дефолту). Для спавна энтити без меню: ent_create.", "category": "Bindings"},
            {"command": "ent_create", "description": "Спавнит энтити по классу. Пример: ent_create prop_physics {model \"models/props_junk/watermelon01.mdl\" pos 0 0 0 ang 0 0 0} — спавнит арбуз. Для NPC: ent_create npc_citizen {pos 100 100 0}. Нет в спавн-меню? Это твой хак!", "category": "Spawn"},
            {"command": "ent_setname", "description": "Задаёт имя энтити для таргетов. Пример: ent_setname myprop — потом !pickup myprop.", "category": "Spawn"},
            {"command": "sv_cheats 1", "description": "Включает читы (нужно для noclip, god). Перезапусти карту после.", "category": "Cheats"},
            {"command": "noclip", "description": "Лети сквозь стены (sv_cheats 1). Пример: noclip — вкл/выкл.", "category": "Cheats"},
            {"command": "god", "description": "Бессмертие (sv_cheats 1). god — вкл, god 0 — выкл.", "category": "Cheats"},
            {"command": "impulse 101", "description": "Даёт все оружия (sv_cheats 1). Для HL2-контента.", "category": "Cheats"},
            {"command": "r_drawothermodels 2", "description": "Показывает невидимых игроков (sv_cheats 1). Полезно для дебага.", "category": "Debug"},
            {"command": "ai_disable", "description": "Отключает AI всех NPC. ai_disable 0 — вкл обратно.", "category": "AI"},
            {"command": "npc_create npc_zombie", "description": "Спавнит зомби (sv_cheats 1). Альтернатива ent_create для NPC.", "category": "Spawn"},
            {"command": "phys_swap", "description": "Меняет гравитацию (sv_cheats 1). phys_swap 0 — норм.", "category": "Physics"},
            {"command": "gmod_mcore_test 1", "description": "Включает мультикор рендеринг (+FPS на 64-bit).", "category": "Performance"},
            {"command": "cl_detaildist 800", "description": "Уменьшает детали пропов для +FPS.", "category": "Performance"},
            {"command": "net_graph 1", "description": "Показывает FPS/ping в углу.", "category": "HUD"},
            {"command": "developer 1", "description": "Включает дебаг-инфо в консоль.", "category": "Debug"},
            {"command": "con_enable 1", "description": "Включает консоль (~).", "category": "Bindings"},
            {"command": "sv_gravity 600", "description": "Меняет гравитацию (дефолт 600).", "category": "Physics"},
            {"command": "sbox_maxprops 500", "description": "Лимит пропов на сервере (для админов).", "category": "Server"},
            {"command": "ulx who", "description": "ULX: Показывает игроков (если мод установлен).", "category": "Admin"},
            {"command": "rcon_password \"pass\"", "description": "Устанавливает RCON-пароль для удалённого админа.", "category": "Server"},
            # Добавь больше из Wiki, если нужно — здесь топ-20 для примера, полный список в JSON-файле ниже
        ]
        
        # Загрузи полный список из JSON (создай файл commands.json с данными из Wiki)
        try:
            with open("commands.json", "r", encoding="utf-8") as f:
                full_list = json.load(f)
                self.commands.extend(full_list)  # Дополни
        except FileNotFoundError:
            pass  # Используй встроенный
        
        self.filtered_commands = self.commands.copy()
        
        self.create_ui()
    
    def create_ui(self):
        # Верхняя панель поиска
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="Поиск по команде или описанию:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=10)
        self.search_entry.bind("<KeyRelease>", self.filter_commands)
        
        ttk.Button(search_frame, text="Очистить", command=self.clear_search).pack(side=tk.RIGHT)
        
        # Treeview для списка
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("Command", "Description", "Category")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("Command", text="Команда")
        self.tree.heading("Description", text="Описание")
        self.tree.heading("Category", text="Категория")
        
        self.tree.column("Command", width=150)
        self.tree.column("Description", width=400)
        self.tree.column("Category", width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<Double-1>", self.show_details)  # Двойной клик для деталей
        
        # Нижняя панель деталей
        details_frame = ttk.Frame(self.root)
        details_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(details_frame, text="Подробное описание:").pack(anchor=tk.W)
        self.details_text = tk.Text(details_frame, height=8, bg="#404040", fg="#ffffff", wrap=tk.WORD)
        scrollbar_details = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=scrollbar_details.set)
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_details.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Копировать команду в буфер", command=self.copy_command).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Обновить список", command=self.refresh_list).pack(side=tk.RIGHT)
        
        self.populate_tree()
    
    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for cmd in self.filtered_commands:
            self.tree.insert("", tk.END, values=(cmd["command"], cmd["description"][:50] + "..." if len(cmd["description"]) > 50 else cmd["description"], cmd["category"]))
    
    def filter_commands(self, event=None):
        query = self.search_var.get().lower()
        self.filtered_commands = [cmd for cmd in self.commands if query in cmd["command"].lower() or query in cmd["description"].lower()]
        self.populate_tree()
    
    def clear_search(self):
        self.search_var.set("")
        self.filtered_commands = self.commands.copy()
        self.populate_tree()
    
    def show_details(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item["values"]
            cmd = values[0]
            full_desc = next((c["description"] for c in self.commands if c["command"] == cmd), "Описание не найдено.")
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, f"Команда: {cmd}\n\n{full_desc}")
    
    def copy_command(self):
        selection = self.tree.selection()
        if selection:
            cmd = self.tree.item(selection[0])["values"][0]
            self.root.clipboard_clear()
            self.root.clipboard_append(cmd)
            self.root.update()  # Обнови буфер
            messagebox.showinfo("Копировано", f"Команда '{cmd}' скопирована в буфер! Вставь в GMod-консоль (~).")
        else:
            messagebox.showwarning("Предупреждение", "Выбери команду в списке, лентяй! 😏")
    
    def refresh_list(self):
        # Здесь можно reload JSON или web-запрос, но для простоты — просто перезаполни
        self.populate_tree()

if __name__ == "__main__":
    root = tk.Tk()
    app = GModCommandHelper(root)
    root.mainloop()