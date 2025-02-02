import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r'/api/*' : {'origins' : '*'}})
    

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods = ['GET'])
    def get_categories():
        categories = Category.query.order_by('id').all()
        formated_categories = {str(category.id) : category.type for category in categories}
        

        if not len(formated_categories):
            abort(404)
        
        return jsonify({
            'success' : True,
            'categories' : formated_categories
        })


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods = ['GET'])
    def get_paginated_questions():
        questions = Question.query.order_by('id').all()
        paginated_questions = paginate_questions(request, questions)
        categories = Category.query.order_by('id').all()
        formated_categories = {str(category.id) : category.type for category in categories}

        if not len(paginated_questions):
            abort(404)
        
        return jsonify({
            'success' : True,
            'questions' : paginated_questions,
            'total_questions' : len(questions),
            'categories' : formated_categories,
            
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods = ['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.get(id)
            if not question : 
                abort(404)
            question.delete()
        except: 
            abort(422)

        return jsonify({
            'success' : True
        })
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods = ['POST'])
    def creating_question():
        body = request.get_json()
        searchTerm = body.get('searchTerm', None)
        if searchTerm:
            try:
                
                questions = Question.query.order_by(Question.id).filter(
                        Question.question.ilike("%{}%".format(searchTerm))
                    ).all()

            
            except:
                abort(422)
            return jsonify({
                    'success' : True,
                    'questions' : paginate_questions(request, questions),
                    'total_questions': len(questions),
                })
        else:
            try:
                question = request.get_json()['question']
                answer = request.get_json()['answer']
                difficulty = request.get_json()['difficulty']
                category = request.get_json()['category']

                quest = Question(
                    question=question, 
                    answer=answer, 
                    difficulty=difficulty, 
                    category=category
                )

                quest.insert()
            except:
                abort(422)

            return jsonify({
                'success' : True
            })

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions', methods = ['GET'])
    def get_category_questions(id):
        
        questions = Question.query.filter_by(category = str(id)).all()
        formated_questions = paginate_questions(request, questions)
        if not formated_questions:
            abort(404)

        return jsonify({
                    'success' : True,
                    'questions' : formated_questions,
                    'total_questions': len(questions),
                    'current_category': Category.query.get(id).format()
                })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods = ['POST'])
    def get_quizzes():
        
        previous_questions = request.get_json()['previous_questions']
        quizz_category = request.get_json()['quiz_category']
        print(quizz_category)
        
        if not quizz_category['id']:
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category = str(quizz_category['id'])).all()
        
        questions_id = [question.id for question in questions]
        
        
        for i in previous_questions:
            questions_id.remove(i)
        if not len(questions_id):
            abort(404)
        question_id = random.choice(questions_id)
        print(question_id)
        quest = Question.query.get(question_id).format()
        print("all:",quest)

        return jsonify({
                    'success' : True,
                    'question' : quest
                })


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success' : False,
            'error' : 404,
            'message' : 'Not found'
        }), 404

    @app.errorhandler(405)
    def method_not_alowed(error):
        return jsonify({
            'success' : False,
            'error' : 405,
            'message' : 'Method not allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False, 
            "error": 422, 
            "message": "unprocessable"
        }), 422
            
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False, 
            "error": 400, 
            "message": "bad request"
        }), 400

    

    return app

