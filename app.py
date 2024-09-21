from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_mysqldb import MySQL
from MySQLdb import IntegrityError
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from functools import wraps

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
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
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
            cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
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
        cur.execute("SELECT * FROM users WHERE email = %s", [email])
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
@app.route('/dashboard')
@login_required
def dashboard():
    users_id = session['users_id']
    cur = mysql.connection.cursor()

    # Alteração na query para buscar o nome da categoria junto com as tarefas
    cur.execute("""
        SELECT Task.id, Task.title, Task.description, Category.name 
        FROM Task 
        JOIN Category ON Task.category_id = Category.id
        WHERE Task.users_id = %s
    """, (users_id,))
    tasks = cur.fetchall()
    cur.close()

    return render_template('dashboard.html', tasks=tasks)


# Rota para adicionar tarefa
@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    # Busca as categorias no banco de dados para exibir no select
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM Category")
    categories = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category_id = request.form['category_id']  # Obtém o ID da categoria selecionada
        users_id = session['users_id']

        # Inserir a tarefa com a categoria selecionada
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Task (users_id, title, description, category_id) VALUES (%s, %s, %s, %s)",
                    (users_id, title, description, category_id))
        mysql.connection.commit()
        cur.close()

        flash('Tarefa adicionada com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    # Passa as categorias para o template
    return render_template('add_task.html', categories=categories)


# Rota para excluir tarefa
@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Task WHERE id = %s AND users_id = %s", (task_id, session['users_id']))
    mysql.connection.commit()
    cur.close()

    flash('Tarefa excluída com sucesso!', 'success')
    return redirect(url_for('dashboard'))

# Rota para logout
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Você saiu da sua conta!', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
