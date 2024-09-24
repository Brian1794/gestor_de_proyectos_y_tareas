from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, session, flash
from datetime import datetime
import json
import pandas as pd
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Cambia esta clave secreta por una más segura

# Funciones para cargar y guardar empleados (usuarios)
def load_employees():
    try:
        with open('empleados.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_employees(employees):
    with open('empleados.json', 'w') as f:
        json.dump(employees, f)

# Funciones para cargar y guardar tareas
def load_tasks():
    try:
        with open('tasks.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_tasks(tasks):
    with open('tasks.json', 'w') as f:
        json.dump(tasks, f)

tasks = load_tasks()

# Decorator para requerir inicio de sesión
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Por favor, inicia sesión para acceder a esta página.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Rutas de autenticación
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        role = request.form['role']
        password = request.form['password']
        
        employees = load_employees()
        if any(emp['email'] == email for emp in employees):
            flash('Este correo ya está registrado.', 'error')
            return redirect(url_for('register'))
        
        new_employee = {
            'email': email,
            'name': name,
            'role': role,
            'password': generate_password_hash(password)
        }
        employees.append(new_employee)
        save_employees(employees)
        
        flash('Registro exitoso. Por favor, inicia sesión.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('menu'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        employees = load_employees()
        user = next((emp for emp in employees if emp['email'] == email), None)
        
        if user and check_password_hash(user['password'], password):
            session['user'] = {
                'email': user['email'],
                'name': user['name'],
                'role': user['role']
            }
            flash('Has iniciado sesión correctamente.', 'success')
            return redirect(url_for('menu'))
        else:
            flash('Correo o contraseña incorrectos.', 'error')
    
    return render_template('index.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('login'))

# Rutas para tareas
@app.route('/menu')
@login_required
def menu():
    return render_template('menu.html')

@app.route('/')
@login_required
def index():
    return render_template('tareas.html', tasks=tasks)

@app.route('/tareas')
@login_required
def tareas():
    tasks = load_tasks()  # Asegúrate de cargar las tareas aquí
    print(tasks)  # Imprimir tareas en la consola para verificar
    return render_template('tareas.html', tasks=tasks)

@app.route('/add', methods=['POST'])
@login_required
def add_task():
    task = {
        'name': request.form['name'],
        'responsible': request.form['responsible'],
        'start_date': request.form['start_date'],   
        'status': 'Pendiente',
        'details': request.form['details'],
        'completion_date': None
    }
    tasks.append(task)
    save_tasks(tasks)
    flash('Tarea añadida correctamente.', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:index>', methods=['POST'])
@login_required
def delete_task(index):
    if 0 <= index < len(tasks):
        del tasks[index]
        save_tasks(tasks)
        flash('Tarea eliminada correctamente.', 'success')
    else:
        flash('Tarea no encontrada.', 'error')
    return redirect(url_for('index'))

@app.route('/complete/<int:index>', methods=['POST'])
@login_required
def complete_task(index):
    if 0 <= index < len(tasks):
        tasks[index]['status'] = 'Finalizada'
        tasks[index]['completion_date'] = datetime.now().strftime('%Y-%m-%d')
        save_tasks(tasks)
        flash('Tarea marcada como completada.', 'success')
    else:
        flash('Tarea no encontrada.', 'error')
    return redirect(url_for('index'))

@app.route('/task/<int:index>')
@login_required
def task_detail(index):
    if 0 <= index < len(tasks):
        task = tasks[index]
        return render_template('task_detail.html', task=task, task_index=index)
    flash('Tarea no encontrada.', 'error')
    return redirect(url_for('index'))

@app.route('/projects')
@login_required
def projects():
    return render_template('projects.html')

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
@login_required
def edit_task(index):
    if 0 <= index < len(tasks):
        task = tasks[index]
        if request.method == 'POST':
            task['name'] = request.form['name']
            task['responsible'] = request.form['responsible']
            task['start_date'] = request.form['start_date']
            task['end_date'] = request.form['end_date'] or None
            task['details'] = request.form['details']
            save_tasks(tasks)
            flash('Tarea actualizada correctamente.', 'success')
            return redirect(url_for('task_detail', index=index))
        return render_template('edit_task.html', task=task, task_index=index)
    flash('Tarea no encontrada.', 'error')
    return redirect(url_for('index'))

@app.route('/summary')
@login_required
def summary():
    completed_tasks = [task for task in tasks if task['status'] == 'Finalizada']
    completed_tasks.sort(key=lambda x: x['completion_date'])
    
    data = {
        'labels': [task['completion_date'] for task in completed_tasks],
        'datasets': [{
            'label': 'Tareas Completadas',
            'data': [1 for _ in completed_tasks],
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1
        }]
    }
    
    responsible_data = {}
    for task in completed_tasks:
        responsible = task['responsible']
        if responsible in responsible_data:
            responsible_data[responsible] += 1
        else:
            responsible_data[responsible] = 1
    
    return render_template('summary.html', data=data, responsible_data=responsible_data)

@app.route('/download-excel')
@login_required
def download_excel():
    completed_tasks = [task for task in tasks if task['status'] == 'Finalizada']
    
    # Crear DataFrame de pandas
    df = pd.DataFrame(completed_tasks)
    
    # Crear archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Tareas Completadas')
    
    output.seek(0)  # Posiciona el puntero al principio del archivo
    
    # Enviar archivo como respuesta
    return send_file(output, as_attachment=True, download_name='tareas_completadas.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)