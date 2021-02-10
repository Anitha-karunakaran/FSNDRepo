import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''

# db_drop_and_create_all()

app = Flask(__name__)
setup_db(app)
CORS(app)


# CORS Headers
# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,PATCH,DELETE,OPTIONS')
#     return response


## ROUTES
'''
Endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        all_drinks = Drink.query.order_by(Drink.id).all()
        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in all_drinks]
        })
    except:
        print(sys.exc_info())
        abort(500)

'''
Endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail',methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    try:
        all_drinks = Drink.query.all()
        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in all_drinks]
        })
    except:
        abort(404)


'''
Endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def create_drink(payload):
    try:
        # The request should post the new recipe in the format below
        # {
        #     "title": "Black Coffee",
        #     "recipe": [{
        #         "name": "Water",
        #         "color": "white",
        #         "parts": 3
        #     }, {
        #         "name": "Coffee",
        #         "color": "brown",
        #         "parts": 1
        #     }
        #     ]
        #  }
        body = request.get_json()
        #print('logging:::: request body:::::'+str(body))
        #print('logging:::: payload:::::'+str(payload))

        new_drink_title = body.get('title', None)
        new_drink_recipe = body.get('recipe', None)

        if (new_drink_title is None) or (new_drink_recipe is None):
            abort(422) #Unprocessable

        new_drink = Drink(title=new_drink_title, recipe =json.dumps(new_drink_recipe))
        new_drink.insert()

        return jsonify({
        'success':True,
        'drinks': [new_drink.long()]
        }),200
    except:
        print(sys.exc_info())
        abort(500)

'''
Endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drank(payload, drink_id):
    try:
        body = request.get_json()
        # title_update = body.get('title')
        # recipe_update = body.get('recipe')

        updated_title = body.get('title', None)
        updated_recipe = body.get('recipe', None)

        if (updated_title is None) and (updated_recipe is None):
            abort(422)  # Unprocessable

        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)
        if updated_title:
            drink.title = updated_title
        if updated_recipe:
            drink.recipe = json.dumps(updated_recipe)
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except:
        abort(500)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''



# ----------------------------------------------------------------------------#
# Error Handlers
# ----------------------------------------------------------------------------#
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request'
    }), 400


@app.errorhandler(422)
def request_unprocessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'request is unprocessable'
    }), 422


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'internal server error'
    }), 500
