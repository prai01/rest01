#
#This is copy of app.py before the ORM was implemented.
#
from flask import Flask, jsonify, request, Response, json
from settings import *
from BookModel import *


books = [
    {
        'name':'Green Eggs and Ham',
        'price':7.99,
        'isbn':978039400165
    },
    {
        'name':'The Cat in The Hat',
        'price':6.99,
        'isbn':958039400165
    }
]

#data sanitization from POST
def validBookObject(bookObject):
    if("name" in bookObject and "price" in bookObject and "isbn" in bookObject):
        return True
    else:
        return False


#decorator
@app.route('/')
def app_health():
    return 'App API is running...'

@app.route('/health', methods=['GET'])
def health_check():
    return 'App API is running...'

#GET /books
@app.route('/books')
def get_books():
    return jsonify({'books':books})
    
#GET /books/978039400165
@app.route('/books/<int:isbn>')
def get_book_by_isbn(isbn):
    return_value={}
    for book in books:
        if book["isbn"]==isbn:
            return_value = {
                'name':book["name"],
                'price':book["price"]
            }
    return jsonify(return_value)        


#POST /books
#{
#    'name':'F',
#    'price':6.99,
#    'isbn':0123456789
#}

@app.route('/books', methods=['POST'])
def add_book():
    payload = request.get_json()
    if(validBookObject(payload)):
        new_book = {
            "name":payload['name'],
            "price":payload['price'],
            "isbn":payload['isbn']
        }
        books.insert(0, new_book)
        response = Response("",201,mimetype="application/json")
        response.headers['Location']='/books/' + str(new_book['isbn'])
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
def replace_book(isbn):
    payload= request.get_json()
    updated_book = {
        'name':payload["name"],
        'price':payload["price"],
        'isbn':isbn
    }
    
    i =0
    for book in books:
        currentIsbn = book["isbn"]
        if currentIsbn == isbn:
            books[i] = updated_book
        i += 1
    response = Response("", status=204)    
    return response


#PATCH /books/978039400165
#{
#    'name':'Harry Potter and the Chamber of Secrets'
#}

@app.route('/books/<int:isbn>', methods=['PATCH'])
def update_book(isbn):
    payload=request.get_json()
    updated_book={}
    
    if("name" in payload):
        updated_book["name"] = payload['name']
    if("price" in payload):
        updated_book["price"] = payload['price']

    for book in books:
        if book["isbn"] == isbn:
            book.update(updated_book)
    
    response = Response("", status=204)
    response.headers['Location']="/books/" + str(isbn)
    return response


#DELETE /books/978039400165
@app.route('/books/<int:isbn>', methods=['DELETE'])
def delete_book(isbn):
    i = 0
    for book in books:
        if book["isbn"] == isbn:
            books.pop(i)
            response = Response("", status=204)
            return response
        i += 1
    
    invalidBookObjectErrorMsg={
        "error":"Book with the ISBN number#"+str(isbn) +" was not found, so therefore unable to delete."
    }
    response = Response(json.dumps(invalidBookObjectErrorMsg), status=404, mimetype='application/json')
    return response


app.run(port=5004)