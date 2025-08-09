import os
from flask import Flask, render_template

app = Flask(__name__)

# Simulación de lista de tareas
tareas = [
    {
        'id': 1,
        'titulo': 'Pantalla PI Arranque Unidades',
        'descripcion': 'Armar una pantalla en PI Vision en dónde se pueda visualizar todos los hitos del arranque de las unidades',
        'responsable': 'Gonzalo Reiner',
        'fecha_creacion': '08/08/2023 18:36',
        'fecha_entrega': '31/10/2025',
        'estado': 'pendiente',
        'progreso': 0
    }
]

# Cálculo de contadores
total = len(tareas)
completadas = sum(1 for t in tareas if t['estado'] == 'completada')
pendientes = sum(1 for t in tareas if t['estado'] == 'pendiente')
vencidas = sum(1 for t in tareas if t['estado'] == 'vencida')

# Lista de responsables únicos
responsables = sorted(set(t['responsable'] for t in tareas))

@app.route('/')
def index():
    return render_template('index.html',
                           tareas=tareas,
                           total=total,
                           completadas=completadas,
                           pendientes=pendientes,
                           vencidas=vencidas,
                           responsables=responsables)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

