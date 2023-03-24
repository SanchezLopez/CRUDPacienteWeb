from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_mysqldb import MySQL
import pdfkit

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'nombre_de_tu_base_de_datos'
mysql = MySQL(app)

app.secret_key = "mysecretkey"


def get_paciente_by_id(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM pacientes WHERE id = %s", (id,))
    registro = cursor.fetchone()
    return registro



@app.route('/pacientes/delete/<int:id>', methods=['POST'])
def delete_paciente(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM pacientes WHERE id = %s', (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('pacientes'))


@app.route('/registro.html')
def registro():
    return render_template("registro.html")




@app.route('/add.html', methods=['POST'])
def add():
    if request.method == "POST":
        nombres = request.form["nombres"]
        apellido_pat = request.form["apellido_paterno"]
        apellido_mat = request.form["apellido_materno"]
        correo = request.form["correo"]
        password = request.form["contraseña"]
        telefono = request.form["telefono"]
        edad = request.form["edad"]
        tipo_sangre = request.form["tipo_sangre"]
        peso = request.form["peso"]
        estatura = request.form["estatura"]
        codigo_postal = request.form["codigo_postal"]
        cur = mysql.connection.cursor()
        
        
        cur.execute("SELECT correo FROM pacientes WHERE correo=%s", (correo,))
        result = cur.fetchone()
        if result:
            flash("Correo registrado.")
            return redirect(url_for("registro"))

        
        cur.execute("INSERT INTO pacientes (nombres, apellido_paterno, apellido_materno, correo, contraseña, telefono, edad, tipo_sangre, peso, estatura, codigo_postal) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (nombres, apellido_pat, apellido_mat, correo, password, telefono, edad, tipo_sangre, peso, estatura, codigo_postal))
        mysql.connection.commit()
        flash("Registro Completo!")
        return redirect(url_for("login"))



@app.route('/')
def index():
    return render_template("index.html")




@app.route('/Especialidades.html')
def specialties():
    return render_template("Especialidades.html")


@app.route('/Citas.html')
def about():
    return render_template("Citas.html")

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM pacientes WHERE correo=%s AND contraseña=%s", (correo, contraseña))
        record = cur.fetchone()
        cur.close()
        if record:
            session['loggedin'] = True
            session['correo'] = correo
            session['nombres'] = record[1]
            session['apellidos'] = record[2]
            return redirect(url_for('dashboard'))
        else:
            flash('Correo o contraseña incorrectos.')
    return render_template("login.html")


@app.route('/generate_pdf/<int:id>', methods=['POST'])
def generate_pdf(id):
    
    paciente = get_paciente_by_id(id)

    
    html = render_template('datos_paciente.html', paciente=paciente)

    
    pdf = pdfkit.from_string(html, False)

   
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=paciente_{id}.pdf'

    return response



@app.route('/pacientes')
def pacientes():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM nombre_de_tu_base_de_datos.pacientes')
    registros = cur.fetchall()
    cur.close()
    return render_template('lista_pacientes.html', registros=registros)

@app.route('/pacientes/edit/<int:id>', methods=['GET', 'POST'])
def edit_paciente(id):
    registro = get_paciente_by_id(id)
    if request.method == 'POST':
        nombres = request.form['nombres']
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']
        correo = request.form['correo']
        telefono = request.form['telefono']
        edad = request.form['edad']
        tipo_sangre = request.form['tipo_sangre']
        peso = request.form['peso']
        estatura = request.form['estatura']
        codigo_postal = request.form['codigo_postal']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE pacientes SET nombres = %s, apellido_paterno = %s, apellido_materno = %s, correo = %s, telefono = %s, edad = %s, tipo_sangre = %s, peso = %s, estatura = %s, codigo_postal = %s WHERE id = %s",
        (nombres, apellido_paterno, apellido_materno, correo, telefono, edad, tipo_sangre, peso, estatura, codigo_postal, id))
        mysql.connection.commit()
        cur.close()
        flash('Registro exitoso!')
        return redirect(url_for('pacientes'))
    return render_template('edit_paciente.html', registro=registro)



@app.route('/dashboard.html')
def dashboard():
    if 'loggedin' in session:
        correo = session['correo']
        nombres = session['nombres']
        apellidos = session['apellidos']

        # Obtener los registros de la tabla "pacientes"
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM pacientes"
        cursor.execute(query)
        pacientes = cursor.fetchall()
        cursor.close()

        return render_template('dashboard.html', correo=correo, nombres=nombres, apellidos=apellidos, pacientes=pacientes)
    return redirect(url_for('login'))


@app.route('/logout.html', methods= ["GET","POST"])
def logout():
    session.pop('correo', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port= 8000)

