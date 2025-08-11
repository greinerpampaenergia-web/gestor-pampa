import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "pampa-energia-dev-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///rutinas_cpb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    from models_task import Task, ProgressUpdate
    db.create_all()

@app.route('/')
def index():
    status_filter = request.args.get('status', 'all')
    responsible_filter = request.args.get('responsible', '')

    query = Task.query

    if status_filter == 'pending':
        query = query.filter(Task.completed == False)
    elif status_filter == 'completed':
        query = query.filter(Task.completed == True)

    if responsible_filter:
        query = query.filter(Task.responsible.ilike(f'%{responsible_filter}%'))

    tasks = query.order_by(Task.due_date.asc(), Task.created_at.desc()).all()
    responsible_persons = db.session.query(Task.responsible).distinct().all()
    responsible_list = [person[0] for person in responsible_persons if person[0]]

    return render_template('index.html', 
                           tasks=tasks, 
                           status_filter=status_filter,
                           responsible_filter=responsible_filter,
                           responsible_list=responsible_list)

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        responsible = request.form.get('responsible', '').strip()
        due_date_str = request.form.get('due_date', '')

        if not title:
            flash('El título es obligatorio', 'error')
            return render_template('add_task.html')

        if not responsible:
            flash('El responsable es obligatorio', 'error')
            return render_template('add_task.html')

        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Formato de fecha inválido', 'error')
                return render_template('add_task.html')

        task = Task(title=title, description=description, responsible=responsible, due_date=due_date)

        try:
            db.session.add(task)
            db.session.commit()
            flash('Tarea creada exitosamente', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear la tarea', 'error')
            app.logger.error(f'Error creating task: {e}')

    return render_template('add_task.html')

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        responsible = request.form.get('responsible', '').strip()
        due_date_str = request.form.get('due_date', '')

        if not title or not responsible:
            flash('Título y responsable son obligatorios', 'error')
            return render_template('edit_task.html', task=task)

        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Formato de fecha inválido', 'error')
                return render_template('edit_task.html', task=task)

        task.title = title
        task.description = description
        task.responsible = responsible
        task.due_date = due_date

        try:
            db.session.commit()
            flash('Tarea actualizada exitosamente', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar la tarea', 'error')
            app.logger.error(f'Error updating task: {e}')

    return render_template('edit_task.html', task=task)

@app.route('/toggle_task/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)

    try:
        task.completed = not task.completed
        task.completed_at = datetime.utcnow() if task.completed else None
        db.session.commit()
        flash(f'Tarea marcada como {"completada" if task.completed else "pendiente"}', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al actualizar el estado de la tarea', 'error')
        app.logger.error(f'Error toggling task: {e}')

    return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    try:
        db.session.delete(task)
        db.session.commit()
        flash('Tarea eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar la tarea', 'error')
        app.logger.error(f'Error deleting task: {e}')

    return redirect(url_for('index'))
