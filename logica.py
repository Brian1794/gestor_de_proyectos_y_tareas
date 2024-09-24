import tkinter as tk
from tkinter import messagebox, simpledialog, Scrollbar, Frame
import json

class TaskManager:
    def __init__(self, filename='tasks.json'):
        self.filename = filename
        self.load_tasks()

    def load_tasks(self):
        try:
            with open(self.filename, 'r') as file:
                self.tasks = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.tasks = []

    def save_tasks(self):
        with open(self.filename, 'w') as file:
            json.dump(self.tasks, file)

    def add_task(self, name, description, start_date, end_date):
        task = {
            'name': name,
            'description': description,
            'start_date': start_date,
            'end_date': end_date,
            'status': 'Pending'
        }
        self.tasks.append(task)
        self.save_tasks()

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self.save_tasks()

    def edit_task(self, index, name, description, start_date, end_date):
        if 0 <= index < len(self.tasks):
            self.tasks[index] = {
                'name': name,
                'description': description,
                'start_date': start_date,
                'end_date': end_date,
                'status': 'Pending'
            }
            self.save_tasks()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Tareas y Proyectos")
        self.root.geometry("700x500")
        self.root.configure(bg="#f0f0f0")

        self.task_manager = TaskManager()

        self.create_widgets()

    def create_widgets(self):
        # Frame del menú
        self.menu_frame = tk.Frame(self.root, bg="#4CAF50")
        self.menu_frame.pack(fill=tk.X)

        self.add_task_button = tk.Button(self.menu_frame, text="Agregar Tarea", command=self.add_task, bg="#4CAF50", fg="white", relief=tk.FLAT)
        self.add_task_button.pack(side=tk.LEFT, padx=5, pady=10)

        self.view_tasks_button = tk.Button(self.menu_frame, text="Mostrar Tareas", command=self.display_tasks, bg="#2196F3", fg="white", relief=tk.FLAT)
        self.view_tasks_button.pack(side=tk.LEFT, padx=5, pady=10)

        self.edit_task_button = tk.Button(self.menu_frame, text="Editar Tarea", command=self.edit_task, bg="#FFC107", fg="white", relief=tk.FLAT)
        self.edit_task_button.pack(side=tk.LEFT, padx=5, pady=10)

        self.delete_task_button = tk.Button(self.menu_frame, text="Eliminar Tarea", command=self.delete_task, bg="#F44336", fg="white", relief=tk.FLAT)
        self.delete_task_button.pack(side=tk.LEFT, padx=5, pady=10)

        # Scrollable Text Area
        self.text_frame = Frame(self.root)
        self.text_frame.pack(pady=10)

        self.text_area = tk.Text(self.text_frame, width=80, height=20, bg="#ffffff", font=("Arial", 12), wrap=tk.WORD)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH)

        self.scrollbar = Scrollbar(self.text_frame, command=self.text_area.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_area.config(yscrollcommand=self.scrollbar.set)

    def add_task(self):
        name = simpledialog.askstring("Nombre de la Tarea", "Ingresa el nombre de la tarea:")
        if not name:
            return
        
        description = simpledialog.askstring("Descripción", "Ingresa la descripción de la tarea:")
        if not description:
            return
        
        start_date = simpledialog.askstring("Fecha de Inicio", "Ingresa la fecha de inicio (YYYY-MM-DD):")
        if not start_date:
            return
        
        end_date = simpledialog.askstring("Fecha de Cierre", "Ingresa la fecha de cierre (YYYY-MM-DD):")
        if not end_date:
            return
        
        self.task_manager.add_task(name, description, start_date, end_date)
        messagebox.showinfo("Éxito", "Tarea agregada con éxito.")

    def display_tasks(self):
        self.text_area.delete(1.0, tk.END)  # Limpiar el área de texto
        for i, task in enumerate(self.task_manager.tasks, start=1):
            self.text_area.insert(tk.END, f"Tarea {i}:\n")
            self.text_area.insert(tk.END, f"  Nombre: {task['name']}\n")
            self.text_area.insert(tk.END, f"  Descripción: {task['description']}\n")
            self.text_area.insert(tk.END, f"  Fecha de Inicio: {task['start_date']}\n")
            self.text_area.insert(tk.END, f"  Fecha de Cierre: {task['end_date']}\n")
            self.text_area.insert(tk.END, f"  Estado: {task['status']}\n")
            self.text_area.insert(tk.END, "-" * 50 + "\n")  # Separador

    def edit_task(self):
        task_index = simpledialog.askinteger("Editar Tarea", "Ingresa el número de la tarea a editar:")
        if task_index is None or task_index < 1 or task_index > len(self.task_manager.tasks):
            messagebox.showerror("Error", "Número de tarea inválido.")
            return
        
        task_index -= 1  # Ajustar el índice
        name = simpledialog.askstring("Nombre de la Tarea", "Ingresa el nuevo nombre de la tarea:")
        description = simpledialog.askstring("Descripción", "Ingresa la nueva descripción de la tarea:")
        start_date = simpledialog.askstring("Fecha de Inicio", "Ingresa la nueva fecha de inicio (YYYY-MM-DD):")
        end_date = simpledialog.askstring("Fecha de Cierre", "Ingresa la nueva fecha de cierre (YYYY-MM-DD):")
        
        self.task_manager.edit_task(task_index, name, description, start_date, end_date)
        messagebox.showinfo("Éxito", "Tarea editada con éxito.")

    def delete_task(self):
        task_index = simpledialog.askinteger("Eliminar Tarea", "Ingresa el número de la tarea a eliminar:")
        if task_index is None or task_index < 1 or task_index > len(self.task_manager.tasks):
            messagebox.showerror("Error", "Número de tarea inválido.")
            return
        
        task_index -= 1  # Ajustar el índice
        self.task_manager.delete_task(task_index)
        messagebox.showinfo("Éxito", "Tarea eliminada con éxito.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()