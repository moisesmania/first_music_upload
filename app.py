from flask import Flask, render_template, request, send_file, redirect, url_for
import pyodbc
import io

app = Flask(__name__)

# Conexão com o SQL Server
DB_SERVER = 'DESKTOP-U5SFQEC\\SQLEXPRESS'  # Verifique se esse nome está correto
DB_DATABASE = 'music_storage'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};Trusted_Connection=yes;'

# Tentativa de conexão com o banco
try:
    conn = pyodbc.connect(conn_str)
    print("Conexão bem-sucedida!")
except Exception as e:
    print(f"Erro de conexão: {e}")

@app.route('/')
def index():
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM musicas")
    musicas = cursor.fetchall()
    cursor.close()  # Fechar o cursor após o uso
    return render_template('index.html', musicas=musicas)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        nome = request.form['nome']
        arquivo = request.files['arquivo']
        arquivo_binario = arquivo.read()

        cursor = conn.cursor()
        cursor.execute("INSERT INTO musicas (nome, arquivo) VALUES (?, ?)", (nome, arquivo_binario))
        conn.commit()
        cursor.close()  # Fechar o cursor após o uso

        return redirect(url_for('index'))  # Redireciona de volta para a página principal após o upload

    return render_template('upload.html')

@app.route('/download/<int:id>')
def download(id):
    cursor = conn.cursor()
    cursor.execute("SELECT nome, arquivo FROM musicas WHERE id=?", (id,))
    musica = cursor.fetchone()

    cursor.close()  # Fechar o cursor após o uso

    if musica:
        mp3_file = io.BytesIO(musica[1])
        mp3_file.seek(0)
        return send_file(mp3_file, as_attachment=True, download_name=musica[0] + '.mp3', mimetype='audio/mp3')
    
    return 'Música não encontrada!'

if __name__ == '__main__':
    app.run(debug=True)
