"Note - The non ORM version is app_static.py"

from flask import Flask, jsonify, request, Response
from settings import *
from BookModel import *
from UserModel import *
import json
import jwt, datetime
from functools import wraps


books = Book.get_all_books()

app.config['SECRET_KEY'] = 'meow'


#data sanitization from POST
def validBookObject(bookObject):
    if("name" in bookObject and "price" in bookObject and "isbn" in bookObject):
        return True
    else:
        return False


#decorator
@app.route('/login', methods=['POST'])
def get_token():
    request_data = request.get_json()
    username = str(request_data['username'])
    password = str(request_data['password'])

    match = User.username_password_match(username, password)
    if match:
        expiration_date = datetime.datetime.utcnow() + datetime.timedelta(seconds=100)
        token=jwt.encode({'exp': expiration_date}, app.config['SECRET_KEY'], algorithm='HS256')
        return token
    else:
        return Response('',401, mimetype='application/json')

@app.route('/')
def app_health():
    return 'App API is running...'

@app.route('/health', methods=['GET'])
def health_check():
    return 'App API is running...'

#decorator - a decorator is a function that takes another function and extends the behavior of the latter function 
# without explicitly modifying it.
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token=request.args.get('token')
        try:
            jwt.decode(token, app.config['SECRET_KEY'])
            return f(*args, **kwargs)
        except:
            return jsonify({'error': 'Need a valid token to view the page'}),401
    return wrapper

#GET /books
@app.route('/books')
#@token_required
def get_books():
    return jsonify({'books': Book.get_all_books()})

#GET /books/978039400165
@app.route('/books/<int:isbn>')
def get_book_by_isbn(isbn):
    return_value={}
    #for book in books:
    #    if book["isbn"]==isbn:
    #        return_value = {
    #            'name':book["name"],
    #            'price':book["price"]
    #        }
    return_value = Book.get_book(isbn)
    return jsonify(return_value)        


#POST /books
#{
#    'name':'F',
#    'price':6.99,
#    'isbn':0123456789
#}

@app.route('/books', methods=['POST'])
@token_required
def add_book():
    payload = request.get_json()
    if(validBookObject(payload)):
        Book.add_book(payload['name'], payload['price'], payload['isbn'])
        response = Response("",201,mimetype="application/json")
        response.headers['Location']='/books/' + str(payload['isbn'])
        return response
    else:
        invalidBookObjectErrorMsg={
            "error":"Invalid book object passed in request",
            "helpString":"Data passed in "+ str(payload)
        }
        response = Response(json.dumps(invalidBookObjectErrorMsg), status=400, mimetype='application/json')
        return response


#PUT /books/978039400165
# {
#   'name':'Green Eggs and Ham',
#   'price':8.99,
# }

@app.route('/books/<int:isbn>', methods=['PUT'])
@token_required
def replace_book(isbn):
    payload= request.get_json()
    """
    if (not validBookObject(payload)):
        invalidBookObjectErrorMsg={
            "error":"Invalid book object passed in request",
            "helpStrting":"Data should be passed in similar to this {'name:"
        }
        response = Response(json.dumps(invalidBookObjectErrorMsg), status=400, mimetype='application/json')
        return response
    """

    Book.replace_book(isbn, payload['name'], payload['price'])
    response = Response("", status=204)
    return response


#PATCH /books/978039400165
#{
#    'name':'Harry Potter and the Chamber of Secrets'
#}

@app.route('/books/<int:isbn>', methods=['PATCH'])
@token_required
def update_book(isbn):
    payload=request.get_json()
    updated_book={}
    
    if("name" in payload):
        Book.update_book_name(isbn, payload['name'])
    if("price" in payload):
        Book.update_book_price(isbn,payload['price'])
        
    response = Response("", status=204)
    response.headers['Location']="/books/" + str(isbn)
    return response


#DELETE /books/978039400165
@app.route('/books/<int:isbn>', methods=['DELETE'])
def delete_book(isbn):
    if(Book.delete_book(isbn)):
        response = Response("", status=204)
        return response
    
    invalidBookObjectErrorMsg={
        "error":"Book with the ISBN number#"+str(isbn) +" was not found, so therefore unable to delete."
    }
    response = Response(json.dumps(invalidBookObjectErrorMsg), status=404, mimetype='application/json')
    return response


app.run(port=5004)