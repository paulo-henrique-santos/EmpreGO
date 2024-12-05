from flask import Flask, render_template, request, redirect, session, send_from_directory
from mysql.connector import Error
from config import *
from db_functions import *
import os

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'uploads/'

#ROTA INICIAL
@app.route('/')
def index():
    if session:
        if 'adm' in session:
            login = 'adm'
        else:
            login = 'empresa'
    else:
        login = False

    try:
        comandoSQL = '''
        SELECT vaga.*, empresa.Nome_Empresa 
        FROM vaga 
        JOIN empresa ON vaga.Id_Empresa = empresa.Id_Empresa
        WHERE vaga.Status = 'ativa'
        ORDER BY vaga.Id_Vaga DESC;
        '''
        conexao, cursor = conectar_db()
        cursor.execute(comandoSQL)
        vagas = cursor.fetchall()
        return render_template('index.html', vagas=vagas, login=login)
    except Error as erro:
        return f"ERRO! Erro de Banco de Dados: {erro}"
    except Exception as erro:
        return f"ERRO! Outros erros: {erro}"
    finally:
        encerrar_db(cursor, conexao)


#ROTA DO ADM (O dono do site ou quem for superior do que o próprio criador)
@app.route('/adm')
def adm():
    #Se não houver sessão ativa
    if not session:
        return redirect('/login')
    #Se não for o administrador
    if not 'adm' in session:
        return redirect('/empresa')
  
    try:
        conexao, cursor = conectar_db()
        comandoSQL = 'SELECT * FROM Empresa WHERE Status = "ativa"'
        cursor.execute(comandoSQL)
        empresas_ativas = cursor.fetchall()

        comandoSQL = 'SELECT * FROM Empresa WHERE Status = "inativa"'
        cursor.execute(comandoSQL)
        empresas_inativas = cursor.fetchall()

        return render_template('adm.html', empresas_ativas=empresas_ativas, empresas_inativas=empresas_inativas)
    except Error as erro:
        return f"ERRO! Erro de Banco de Dados: {erro}"
    except Exception as erro:
        return f"ERRO! Outros erros: {erro}"
    finally:
        encerrar_db(cursor, conexao)

# ROTA DA PÁGINA DE LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session:
        if 'adm' in session:
            return redirect('/adm')
        else:
            return redirect('/empresa')

    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        if not email or not senha:  # Corrigi aqui para verificar ambos os campos corretamente
            erro = "Os campos precisam estar preenchidos!"
            return render_template('login.html', msg_erro=erro)

        if email == MASTER_EMAIL and senha == MASTER_PASSWORD:
            session['adm'] = True
            return redirect('/adm')

        try:
            conexao, cursor = conectar_db()
            comandoSQL = 'SELECT * FROM empresa WHERE email = %s AND senha = %s'
            cursor.execute(comandoSQL, (email, senha))
            empresa = cursor.fetchone()

            if not empresa:
                return render_template('login.html', msgerro='E-mail e/ou senha estão errados!')

            # Acessar os dados como dicionário
            if empresa['Status'] == 'Inativa':
                return render_template('login.html', msgerro='Empresa desativada! Procure o administrador!')

            session['Id_Empresa'] = empresa['Id_Empresa']
            session['Nome_Empresa'] = empresa['Nome_Empresa']
            return redirect('/empresa')
        
        except Error as erro:
            return f"ERRO! Erro de Banco de Dados: {erro}"
        except Exception as erro:
            return f"ERRO! Outros erros: {erro}"
        finally:
            encerrar_db(cursor, conexao)

#ROTA DE LOGOUT (ENCERRA AS SESSÕES)
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ROTA PARA ABRIR E RECEBER AS INFORMAÇÕES DE UMA NOVA EMPRESA
@app.route("/cadastrar_empresa", methods=['POST','GET'])
def cadastrar_empresa():
    # Verifica se tem alguem logado
    if not session:
        return redirect('/login')
    
    # Se nõa for o ADM, deve ser a empresa
    if 'adm' not in session:
        return redirect('/empresa')

    if request.method == 'GET':
        return render_template('cadastrar_empresa.html')

    #Tratando os dados vindos do formulario
    if request.method == 'POST':
        nome_empresa = request.form['nome_empresa']
        cnpj = limpar_input(request.form['cnpj'])
        telefone = limpar_input(request.form['telefone'])
        email = request.form['email']
        senha = request.form['senha']

        # Verifica se todos os campos estão preechidos
        if not nome_empresa or not cnpj or not telefone or not email or not senha:
            return render_template('cadastrar_empresa.html', msg_erro="Todos os campos são obrigatórios!!")

        try:
            conexao, cursor = conectar_db()
            comandoSQL = 'INSERT INTO empresa (Nome_Empresa, cnpj, telefone, email, senha) VALUES (%s,%s,%s,%s,%s)'
            cursor.execute(comandoSQL, (nome_empresa, cnpj, telefone, email, senha))
            conexao.commit() # Para comandos SQL
            return redirect('/adm')
        
        #Erro de usuario tentar entrar com um email que já existe!
        except Error as erro:
            # Erro número (o "erro")
            if erro.errno == 1062:
                return render_template('cadastrar_empresa.html', msg_erro="Esse e-mail já existe!!")
            
            else:
                return f"Erro de BD: {erro}"
            
        except Exception as erro:
            return f"Erro de BackEnd: {erro}"
        finally:
            encerrar_db(cursor, conexao)

#ROTA PARA EDITAR EMPRESA
@app.route("/editar_empresa/<int:id_empresa>", methods=['GET','POST'])
def editar_empresa(id_empresa):
    if not session:
        return redirect('/login')
    
    if not session['adm']:
        return redirect('/login')
    
    if request.method == 'GET':
        try:
            conexao, cursor = conectar_db()
            comandoSQL = 'SELECT * FROM Empresa WHERE Id_Empresa = %s'
            cursor.execute(comandoSQL, (id_empresa,))
            empresa = cursor.fetchone()
            return render_template('editar_empresa.html', empresa=empresa)
        except Error as erro:
            return f"Erro de BD: {erro}"
        except Exception as erro:
            return f"Erro de BackEnd: {erro}"
        finally:
            encerrar_db(cursor, conexao)

     #Tratando os dados vindos do formulario
    if request.method == 'POST':
        nome_empresa = request.form['nome_empresa']
        cnpj = limpar_input(request.form['cnpj'])
        telefone = limpar_input(request.form['telefone'])
        email = request.form['email']
        senha = request.form['senha']
        # Verifica se todos os campos estão preechidos
        if not nome_empresa or not cnpj or not telefone or not email or not senha:
            return render_template('editar_empresa.html', empresa=empresa, msg_erro='Todos os campos são obrigatórios!!')

        try:
            conexao, cursor = conectar_db()
            comandoSQL = '''

            UPDATE Empresa
            SET Nome_Empresa = %s, CNPJ = %s, Telefone = %s, Email = %s, Senha = %s WHERE Id_Empresa = %s;

            '''
            cursor.execute(comandoSQL, (nome_empresa, cnpj, telefone, email, senha, id_empresa))
            conexao.commit() # Para comandos SQL
            return redirect('/adm')

        #Erro de usuario tentar entrar com um email que já existe!
        except Error as erro:
            if erro.erro == 1062:
                return render_template('editar_empresa.html', msg_erro="Esse e-mail já existe!!")
            
            else:
                return f"Erro de BD: {erro}"
            
        except Exception as erro:
            return f"Erro de BackEnd: {erro}"
        finally:
            encerrar_db(cursor, conexao)

#ROTA PARA ATIVAR E DESATIVAR A EMPRESA
@app.route('/status_empresa/<int:id_empresa>')
def status(id_empresa):
    if not session:
        return redirect('/login')
    
    if not session['adm']:
        return redirect('/login')
    
    try:
        conexao, cursor = conectar_db()
        comandoSQL = 'SELECT Status FROM empresa WHERE Id_Empresa = %s'
        cursor.execute(comandoSQL, (id_empresa,))
        status_empresa = cursor.fetchone()
        if status_empresa['Status'] == 'Ativa':
            novo_status = 'inativa'
        else:
            novo_status = 'Ativa'
        
        comandoSQL = 'UPDATE Empresa SET Status =%s WHERE Id_Empresa =%s'
        cursor.execute(comandoSQL, (novo_status, id_empresa))
        conexao.commit()

        #Se a empresa estiver sendo desativada, as vagas também serão
        if novo_status == 'inativa':
            comandoSQL = 'UPDATE Vaga SET Status = %s WHERE Id_Empresa = %s'
            cursor.execute(comandoSQL, (novo_status,id_empresa))
            conexao.commit()
        return redirect('/adm')
    
    except Error as erro:
        return f"Erro de BD: {erro}"
    except Exception as erro:
        return f"Erro de BackEnd: {erro}"
    finally:
        encerrar_db(cursor, conexao)

@app.route('/excluir_empresa/<int:id_empresa>')
def excluir_empresa(id_empresa):
    if not session:
        return redirect('/login')
    
    if not session['adm']:
        return redirect('/login')
    
    try:
        conexao, cursor = conectar_db()
        comandoSQL = 'DELETE FROM vaga WHERE Id_Empresa =%s'
        cursor.execute(comandoSQL, (id_empresa,))
        conexao.commit()

        comandoSQL = 'DELETE FROM empresa WHERE Id_Empresa =%s'
        cursor.execute(comandoSQL, (id_empresa,))
        conexao.commit()
        return redirect('/adm')
    
    except Error as erro:
        return f"Erro de BD: {erro}"
    except Exception as erro:
        return f"Erro de BackEnd: {erro}"
    finally:
        encerrar_db(cursor, conexao)


#ROTA DA PÁGINA DE GESTÃO DAS EMPRESAS
@app.route('/empresa')
def empresa():
    #Verifica se não tem sessão ativa
    if not session:
        return redirect('/login')
    #Verifica se o adm está tentando acessar indevidamente
    if 'adm' in session:
        return redirect('/adm')

    id_empresa = session['Id_Empresa']
    nome_empresa = session['Nome_Empresa']

    try:
        conexao, cursor = conectar_db()
        comandoSQL = 'SELECT * FROM Vaga WHERE Id_Empresa = %s AND Status = "Ativa" ORDER BY Id_Vaga DESC'
        cursor.execute(comandoSQL, (id_empresa,))
        vagas_ativas = cursor.fetchall()

        comandoSQL = 'SELECT * FROM Vaga WHERE Id_Empresa = %s AND Status = "Inativa" ORDER BY Id_Vaga DESC'
        cursor.execute(comandoSQL, (id_empresa,))
        vagas_inativas = cursor.fetchall()

        return render_template('empresa.html', nome_empresa=nome_empresa, vagas_ativas=vagas_ativas, vagas_inativas=vagas_inativas)         
    except Error as erro:
        return f"ERRO! Erro de Banco de Dados: {erro}"
    except Exception as erro:
        return f"ERRO! Outros erros: {erro}"
    finally:
        encerrar_db(cursor, conexao)

#ROTA PARA EDITAR A VAGA
@app.route('/editar_vaga/<int:id_vaga>', methods=['GET','POST'])
def editarvaga(id_vaga):
    #Verifica se não tem sessão ativa
    if not session:
        return redirect('/login')
    #Verifica se o adm está tentando acessar indevidamente
    if 'adm' in session:
        return redirect('/adm')

    if request.method == 'GET':
        try:
            conexao, cursor = conectar_db()
            comandoSQL = 'SELECT * FROM vaga WHERE Id_Vaga = %s;'
            cursor.execute(comandoSQL, (id_vaga,))
            vaga = cursor.fetchone()
            return render_template('editar_vaga.html', vaga=vaga)
        except Error as erro:
            return f"ERRO! Erro de Banco de Dados: {erro}"
        except Exception as erro:
            return f"ERRO! Outros erros: {erro}"
        finally:
            encerrar_db(cursor, conexao)

    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        formato = request.form['formato']
        tipo = request.form['tipo']
        local = request.form['local']
        salario = limpar_input(request.form['salario'])

        if not titulo or not descricao or not formato or not tipo:
            return redirect('/empresa')
        
        try:
            conexao, cursor = conectar_db()
            comandoSQL = '''
            UPDATE vaga SET Titulo = %s, Descricao = %s, Formato = %s, Tipo = %s, Local = %s, Salario = %s
            WHERE Id_Vaga = %s;
            '''
            cursor.execute(comandoSQL, (titulo, descricao, formato, tipo, local, salario, id_vaga))
            conexao.commit()
            return redirect('/empresa')
        except Error as erro:
            return f"ERRO! Erro de Banco de Dados: {erro}"
        except Exception as erro:
            return f"ERRO! Outros erros: {erro}"
        finally:
            encerrar_db(cursor, conexao)

#ROTA PARA ALTERAR O STATUS DA VAGA
@app.route("/status_vaga/<int:id_vaga>")
def statusvaga(id_vaga):
    #Verifica se não tem sessão ativa
    if not session:
        return redirect('/login')
    #Verifica se o adm está tentando acessar indevidamente
    if 'adm' in session:
        return redirect('/adm')

    try:
        conexao, cursor = conectar_db()
        comandoSQL = 'SELECT Status FROM Vaga WHERE Id_Vaga = %s;'
        cursor.execute(comandoSQL, (id_vaga,))
        vaga = cursor.fetchone()
        if vaga['Status'] == 'Ativa':
            status = 'Inativa'
        else:
            status = 'Ativa'

        comandoSQL = 'UPDATE Vaga SET Status = %s WHERE Id_Vaga = %s'
        cursor.execute(comandoSQL, (status, id_vaga))
        conexao.commit()
        return redirect('/empresa')

    except Error as erro:
        return f"ERRO! Erro de Banco de Dados: {erro}"
    except Exception as erro:
        return f"ERRO! Outros erros: {erro}"
    finally:
        encerrar_db(cursor, conexao)

    #ROTA PARA EXCLUIR VAGA
@app.route("/excluir_vaga/<int:id_vaga>")
def excluirvaga(id_vaga):
    #Verifica se não tem sessão ativa
    if not session:
        return redirect('/login')
    #Verifica se o adm está tentando acessar indevidamente
    if 'adm' in session:
        return redirect('/adm')

    try:
        conexao, cursor = conectar_db()
        comandoSQL = 'DELETE FROM Vaga WHERE Id_Vaga = %s AND Status = "Inativa"'
        cursor.execute(comandoSQL, (id_vaga,))
        conexao.commit()
        return redirect('/empresa')
    except Error as erro:
        return f"ERRO! Erro de Banco de Dados: {erro}"
    except Exception as erro:
        return f"ERRO! Outros erros: {erro}"
    finally:
        encerrar_db(cursor, conexao)

@app.route('/cadastrar_vaga', methods=['POST','GET'])
def cadastrar_vaga():
    #Verifica se não tem sessão ativa
    if not session:
        return redirect('/login')
    #Verifica se o adm está tentando acessar indevidamente
    if 'adm' in session:
        return redirect('/adm')
    
    if request.method == 'GET':
        return render_template('cadastrar_vaga.html')
    
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        formato = request.form['formato']
        tipo = request.form['tipo']
        local = ''
        local = request.form['local']
        salario = ''
        salario = limpar_input(request.form['salario'])
        id_empresa = session['Id_Empresa']

        if not titulo or not descricao or not formato or not tipo:
            return render_template('cadastrar_vaga.html', msg_erro="Os campos obrigatório precisam estar preenchidos!")
        
        try:
            conexao, cursor = conectar_db()
            comandoSQL = '''
            INSERT INTO Vaga (titulo, descricao, formato, tipo, local, salario, Id_Empresa)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(comandoSQL, (titulo, descricao, formato, tipo, local, salario, id_empresa))
            conexao.commit()
            return redirect('/empresa')
        except Error as erro:
            return f"ERRO! Erro de Banco de Dados: {erro}"
        except Exception as erro:
            return f"ERRO! Outros erros: {erro}"
        finally:
            encerrar_db(cursor, conexao)
            
#ROTA PARA VER DETALHES DA VAGA
@app.route("/sobre_vaga/<int:id_vaga>")
def sobre_vaga(id_vaga):
    try:
        comandoSQL = '''
        SELECT vaga.*, empresa.nome_empresa 
        FROM vaga 
        JOIN empresa ON vaga.id_empresa = empresa.id_empresa
        WHERE vaga.id_vaga = %s;
        '''
        conexao, cursor = conectar_db()
        cursor.execute(comandoSQL, (id_vaga,))
        vaga = cursor.fetchone()
        
        if not vaga:
            return redirect('/')
        
        return render_template('sobre_vaga.html', vaga=vaga)
    except Error as erro:
        return f"ERRO! Erro de Banco de Dados: {erro}"
    except Exception as erro:
        return f"ERRO! Outros erros: {erro}"
    finally:
        encerrar_db(cursor, conexao)

#ROTA PARA O ERRO 404(PÁGINA NÃO ENCONTRADA)
@app.errorhandler(404)
def not_found(error):
    return render_template('erro404.html'), 404

@app.route("/candidatar/<int:id_vaga>", methods=['GET','POST'])
def candidatar(id_vaga):

    if session:

        return redirect('/')
    
    if request.method == 'GET':
        try:
            conexao, cursor = conectar_db()
            comandoSQL = 'SELECT * FROM Vaga WHERE Id_Vaga = %s'
            cursor.execute(comandoSQL, (id_vaga,))
            vaga = cursor.fetchone()
            return render_template('candidatar.html', vaga=vaga)
        except Error as erro:
            return f"Erro de BD: {erro}"
        except Exception as erro:
            return f"Erro de BackEnd: {erro}"
        finally:
            encerrar_db(cursor, conexao)

    if request.method == 'POST':

        nome_candidato = request.form['nome_candidato']
        telefone = limpar_input(request.form['telefone'])
        email = request.form['email']
        file = request.files['file']

        if file.filename == '':
            msg = f"Nenhum arquivo enviado!"
            return render_template('candidatar.html', msg=msg)

        try:
            conexao, cursor = conectar_db()
            nome_arquivo = f"{id_vaga}_{file.filename}"
            comandoSQL = "INSERT INTO candidato (nome, email, telefone, curriculo, id_vaga) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(comandoSQL, (nome_candidato, email, telefone, nome_arquivo, id_vaga))
            conexao.commit()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo))

            return redirect('/')

        except Error as erro:
            return f"Erro de BD: {erro}"
        except Exception as erro:
            return f"Erro de BackEnd: {erro}"
        finally:
            encerrar_db(cursor, conexao)

@app.route("/curriculo/<int:id_vaga>")
def curriculo(id_vaga):

    if not session:
        return redirect('/')

    try:
        conexao, cursor = conectar_db()
        comandoSQL = '''
        SELECT c.*, v.Id_Empresa FROM vaga v JOIN candidato c ON c.id_vaga = v.id_vaga WHERE c.id_vaga = %s
        '''
        cursor.execute(comandoSQL, (id_vaga,))
        curriculo = cursor.fetchall()

        if not curriculo:
            
            return redirect('/empresa')

        if session['Id_Empresa'] != curriculo[0]['Id_Empresa']:
            
            return redirect('/empresa')

        return render_template('curriculo.html', curriculo=curriculo)

    except Error as erro:
        return f"Erro de BD: {erro}"
    except Exception as erro:
        return f"Erro de BackEnd: {erro}"
    finally:
        encerrar_db(cursor, conexao)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False)

@app.route('/delete/<filename>')
def delete_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.remove(file_path)

        conexao, cursor = conectar_db()
        comandoSQL = 'DELETE FROM candidato WHERE curriculo = %s'
        cursor.execute(comandoSQL, (filename,))
        conexao.commit()

        return redirect('/empresa')

    except Error as erro:
        return f"Erro de BD: {erro}"
    except Exception as erro:
        return f"Erro de BackEnd: {erro}"
    finally:
        encerrar_db(cursor, conexao)

@app.route('/procurar', methods=['POST'])
def procurar():
    if request.method == 'POST':

        procurar = request.form['pesquisar']

        conexao, cursor = conectar_db()
        comandoSQL = 'SELECT * FROM vaga WHERE titulo LIKE %s AND status = "Ativa" ORDER BY Id_Vaga DESC'
        cursor.execute(comandoSQL, (f'%{procurar}%',))
        resultados = cursor.fetchall()

        return render_template('procurar.html', resultados=resultados, procurar=procurar)

#FINAL DO CÓDIGO
if __name__ == '__main__':
    app.run(debug=True) 
