import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from settings import (
DATABASE_HOSTNAME,
DATABASE_PORT,
DATABASE_USER,
DATABASE_PASSWORD
)

QUESTION_ID_TO_DELETE = 0

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""


    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(DATABASE_USER, DATABASE_PASSWORD,
                                                        DATABASE_HOSTNAME + ':' + DATABASE_PORT, self.database_name)

        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass


    '''
    Endpoint to handle GET requests for questions
    default page 1
    '''
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['categories'])

        print('********************************************************************')
        print('Request: /questions')
        print('Result Data:::: ' + str(data))
        print('-----------------------')
        print('Length of Questions'+str(len(data['questions'])))
    '''
    Endpoint to handle GET requests for questions with page in request
    '''

    def test_get_questions_in_page(self):
        res = self.client().get('/questions?page=2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['categories'])

        print('********************************************************************')
        print('Request: /questions?page=2')
        print('Result Data:::: ' + str(data))
        print('-----------------------')
        print('Length of Questions' + str(len(data['questions'])))

    def test_get_questions_in_non_existing_page(self):
        res = self.client().get('/questions?page=20000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['success'], False)
        print('********************************************************************')
        print('Request: /questions?page=20000')
        print('Result Data:::: ' + str(data))

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        print('********************************************************************')
        print('Request: /categories')
        print('Result Data::::  ' + str(data))

    def test_create_question(self):
        create_payload = {'question':'How many planets are there in Solar System',
                                                     'answer':'eight', 'difficulty':3, 'category':1}
        res = self.client().post('/questions', json=create_payload)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

        QUESTION_ID_TO_DELETE = int(data['created'])

        print('********************************************************************')
        print('Request: POST /questions')
        print('Request Payload::' + str(create_payload))
        print('Result Data::::  ' + str(data))

    def test_delete_question(self):
        create_payload = {'question': 'How many planets are there in Solar System',
                          'answer': 'eight', 'difficulty': 3, 'category': 1}
        res = self.client().post('/questions', json=create_payload)

        data = json.loads(res.data)
        new_question_id = data['created']
        print('created question id*************** '+str(new_question_id))

        url = '/questions/'+ str(new_question_id)
        res = self.client().delete(url)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['message'], 'question deleted')
        print('********************************************************************')
        print('Request: DELETE /questions/'+str(QUESTION_ID_TO_DELETE))
        print('Result Data::::  ' + str(data))

    def test_delete_non_existing_question(self):
        url = '/questions/20000'
        res = self.client().delete(url)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        print('********************************************************************')
        print('Request: DELETE /questions/20000')
        print('Result Data::::  ' + str(data))

    def test_search_questions(self):
        new_search = {'searchTerm': 'who'}
        res = self.client().post('/questions/search', json=new_search)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])

        print('********************************************************************')
        print('Request: POST /questions/search')
        print('Request Data: ' + str(new_search))
        print('Result Data::::  ' + str(data))

    def test_no_result_search_questions(self):
        new_search = {'searchTerm': 'abcdef'}
        res = self.client().post('/questions/search', json=new_search)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['success'], False)

        print('********************************************************************')
        print('Request: POST /questions/search')
        print('Request Data: '+str(new_search))
        print('Result Data::::  ' + str(data))

    def test_play_quiz_on_category(self):
        new_quiz = {'previous_questions': [], 'quiz_category': {'id': 1}}

        res = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        print('********************************************************************')
        print('Request: POST /quizzes')
        print('Request Data: '+str(new_quiz))
        print('Result Data::::  ' + str(data))

    def test_play_quiz_all_category(self):
        new_quiz = {'previous_questions': [], 'quiz_category': {'id': 0}}

        res = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        print('********************************************************************')
        print('Request: POST /quizzes')
        print('Request Data: '+str(new_quiz))
        print('Result Data::::  ' + str(data))


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
