from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    conn.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, content TEXT, done INTEGER)')
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.execute('SELECT id, content, done FROM tasks')
    tasks = cursor.fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add():
    task_content = request.form['task']
    conn = sqlite3.connect('database.db')
    conn.execute('INSERT INTO tasks (content, done) VALUES (?, ?)', (task_content, 0))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete(task_id):
    conn = sqlite3.connect('database.db')
    conn.execute('DELETE FROM tasks WHERE id=?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle(task_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.execute('SELECT done FROM tasks WHERE id=?', (task_id,))
    done = cursor.fetchone()[0]
    conn.execute('UPDATE tasks SET done=? WHERE id=?', (0 if done else 1, task_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
