# Importar librerías necesarias
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear instancia de la aplicación Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'clave_secreta_por_defecto')

# Habilitar CORS para permitir peticiones desde otros orígenes
CORS(app)

# Configuración de la URL del backend API
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:3000')
# Exponer en app.config para que el template lo lea via {{ config.BACKEND_URL }}
app.config['BACKEND_URL'] = BACKEND_URL

# Ruta principal - muestra la página de inicio
@app.route('/')
def index():
    """
    Página principal que muestra todos los usuarios
    Obtiene la lista de usuarios desde el backend API
    """
    try:
        # Petición GET al backend para obtener todos los usuarios
        response = requests.get(f'{BACKEND_URL}/api/usuarios')
        
        if response.status_code == 200:
            usuarios = response.json()
            return render_template('index.html', usuarios=usuarios)
        else:
            flash('Error al obtener los usuarios del servidor', 'error')
            return render_template('index.html', usuarios=[])
            
    except requests.exceptions.RequestException as e:
        print(f'Error de conexión con el backend: {e}')
        flash('No se pudo conectar con el servidor backend', 'error')
        return render_template('index.html', usuarios=[])

# Ruta para mostrar el formulario de crear usuario
@app.route('/crear')
def crear_usuario_form():
    """
    Muestra el formulario para crear un nuevo usuario
    """
    return render_template('crear_usuario.html')

# Ruta para procesar la creación de un nuevo usuario
@app.route('/crear', methods=['POST'])
def crear_usuario():
    """
    Procesa el formulario de creación de usuario
    Envía los datos al backend API mediante POST
    """
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        edad = request.form.get('edad')
        
        # Validar que los campos requeridos no estén vacíos
        if not nombre or not email:
            flash('El nombre y el email son obligatorios', 'error')
            return redirect(url_for('crear_usuario_form'))
        
        # Preparar datos para enviar al backend
        datos_usuario = {
            'nombre': nombre,
            'email': email,
            'edad': int(edad) if edad else None
        }
        
        # Petición POST al backend para crear el usuario
        response = requests.post(
            f'{BACKEND_URL}/api/usuarios',
            json=datos_usuario,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('index'))
        else:
            error_data = response.json()
            flash(f'Error al crear usuario: {error_data.get("error", "Error desconocido")}', 'error')
            return redirect(url_for('crear_usuario_form'))
            
    except requests.exceptions.RequestException as e:
        print(f'Error de conexión con el backend: {e}')
        flash('No se pudo conectar con el servidor backend', 'error')
        return redirect(url_for('crear_usuario_form'))
    except ValueError as e:
        flash('La edad debe ser un número válido', 'error')
        return redirect(url_for('crear_usuario_form'))

# Ruta para mostrar el formulario de editar usuario
@app.route('/editar/<int:usuario_id>')
def editar_usuario_form(usuario_id):
    """
    Muestra el formulario para editar un usuario existente
    """
    try:
        # Obtener los datos del usuario desde el backend
        response = requests.get(f'{BACKEND_URL}/api/usuarios')
        
        if response.status_code == 200:
            usuarios = response.json()
            # Buscar el usuario por ID
            usuario = next((u for u in usuarios if u['id'] == usuario_id), None)
            
            if usuario:
                return render_template('editar_usuario.html', usuario=usuario)
            else:
                flash('Usuario no encontrado', 'error')
                return redirect(url_for('index'))
        else:
            flash('Error al obtener los datos del usuario', 'error')
            return redirect(url_for('index'))
            
    except requests.exceptions.RequestException as e:
        print(f'Error de conexión con el backend: {e}')
        flash('No se pudo conectar con el servidor backend', 'error')
        return redirect(url_for('index'))

# Ruta para procesar la actualización de un usuario
@app.route('/editar/<int:usuario_id>', methods=['POST'])
def editar_usuario(usuario_id):
    """
    Procesa el formulario de edición de usuario
    Envía los datos actualizados al backend API mediante PUT
    """
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        edad = request.form.get('edad')
        
        # Validar campos requeridos
        if not nombre or not email:
            flash('El nombre y el email son obligatorios', 'error')
            return redirect(url_for('editar_usuario_form', usuario_id=usuario_id))
        
        # Preparar datos para enviar al backend
        datos_usuario = {
            'nombre': nombre,
            'email': email,
            'edad': int(edad) if edad else None
        }
        
        # Petición PUT al backend para actualizar el usuario
        response = requests.put(
            f'{BACKEND_URL}/api/usuarios/{usuario_id}',
            json=datos_usuario,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('index'))
        else:
            error_data = response.json()
            flash(f'Error al actualizar usuario: {error_data.get("error", "Error desconocido")}', 'error')
            return redirect(url_for('editar_usuario_form', usuario_id=usuario_id))
            
    except requests.exceptions.RequestException as e:
        print(f'Error de conexión con el backend: {e}')
        flash('No se pudo conectar con el servidor backend', 'error')
        return redirect(url_for('editar_usuario_form', usuario_id=usuario_id))
    except ValueError as e:
        flash('La edad debe ser un número válido', 'error')
        return redirect(url_for('editar_usuario_form', usuario_id=usuario_id))

# Ruta para eliminar un usuario
@app.route('/eliminar/<int:usuario_id>', methods=['POST'])
def eliminar_usuario(usuario_id):
    """
    Elimina un usuario mediante petición DELETE al backend API
    """
    try:
        # Petición DELETE al backend para eliminar el usuario
        response = requests.delete(f'{BACKEND_URL}/api/usuarios/{usuario_id}')
        
        if response.status_code == 200:
            flash('Usuario eliminado exitosamente', 'success')
        else:
            error_data = response.json()
            flash(f'Error al eliminar usuario: {error_data.get("error", "Error desconocido")}', 'error')
            
    except requests.exceptions.RequestException as e:
        print(f'Error de conexión con el backend: {e}')
        flash('No se pudo conectar con el servidor backend', 'error')
    
    return redirect(url_for('index'))

# Manejo de errores 404
@app.errorhandler(404)
def pagina_no_encontrada(error):
    """
    Maneja el error 404 - Página no encontrada
    """
    return render_template('404.html'), 404

# Manejo de errores 500
@app.errorhandler(500)
def error_servidor(error):
    """
    Maneja el error 500 - Error interno del servidor
    """
    return render_template('500.html'), 500

# Punto de entrada principal
if __name__ == '__main__':
    # Obtener el puerto desde variables de entorno o usar 5000 por defecto
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f'Iniciando servidor Flask en el puerto {port}')
    print(f'URL del backend: {BACKEND_URL}')
    
    # Iniciar el servidor Flask
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
