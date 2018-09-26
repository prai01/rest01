from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
from settings import app

# This is written in the format
# sqlite:///(ABSOLUTE PATH)

db = SQLAlchemy(app)

# So the table name is automatically set for you unless overridden.

# So let's say we had a class named BookResource, this would first be
# coverted to Book_Resource and then lower cased to book_resource

# We are going to override this default behavior.

# We are going to show how to override this here.
# To override the table name, set the __tablename__ class attribute.

class Book(db.Model):
    __tablename__ = 'books'
    id=db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    isbn = db.Column(db.Integer)    

    def json(self):
        return {'name':self.name, 'price':self.price, 'isbn':self.isbn}

    def add_book(_name, _price, _isbn):
        new_book=Book(name=_name, price = _price, isbn = _isbn)
        db.session.add(new_book)
        db.session.commit()
    
    def get_all_books():
        #return Book.query.all()
        return [Book.json(book) for book in Book.query.all()]

    def get_book(_isbn):
        return Book.json(Book.query.filter_by(isbn=_isbn).first())

    def delete_book(_isbn):
        #filter the book by isbn and chain it to delete
        is_successful = Book.query.filter_by(isbn=_isbn).delete()
        db.session.commit()
        return bool(is_successful)
    
    def update_book_price(_isbn,_price):
        book_to_update = Book.query.filter_by(isbn=_isbn).first()
        book_to_update.price=_price
        db.session.commit()

    def update_book_name(_isbn,_name):
        book_to_update = Book.query.filter_by(isbn=_isbn).first()
        book_to_update.name=_name
        db.session.commit()

    def replace_book(_isbn, _name, _price):
        book_to_replace= Book.query.filter_by(isbn=_isbn).first()
        book_to_replace.price = _price
        book_to_replace.name = _name
        db.session.commit()


    #define the represention method and the data format how we want it back.
    def __repr__(self):
        book_object={
            'name': self.name,
            'price': self.price,
            'isbn':self.isbn
        }
        return json.dumps(book_object)
