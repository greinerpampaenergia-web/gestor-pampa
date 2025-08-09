from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

tasks = []

@app.route('/')
def index():
    estado = request.args.get('estado')
    responsable = request.args.get('responsable')
    filtradas = tasks

    if estado:
        filtradas = [t for t in filtradas if t['estado'] == estado]
    if responsable:
        filtradas = [t for t in filtradas if t['responsable'] == responsable]

    return render_template('index.html', tasks=filtradas)

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        nueva_tarea = {
            'titulo': request.form['titulo'],
            'descripcion': request.form['descripcion'],
            'responsable': request.form['responsable'],
            'fecha_limite': request.form['fecha_limite'],
            'estado': 'pendiente',
            'avances': []
        }
        tasks.append(nueva_tarea)
        return redirect(url_for('index'))
    return render_template('add_task.html')

@app.route('/completar/<int:task_id>')
def completar(task_id):
    tasks[task_id]['estado'] = 'completada'
    return redirect(url_for('index'))

@app.route('/tarea/<int:task_id>')
def ver_tarea(task_id):
    tarea = tasks[task_id]
    return render_template('ver_tarea.html', tarea=tarea, task_id=task_id)

@app.route('/tarea/<int:task_id>/avance', methods=['POST'])
def agregar_avance(task_id):
    avance = {
        'descripcion': request.form['descripcion'],
        'fecha': request.form['fecha']
    }
    tasks[task_id]['avances'].append(avance)
    return redirect(url_for('ver_tarea', task_id=task_id))

if __name__ == '__main__':
    app.run(debug=True)
