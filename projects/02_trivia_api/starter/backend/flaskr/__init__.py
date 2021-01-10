import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [qn.format() for qn in selection]
  current_questions = questions[start:end]

  return current_questions



def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  # Set up CORS. Allow '*' for origins.
  CORS(app, resources={r"/*": {"origins": "*"}})

  # CORS Headers
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,PATCH,DELETE,OPTIONS')
    return response

  # GET requests for all available categories.
  @app.route('/categories')
  def retrieve_categories():
    try:
      categories = Category.query.order_by(Category.id).all()
      ctg_dictionary = {}

      for ctg in categories:
        ctg_dictionary[ctg.id] = ctg.type

      return jsonify({
        'categories': ctg_dictionary,
        'success': True
      }),200
    except:
      abort(500)

  '''
    Endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
  @app.route('/questions')
  def retrieve_questions():
    try:
      all_questions = Question.query.order_by(Question.id).all()
      total_no_of_questions = len(all_questions)

      current_questions = paginate_questions(request, all_questions)

      if len(current_questions) == 0:
        abort(404)

      categories = Category.query.order_by(Category.id).all()
      ctg_dictionary = {}

      for ctg in categories:
        ctg_dictionary[ctg.id] = ctg.type

      return jsonify({
        'success': True,
        'questions': current_questions,
        'totalQuestions': total_no_of_questions,
        'categories': ctg_dictionary
      }),200
    except:
      abort(500)

  # ------------------#
  # DELETE
  # ------------------#

  '''
  Endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
        abort(404)
      question.delete()
      return jsonify({
        'success': True,
        'message': "question deleted"
      }), 200

    except:
      abort(422)

  # ------------------#
  # CREATE
  # ------------------#

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    try:
      body = request.get_json()
      question = body.get('question', None)
      answer = body.get('answer', None)
      difficulty = body.get('difficulty', None)
      category = body.get('category', None)

      new_question = Question(question = question, answer = answer, difficulty = difficulty, category = category)
      new_question.insert()
      return jsonify({
        'success':True,
        'created': new_question.id
      }),200
    except:
      abort(500)

  '''
  POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    try:
      body = request.get_json()
      search_term = body.get('searchTerm', '')

      matched_questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      if (matched_questions is None) or (len(matched_questions)==0):
        abort(404)
      current_questions = paginate_questions(request, matched_questions)

      if len(current_questions) == 0:
        abort(404)

      categories = Category.query.order_by(Category.id).all()
      ctg_dictionary = {}

      for ctg in categories:
        ctg_dictionary[ctg.id] = ctg.type

      return jsonify({
        'success': True,
        'questions': current_questions,
        'totalQuestions': len(current_questions),
        'categories': ctg_dictionary
      }), 200
    except:
      abort(500)

  '''
  A GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def retrieve_questions_by_category(category_id):
    try:
      questions = Question.query.filter(Question.category == category_id).all()
      total_no_questions = len(questions)
      if(total_no_questions == 0):
        abort(404)
      
      current_questions = paginate_questions(request, questions)
      
      categories = Category.query.order_by(Category.id).all()
      ctg_dictionary = {}

      for ctg in categories:
        ctg_dictionary[ctg.id] = ctg.type

      return jsonify({
        'success': True,
        'questions': current_questions,
        'totalQuestions': total_no_questions,
        'categories': ctg_dictionary,
        'currentCategory': category_id
      }),200
    except:
      abort(500)

  '''
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 
  
  If category is 0, get questions from all the categories

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def show_quiz():
    body = request.get_json()
    # print('body******'+ str(body))
    previous_questions = body.get('previous_questions', None)
    quiz_category = body.get('quiz_category', None)
    if ((quiz_category is None) or (previous_questions is None)):
      abort(422)
      # print('******abort 422')

    try:
      if(quiz_category['id'] == 0):
        # print('*****Quiz Category All')
        # print('*****previous_questions'+str(type(previous_questions))+'**'+str(previous_questions))
        questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
        # print('*****Qn All -'+str(questions))

      else:
        # print('*****Quiz Category'+str(quiz_category['id']))
        # print('*****previous_questions' + str(type(previous_questions)) + '**' + str(previous_questions))
        questions = Question.query.filter_by(category=quiz_category['id']).filter(Question.id.notin_(previous_questions)).all()
        # print('questions in Category ********' + str(questions))
      if len(questions) > 0:
        next_question = questions[random.randrange(0, len(questions))].format()
      else:
        next_question = None

      return jsonify({
        'success': True,
        'question': next_question
      }), 200
    except:
      print('Error::'+str(sys.exc_info()))
      abort(500)


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

  return app
