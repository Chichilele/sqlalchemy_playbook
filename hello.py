from datetime import datetime
from flask import Flask, request, flash, url_for, redirect, \
     render_template
from flask_sqlalchemy import SQLAlchemy
#  db.ForeignKey, db.Integer, db.String



app = Flask(__name__)
app.config.from_pyfile('test.cfg')
db = SQLAlchemy(app)


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column('todo_id', db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    text = db.Column(db.String)
    done = db.Column(db.Boolean)
    pub_date = db.Column(db.DateTime)

    def __init__(self, title, text):
        self.title = title
        self.text = text
        self.done = False
        self.pub_date = datetime.utcnow()

class Current_address(db.Model):
    __tablename__ = 'current_addresses'
    id = db.Column(db.Integer, primary_key=True)

    # associated to one user
    user_id=db.Column(db.Integer, db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'), unique=True)
    user=db.relationship('User', back_populates='current_address')
    # associated to one dataset
    address_id=db.Column(db.Integer, db.ForeignKey('addresses.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    address=db.relationship('Address', back_populates='current_address')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    fullname = db.Column(db.String)
    nickname = db.Column(db.String)
    addrs = db.relationship("Address", back_populates="user")
    current_address = db.relationship("Current_address", uselist=False, back_populates="user")

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (
                            self.name, self.fullname, self.nickname)


class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)

    user = db.relationship("User", back_populates="addrs")
    current_address = db.relationship("Current_address", uselist=False, back_populates="address")
    foos=db.relationship('Foo', back_populates='address')#, cascade='all, delete, delete-orphan')

    def __repr__(self):
        return "<Address(email_address='%s')>" % self.email_address

class Foo(db.Model):
    __tablename__ = 'foos'
    id = db.Column(db.Integer, primary_key=True)
    bar = db.Column(db.String, nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    address = db.relationship("Address", back_populates="foos")

    def __repr__(self):
        return "<Foo(bar='%s')>" % self.bar





@app.route('/')
def show_all():
    return render_template('show_all.html',
        todos=Todo.query.order_by(Todo.pub_date.desc()).all()
    )


@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        if not request.form['title']:
            flash('Title is required', 'error')
        elif not request.form['text']:
            flash('Text is required', 'error')
        else:
            todo = Todo(request.form['title'], request.form['text'])
            db.session.add(todo)
            db.session.commit()
            flash(u'Todo item was successfully created')
            return redirect(url_for('show_all'))
    return render_template('new.html')


@app.route('/update', methods=['POST'])
def update_done():
    for todo in Todo.query.all():
        print(f"HERE IS TODO {todo}")
        todo.done = ('done.%d' % todo.id) in request.form
    flash('Updated status') 
    db.session.commit()

    for i in Foo.query.all():
        print(f"------------- here: {i}")
    
    # Address.query.filter(Address.user_id==User.id, User.name=='Rene').delete(synchronize_session='fetch')
    # Address.query.filter(Address.user_id==User.id, 
    #                                 User.name=='Rene', 
    #                                 Address.id==Foo.address_id,
    #                                 Foo.bar=='foo1bars').delete(synchronize_session='fetch')

    Foo.query.filter(Foo.bar=='foo2bars').delete(synchronize_session='fetch')
    db.session.commit()
    return redirect(url_for('show_all'))


if __name__ == '__main__':
    app.run()