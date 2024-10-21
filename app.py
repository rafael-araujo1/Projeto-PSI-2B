from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_mysqldb import MySQL
from MySQLdb import IntegrityError
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config.Config')

mysql = MySQL(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

# Função para verificar login
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
    return wrap

# Função para verificar se o e-mail já está em uso
def is_email_taken(email):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tb_users WHERE use_email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    return result is not None

# Rota inicial
@app.route('/')
def home():
    return render_template('index.html')

# Rota de registro

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        email = request.form['email']
        password = request.form['password']

        # Verifique se o e-mail já está em uso
        if is_email_taken(email):
            flash('Esse e-mail já está em uso. Escolha outro.')
            return redirect(url_for('register'))

        # Hash da senha
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Tente inserir o novo usuário
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO tb_users (use_username, use_email, use_password) VALUES (%s, %s, %s)", (username, email, hashed_password))
            mysql.connection.commit()

            # Enviar e-mail após o registro
            msg = Message('Cadastro feito',
                          recipients=[email])  # Envia para o e-mail do usuário
            msg.body = 'Seu cadastro foi realizado com sucesso!'
            mail.send(msg)

            flash('Registro realizado com sucesso! Você pode fazer login agora.','info')
            return redirect(url_for('login'))
        except IntegrityError:
            mysql.connection.rollback()
            flash('Erro ao registrar usuário.')
            return redirect(url_for('register'))
        finally:
            cursor.close()
    
    return render_template('register.html')



# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Buscar o usuário no banco de dados
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tb_users WHERE use_email = %s", [email])
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.check_password_hash(user[3], password):  # O campo 3 é a senha
            session['logged_in'] = True
            session['users_id'] = user[0]  # Armazenar o ID do usuário na sessão
            session['username'] = user[1]
            flash('Login efetuado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Falha no login. Verifique suas credenciais', 'danger')
    return render_template('login.html')

# Rota para o painel do usuário (dashboard)
@app.route('/dashboard', methods=["GET"])
@login_required
def dashboard():
    users_id = int(session['users_id'])
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT tas_id, tas_title, tas_description, tas_categoria, tas_status, tas_prioridade, tas_data_inicial, tas_data_limite 
        FROM tb_task 
        WHERE tas_use_id = %s
    """, (users_id,))
    tasks = cur.fetchall()
    cur.close()

    # FILTRAGEM
    filtros = []
    parametros = [users_id]

    # Status
    status = request.args.get('status')
    if status:
        filtros.append("tas_status = %s")
        parametros.append(status)

    # Data de Criação
    criadoI = request.args.get('criadoI')
    criadoF = request.args.get('criadoF')
    if criadoI and criadoF:
        filtros.append("tas_data_inicial BETWEEN %s AND %s")
        parametros.extend([criadoI, criadoF])
    
    # Data Limite (Prazo)
    limiteI = request.args.get('limiteI')
    limiteF = request.args.get('limiteF')
    if limiteI and limiteF:
        filtros.append("tas_data_limite BETWEEN %s AND %s")
        parametros.extend([limiteI, limiteF])
    
    # Prioridade
    prioridade = request.args.get('prioridade')
    if prioridade:
        filtros.append("tas_prioridade = %s")
        parametros.append(prioridade)

    # Categoria
    categoria = request.args.get('categoria')
    if categoria:
        filtros.append("tas_categoria = %s")
        parametros.append(categoria)

    # Descrição (Palavras-chave)
    descricao = request.args.get('descricao')
    if descricao:
        filtros.append("tas_description LIKE %s")
        parametros.append(f"%{descricao}%")  # Usando o % para fazer a busca por substring

    # SELECT DA CONSULTA
    consulta = """
        SELECT tas_id, tas_title, tas_description, tas_categoria, tas_status, tas_prioridade, tas_data_inicial, tas_data_limite 
        FROM tb_task 
        WHERE tas_use_id = %s
    """
    
    if filtros:
        consulta += " AND " + " AND ".join(filtros)

    cur = mysql.connection.cursor()
    cur.execute(consulta, tuple(parametros))
    tasks = cur.fetchall()
    cur.close()


    return render_template('dashboard.html', tasks=tasks)



# Rota para adicionar tarefa
@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        data_inicial = request.form["data-inicial"].replace("T", " ")
        data_limite = request.form["data-limite"].replace("T", " ")
        categoria = request.form['categoria']
        status = ''
        prioridade = request.form["prioridade"]
        users_id = session['users_id']

        data_inicialAux = datetime.strptime(data_inicial, "%Y-%m-%d %H:%M")
        data_limiteAux = datetime.strptime(data_limite, "%Y-%m-%d %H:%M")
        
        if data_limiteAux < data_inicialAux:
            status = "Pendente"
        else:
            status = "Em andamento"

        # Inserir a tarefa com a categoria selecionada
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tb_task (tas_use_id, tas_title, tas_description, tas_data_inicial, tas_data_limite, tas_categoria, tas_status, tas_prioridade) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (users_id, title, description, data_inicial, data_limite, categoria, status, prioridade))
        mysql.connection.commit()
        cur.close()

        flash('Tarefa adicionada com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    # Passa as categorias para o template
    return render_template('add_task.html')


# Rota para excluir tarefa
@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tb_task WHERE tas_id = %s AND tas_use_id = %s", (task_id, session['users_id']))
    mysql.connection.commit()
    cur.close()

    flash('Tarefa excluída com sucesso!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/concluir_task/<int:task_id>', methods=['POST'])
@login_required
def concluir_task(task_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE tb_task SET tas_status = 'Concluída' WHERE tas_id = %s AND tas_use_id = %s", (task_id, session['users_id']))
    mysql.connection.commit()
    cur.close()

    flash('Tarefa concluída com sucesso!', 'success')
    return redirect(url_for('dashboard'))

@app.route("/editar_task/<int:task_id>", methods=["POST"])
@login_required
def editar_task(task_id):
    if request.method == "POST":
        nova_descricao = request.form["editDescricao"]
        novo_status = request.form["editStatus"]
        novo_prazo = request.form["editPrazo"].replace("T", " ")

        cur = mysql.connection.cursor()
        cur.execute("UPDATE tb_task SET tas_description = %s, tas_status = %s, tas_data_limite = %s WHERE tas_id = %s AND tas_use_id = %s", (nova_descricao, novo_status, novo_prazo, task_id, session['users_id']))
        mysql.connection.commit()
        cur.close()

        flash('Tarefa editada com sucesso!', 'success')
        return redirect(url_for("dashboard"))

# Rota para logout
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Você saiu da sua conta!', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
