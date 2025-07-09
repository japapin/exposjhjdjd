from flask import Flask, render_template, request, redirect, url_for, session
import os
from datetime import datetime
import base64
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Garante que o diretório 'uploads' exista no servidor
os.makedirs('uploads', exist_ok=True)
DATA_FILE = 'uploads/comments.json'

# Garante que o arquivo JSON exista
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def load_comments():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_comments(comments):
    with open(DATA_FILE, 'w') as f:
        json.dump(comments, f, indent=4)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if (username == 'SAMUELQ' and password == 'Martins2025') or (username == 'Admin' and password == 'admin2025'):
            session['logged_in'] = True
            session['is_admin'] = (username == 'Admin')
            return redirect(url_for('blog'))
    return render_template('login.html')

@app.route('/blog', methods=['GET', 'POST'])
def blog():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    comments = load_comments()
    if request.method == 'POST':
        comment = request.form['comment']
        image_data = request.form['image_data']
        filename = datetime.now().strftime("photo_%Y%m%d_%H%M%S.png")
        if image_data:
            header, encoded = image_data.split(",", 1)
            data = base64.b64decode(encoded)
            filepath = os.path.join('uploads', filename)
            with open(filepath, "wb") as f:
                f.write(data)
        comments.append({
            'comment': comment,
            'photo': filename
        })
        save_comments(comments)
    return render_template('blog.html', comments=comments, is_admin=session.get('is_admin', False))

@app.route('/delete/<int:index>', methods=['POST'])
def delete_comment(index):
    if not session.get('logged_in') or not session.get('is_admin'):
        return redirect(url_for('login'))
    comments = load_comments()
    if 0 <= index < len(comments):
        photo_path = os.path.join('uploads', comments[index]['photo'])
        if os.path.exists(photo_path):
            os.remove(photo_path)
        comments.pop(index)
        save_comments(comments)
    return redirect(url_for('blog'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)