import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# In-memory storage for procedures
procedures = []

class Procedimiento:
    def __init__(self, nombre, fecha, responsable, eficacia, observaciones):
        self.id = len(procedures) + 1
        self.nombre = nombre
        self.fecha = fecha
        self.responsable = responsable
        self.eficacia = eficacia
        self.observaciones = observaciones
        self.fecha_creacion = datetime.now()

def validar_procedimiento(nombre, fecha, responsable, eficacia, observaciones):
    """Valida los datos del procedimiento"""
    errores = []
    
    if not nombre or len(nombre.strip()) < 3:
        errores.append("El nombre del procedimiento debe tener al menos 3 caracteres")
    
    if not fecha:
        errores.append("La fecha es obligatoria")
    else:
        try:
            datetime.strptime(fecha, '%Y-%m-%d')
        except ValueError:
            errores.append("La fecha debe tener un formato válido")
    
    if not responsable or len(responsable.strip()) < 2:
        errores.append("El responsable debe tener al menos 2 caracteres")
    
    try:
        eficacia_num = float(eficacia)
        if eficacia_num < 0 or eficacia_num > 100:
            errores.append("La eficacia debe estar entre 0 y 100")
    except (ValueError, TypeError):
        errores.append("La eficacia debe ser un número válido")
    
    if len(observaciones) > 500:
        errores.append("Las observaciones no pueden exceder 500 caracteres")
    
    return errores

@app.route('/')
def index():
    """Página principal con lista de procedimientos"""
    # Ordenar procedimientos por fecha (más recientes primero)
    procedures_sorted = sorted(procedures, key=lambda x: x.fecha, reverse=True)
    return render_template('index.html', procedures=procedures_sorted)

@app.route('/agregar', methods=['POST'])
def agregar_procedimiento():
    """Agregar un nuevo procedimiento"""
    try:
        nombre = request.form.get('nombre', '').strip()
        fecha = request.form.get('fecha', '')
        responsable = request.form.get('responsable', '').strip()
        eficacia = request.form.get('eficacia', '')
        observaciones = request.form.get('observaciones', '').strip()
        
        # Validar datos
        errores = validar_procedimiento(nombre, fecha, responsable, eficacia, observaciones)
        
        if errores:
            for error in errores:
                flash(error, 'error')
            return redirect(url_for('index'))
        
        # Crear nuevo procedimiento
        nuevo_procedimiento = Procedimiento(
            nombre=nombre,
            fecha=fecha,
            responsable=responsable,
            eficacia=float(eficacia),
            observaciones=observaciones
        )
        
        procedures.append(nuevo_procedimiento)
        flash('Procedimiento agregado exitosamente', 'success')
        
    except Exception as e:
        logging.error(f"Error al agregar procedimiento: {str(e)}")
        flash('Error interno del servidor. Por favor, intente nuevamente.', 'error')
    
    return redirect(url_for('index'))

@app.route('/eliminar/<int:procedure_id>')
def eliminar_procedimiento(procedure_id):
    """Eliminar un procedimiento específico"""
    try:
        global procedures
        procedures = [p for p in procedures if p.id != procedure_id]
        flash('Procedimiento eliminado exitosamente', 'success')
    except Exception as e:
        logging.error(f"Error al eliminar procedimiento: {str(e)}")
        flash('Error al eliminar el procedimiento', 'error')
    
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    """Manejo de errores 404"""
    return render_template('index.html', procedures=[], error="Página no encontrada"), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores 500"""
    logging.error(f"Error interno: {str(error)}")
    return render_template('index.html', procedures=[], error="Error interno del servidor"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
