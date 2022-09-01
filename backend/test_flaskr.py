import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "student", "student", "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question' : 'Quel est la capital du Burkina Faso?',
            'answer' : 4,
            'difficulty' : 5,
            'category' : 3
        }

        self.searchTerm = {
            'searchTerm' : 'title'
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_404_not_found_categories(self):
        res = self.client().get('/categories/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_get_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)


        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))

    def test_404_not_found_questions_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_delete_question(self):
        res = self.client().delete('/questions/18')
        data = json.loads(res.data)
        question = Question.query.get(20)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)

    def test_422_unprocessable_deleting_not_existing_question(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_creating_question(self):
        res = self.client().post('/questions', json = self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_405_not_allowed_creating_question(self):
        res = self.client().post('/questions/1000', json = self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed')

    def test_searching_question_with_result(self):
        res = self.client().post('/questions', json = self.searchTerm)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']),2)
        self.assertTrue(data['total_questions'])
        

    def test_searching_question_with_no_result(self):
        res = self.client().post('/questions', json = {'searchTerm' : 'fghfjghhj'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']),0)
        self.assertFalse(data['total_questions'])
        

    def test_getting_question_by_category(self):
        res = self.client().get('/categories/5/questions', json = self.searchTerm)
        data = json.loads(res.data)
        questions = Question.query.filter_by(category=str(5)).all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']),len(questions))
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], Category.query.get(5).format()) 

    def test_404_not_found_category_questions(self):
        res = self.client().get('/categories/10/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_getting_quizzes(self):
        res = self.client().post('/quizzes', json={'previous_questions': [2, 4],
        'quiz_category' : Category.query.get(5).format()})
        data =json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['question']))

    def test_405_method_getting_quizzes(self):
        res = self.client().patch('/quizzes', json={'previous_questions': [2, 4],
        'quiz_category' : Category.query.get(5).format()})
        data =json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed')
        
        






# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()