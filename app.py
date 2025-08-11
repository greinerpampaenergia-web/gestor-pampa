import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "pampa-energia-dev-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///rutinas_cpb.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Import models after db initialization
from task_models import Task, ProgressUpdate

@app.route('/')
def index():
    return "App funcionando correctamente"

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
    
    # Get unique responsible persons for filter dropdown
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
        
        # Validation
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
        
        # Create new task
        task = Task()
        task.title = title
        task.description = description
        task.responsible = responsible
        task.due_date = due_date
        
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
        
        # Validation
        if not title:
            flash('El título es obligatorio', 'error')
            return render_template('edit_task.html', task=task)
        
        if not responsible:
            flash('El responsable es obligatorio', 'error')
            return render_template('edit_task.html', task=task)
        
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Formato de fecha inválido', 'error')
                return render_template('edit_task.html', task=task)
        
        # Update task
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
        if task.completed:
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None
        
        db.session.commit()
        
        status = "completada" if task.completed else "pendiente"
        flash(f'Tarea marcada como {status}', 'success')
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

@app.route('/task/<int:task_id>/progress')
def view_task_progress(task_id):
    task = Task.query.get_or_404(task_id)
    progress_updates = ProgressUpdate.query.filter_by(task_id=task_id).order_by(ProgressUpdate.created_at.desc()).all()
    return render_template('task_progress.html', task=task, progress_updates=progress_updates)

@app.route('/task/<int:task_id>/add_progress', methods=['GET', 'POST'])
def add_progress(task_id):
    task = Task.query.get_or_404(task_id)
    
    if request.method == 'POST':
        description = request.form.get('description', '').strip()
        created_by = request.form.get('created_by', '').strip()
        
        # Validation
        if not description:
            flash('La descripción del avance es obligatoria', 'error')
            return render_template('add_progress.html', task=task)
        
        if not created_by:
            flash('El nombre de quien registra el avance es obligatorio', 'error')
            return render_template('add_progress.html', task=task)
        
        # Create new progress update
        progress_update = ProgressUpdate()
        progress_update.task_id = task_id
        progress_update.description = description
        progress_update.created_by = created_by
        
        try:
            db.session.add(progress_update)
            db.session.commit()
            flash('Avance registrado exitosamente', 'success')
            return redirect(url_for('view_task_progress', task_id=task_id))
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar el avance', 'error')
            app.logger.error(f'Error creating progress update: {e}')
    
    return render_template('add_progress.html', task=task)

@app.route('/delete_progress/<int:progress_id>', methods=['POST'])
def delete_progress(progress_id):
    progress_update = ProgressUpdate.query.get_or_404(progress_id)
    task_id = progress_update.task_id
    
    try:
        db.session.delete(progress_update)
        db.session.commit()
        flash('Avance eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar el avance', 'error')
        app.logger.error(f'Error deleting progress update: {e}')
    
    return redirect(url_for('view_task_progress', task_id=task_id))

# Create tables
with app.app_context():
    db.create_all()
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)

