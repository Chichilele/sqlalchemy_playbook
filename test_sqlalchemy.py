import os

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime
from dotenv import load_dotenv

load_dotenv()

DB_URI = f"postgres://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@localhost:5432/sa_users"
engine = create_engine(DB_URI, echo=True)

Base = declarative_base()

class Current_address(Base):
    __tablename__ = 'current_addresses'
    id = Column(Integer, primary_key=True)

    # associated to one user
    user_id=Column(Integer, ForeignKey('users.id'), unique=True)
    user=relationship('User', back_populates='current_address')
    # associated to one dataset
    address_id=Column(Integer, ForeignKey('addresses.id'), nullable=True)
    address=relationship('Address', back_populates='current_address')

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)
    addrs = relationship("Address", back_populates="user")
    current_address = relationship("Current_address", uselist=False, back_populates="user")

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (
                            self.name, self.fullname, self.nickname)


class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="addrs")
    current_address = relationship("Current_address", uselist=False, back_populates="address")
    foos=relationship('Foo', back_populates='address', cascade='all, delete-orphan')

    def __repr__(self):
        return "<Address(email_address='%s')>" % self.email_address

class Foo(Base):
    __tablename__ = 'foos'
    id = Column(Integer, primary_key=True)
    bar = Column(String, nullable=False)
    address_id = Column(Integer, ForeignKey('addresses.id'), nullable=False)
    address = relationship("Address", back_populates="foos")

    def __repr__(self):
        return "<Foo(bar='%s')>" % self.bar



# class Parent(Base):
#     __tablename__ = 'parent'
#     id = Column(Integer, primary_key=True)
#     children = relationship("Child", back_populates="parent")

# class Child(Base):
#     __tablename__ = 'child'
#     id = Column(Integer, primary_key=True)
#     parent_id = Column(Integer, ForeignKey('parent.id'))
#     parent = relationship("Parent", back_populates="children")

##############################
# Base.metadata.create_all(engine)
##############################

def main():
    pass

## start session
Session = sessionmaker(bind=engine)
session = Session()

## perform migration
Base.metadata.create_all(engine)
qu = session.query(Address, Foo).join(Foo, Foo.address_id==Address.id).all()
## populating & deleting demo
## simple user
ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
session.add(ed_user)
session.commit()

## simple query
our_user = session.query(User).filter_by(name='ed').first() 
print(our_user)

## multiple simple users
session.add_all([
    User(name='wendy', fullname='Wendy Williams', nickname='windy'),
    User(name='mary', fullname='Mary Contrary', nickname='mary'),
    User(name='fred', fullname='Fred Flintstone', nickname='freddy')
    ])

## uncommited changes accessible here
session.dirty
session.new

## commit changes (comparable git push... hard naming!)
session.commit()

## create users and addresses from dict
j = {'name':'jack', 'fullname':'Jack Bean', 'nickname':'jacky'}
t = {'name':'Thomas', 'fullname':'Thomas Pasquet', 'nickname':'toto',
    'addrs':[Address(email_address='thomas@google.com'), Address(email_address='toto@yahoo.com')]}
thomas = User(**t)
jack = User(**j)

session.add(thomas)
session.commit()

## add addresses to user as objects (powerful ORM example)
jack.addrs = [
    Address(email_address='jack@google.com'),
    Address(email_address='j25@yahoo.com')
    ]

## alternative
addr1 = Address(email_address='jacky94@yopmail.com')

### !! add it to a parent before commiting to avoid not-null constraint error !!
jack.addrs.append(addr1)

session.add(addr1)
session.commit()

## delete the object from session and commit the change
## whether with the object itself
session.delete(addr1)
## or where it's linked to (here last item of jack addresses)
# session.delete(jack.addrs[-1])
session.commit()

## add address from dict
r = {'email_address':'rand@google.com'}
random_usr = User(name='ran', fullname='Random', nickname='randy')
random_usr.addrs = [Address(**r)]
session.add(random_usr)
session.commit()
# print(parent.children)

def new_rows_from_list(to_create, object_type):
    res = []
    for i in to_create:
        res.append(object_type(**i))
    return res



def new_rows_from_list(to_create, object_type):
    '''
    build new row of table object_type from list of dict
    returns list of instances

    list arributes are resurcively constructed
    '''

    tables = {
        'users': User,
        'addrs': Address,
        'foos': Foo,
    }

    ## saving all objects to list res
    res = []
    for i in to_create:
        d_data = {}
        for k,v in i.items():
            if not isinstance(v, list):
                d_data[k] = v
            else:
                d_data[k] = new_rows_from_list(v, tables[k])

        res.append(object_type(**d_data))

    return res

e = {'fullname':'Jack Bean', 'nickname':'jacky'}
estelle = User(name='estelle', **e)


to_create = [
    {'name':'Simone', 'fullname':'Simone Tangi', 'nickname':'gand-mere'},
    {'name':'Rene', 'fullname':'Rene Jules', 'nickname':'grand-pere',
    'addrs':[   {'email_address':'vittaqilli-3055@yopmail.com'}, 
                {'email_address':'vit305@gmail.com',
                    'foos':[{'bar':'foo1bars'}, {'bar':'foo2bars'}]},
                {'email_address':'vittaqi@yahoo.com'}]},
    {'name':'Claudine', 'fullname':'Claudine Philippe', 'nickname':'tante claudine'},
]

famille = new_rows_from_list(to_create, User)
session.add_all(famille)
session.commit()

nickname='toto'
user = session.query(User).filter_by(nickname=nickname).all()
assert (len(user) == 1),f"More than one user with nickname: {nickname}\n {user}"
user = user[0]

# inc_current_address = Current_address(user=user, address=user.addrs[0])
# user.current_address = inc_current_address
current_add = session.query(Current_address).filter_by(user_id=user.id).all() 
if current_add:
    current_add[0].address = user.addrs[0]
else:
    user.current_address = Current_address(user=user, address=user.addrs[0])

session.add(user)
session.commit()
print(f"user {user.nickname} current address is \'{user.current_address.address.email_address}\'")

for email, fullname in session.query(Address.email_address, User.fullname).join(User).\
    filter(User.nickname=='jacky').\
    all():
    print(f"email: {email}, \t\t fullname: {fullname}")

qu = session.query(Address, Foo).join(Foo, Foo.address_id==Address.id).all()

#############################################
if __name__ == '__main__':
    main()
