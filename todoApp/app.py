from flask import Flask, render_template, abort, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres@localhost:5432/todoapp'
db = SQLAlchemy(app)
migrate=Migrate(app, db)

class Todo(db.Model):
    __tablename__='todos'
    id = db.Column(db.Integer, primary_key=True)
    description=db.Column(db.String(), nullable = False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db. ForeignKey('todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo {self.id}{self.description}>'

class TodoList(db.Model):
    __tablename__='todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', lazy=True)

db.create_all()

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        description = request.get_json()['description']
        todo = Todo(description=description)
        body[description] = todo.description
        db.session.add(todo)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    return jsonify(body)

@app.route('/list/<list_id>')
def get_list_todos(list_id):
    todos = Todo.query.filter_by(list_id=list_id).order_by('id').all()
    return render_template('index.html', todos=todos)

@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    error=False
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
        error=True
    finally:
        db.session.close()
    if error:
        abort(500)
    return jsonify({'message': 'success'})
@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({ 'success': True })

#always include this at the bottom of your code
if __name__ == '__main__':
   app.run(host="0.0.0.0", port=3000)