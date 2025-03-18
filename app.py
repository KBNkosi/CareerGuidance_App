from flask import Config, Flask, jsonify, request, send_file, render_template_string
from flask_cors import CORS
import pandas as pd
from extensions import db
import init_data
from models import User, BehavioralAssessment, ReferenceProfile, Course, University
from recommendation import career_recommendation, calculate_reference_profile
import io
import os
import bcrypt
import logging
import traceback
import jwt
from datetime import datetime, timedelta
from functools import wraps

if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS with more permissive settings for development
CORS(app, 
    resources={
        r"/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "expose_headers": ["Content-Range", "X-Content-Range"]
        }
    }
)

# Configuration
app.config.update(
    SQLALCHEMY_DATABASE_URI='sqlite:///db.sqlite',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ECHO=True,
    JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'your-secret-key-here'),
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(days=1)
)

# Initialize extensions
db.init_app(app)

import logging
from typing import List, Dict, Any

def get_career_progression(career: str) -> List[Dict[str, Any]]:
    """
    Generate career progression path for a given career.
    Args:
        career (str): The career title to generate progression for
    Returns:
        List[Dict]: A list of career stages with title, years of experience, and salary
    """
    # Career progression mapping with defined paths for different careers
    career_paths = {
        "Software Engineer": [
            {"title": "Junior Software Engineer", "years": 0, "salary": 45000, "currency": "ZAR"},
            {"title": "Software Engineer", "years": 2, "salary": 75000, "currency": "ZAR"},
            {"title": "Senior Software Engineer", "years": 5, "salary": 95000, "currency": "ZAR"},
            {"title": "Lead Software Engineer", "years": 8, "salary": 120000, "currency": "ZAR"}
        ],
        "Data Scientist": [
            {"title": "Junior Data Scientist", "years": 0, "salary": 48000, "currency": "ZAR"},
            {"title": "Data Scientist", "years": 2, "salary": 78000, "currency": "ZAR"},
            {"title": "Senior Data Scientist", "years": 5, "salary": 98000, "currency": "ZAR"},
            {"title": "Lead Data Scientist", "years": 8, "salary": 125000, "currency": "ZAR"}
        ],
        "Public Defender": [
            {"title": "Junior Public Defender", "years": 0, "salary": 42000, "currency": "ZAR"},
            {"title": "Public Defender", "years": 3, "salary": 65000, "currency": "ZAR"},
            {"title": "Senior Public Defender", "years": 6, "salary": 85000, "currency": "ZAR"},
            {"title": "Chief Public Defender", "years": 9, "salary": 110000, "currency": "ZAR"}
        ],
        "Accountant": [
            {"title": "Junior Accountant", "years": 0, "salary": 40000, "currency": "ZAR"},
            {"title": "Staff Accountant", "years": 2, "salary": 60000, "currency": "ZAR"},
            {"title": "Senior Accountant", "years": 5, "salary": 80000, "currency": "ZAR"},
            {"title": "Finance Manager", "years": 8, "salary": 100000, "currency": "ZAR"}
        ],
        "Operations Manager": [
            {"title": "Operations Coordinator", "years": 0, "salary": 45000, "currency": "ZAR"},
            {"title": "Operations Manager", "years": 3, "salary": 70000, "currency": "ZAR"},
            {"title": "Senior Operations Manager", "years": 6, "salary": 90000, "currency": "ZAR"},
            {"title": "Director of Operations", "years": 9, "salary": 115000, "currency": "ZAR"}
        ],
        "General Practitioner": [
            {"title": "Medical Resident", "years": 0, "salary": 52000, "currency": "ZAR"},
            {"title": "General Practitioner", "years": 3, "salary": 120000, "currency": "ZAR"},
            {"title": "Senior GP", "years": 6, "salary": 150000, "currency": "ZAR"},
            {"title": "Medical Director", "years": 10, "salary": 180000, "currency": "ZAR"}
        ],
        "Civil Engineer": [
            {"title": "Junior Civil Engineer", "years": 0, "salary": 48000, "currency": "ZAR"},
            {"title": "Civil Engineer", "years": 3, "salary": 75000, "currency": "ZAR"},
            {"title": "Senior Civil Engineer", "years": 6, "salary": 95000, "currency": "ZAR"},
            {"title": "Project Director", "years": 9, "salary": 120000, "currency": "ZAR"}
        ],
        "IT Support Specialist": [
            {"title": "IT Support Technician", "years": 0, "salary": 35000, "currency": "ZAR"},
            {"title": "IT Support Specialist", "years": 2, "salary": 50000, "currency": "ZAR"},
            {"title": "Senior IT Support Specialist", "years": 4, "salary": 65000, "currency": "ZAR"},
            {"title": "IT Support Manager", "years": 7, "salary": 85000, "currency": "ZAR"}
        ]
    }

    try:
        # If we have a defined path for this career, return it
        if career in career_paths:
            logger.info(f"Found defined career path for: {career}")
            return career_paths[career]

        # If no specific path is defined, generate a generic progression
        logger.info(f"Generating generic career path for: {career}")
        return [
            {"title": f"Junior {career}", "years": 0, "salary": 40000},
            {"title": career, "years": 2, "salary": 60000},
            {"title": f"Senior {career}", "years": 5, "salary": 80000},
            {"title": f"Lead {career}", "years": 8, "salary": 100000}
        ]

    except Exception as e:
        logger.error(f"Error generating career progression for {career}: {str(e)}")
        return []

@app.route('/')
def test_route():
    return jsonify({"message": "Backend server is running!"}), 200

if __name__ == "__main__":
    with app.app_context():
        try:
            # Initialize database tables
            db.create_all()

            # Load reference profiles
            if ReferenceProfile.query.count() == 0:
                init_data.init_reference_profiles(app)

            # Load universities
            if University.query.count() == 0:
                init_data.init_universities(app)

            # Load courses
            if Course.query.count() == 0:
                init_data.init_courses(app)

            logger.info("Application initialized successfully")
        except Exception as e:
            logger.error(f"Error during initialization: {str(e)}")

    # Start the app
    app.run(debug=True)


# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        try:
            if token.startswith('Bearer '):
                token = token.split(" ")[1]
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return jsonify({'error': 'Invalid user'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

# Authentication routes
@app.route('/signup', methods=['POST', 'OPTIONS'])
def signup():
    if request.method == 'OPTIONS':
        # Handle preflight request with proper CORS headers
        response = jsonify({"message": "Preflight request successful"})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', 'http://localhost:3000'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '3600')  # Cache preflight response for 1 hour
        return response, 200
        
    try:
        logger.debug("Received signup request")
        data = request.json
        logger.debug(f"Signup data received: {data}")

        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'age', 'careerInterests', 'password']
        if not all(field in data for field in required_fields):
            logger.error("Missing required fields")
            return jsonify({"error": "Missing required fields"}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            logger.error("User already exists")
            return jsonify({"error": "User already exists"}), 409

        # Hash password
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

        # Create new user
        new_user = User(
            first_name=data['firstName'],
            last_name=data['lastName'],
            email=data['email'],
            password=hashed_password,
            age=data['age'],
            career_interests=data['careerInterests'],
            skills=data.get('skills', [])
        )

        # Add user to database
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"New user created: {new_user.email}")

        # Generate token
        token = jwt.encode(
            {
                'user_id': new_user.id,
                'exp': datetime.utcnow() + timedelta(days=1)
            },
            app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )

        # Return user data and token
        response = jsonify({
            "message": "User created successfully",
            "user": {
                "id": new_user.id,
                "firstName": new_user.first_name,
                "lastName": new_user.last_name,
                "email": new_user.email,
                "age": new_user.age,
                "careerInterests": new_user.career_interests,
                "skills": new_user.skills
            },
            "token": token
        })
        
        # Add CORS headers to the response
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', 'http://localhost:3000'))
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 201

    except Exception as e:
        logger.error(f"Error in signup: {str(e)}")
        logger.error(traceback.format_exc())
        db.session.rollback()
        error_response = jsonify({"error": "Failed to create user"})
        error_response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', 'http://localhost:3000'))
        error_response.headers.add('Access-Control-Allow-Credentials', 'true')
        return error_response, 500

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        # Handle preflight request with proper CORS headers
        response = jsonify({"message": "Preflight request successful"})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', 'http://localhost:3000'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '3600')  # Cache preflight response for 1 hour
        return response, 200
        
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES']
            }, app.config['JWT_SECRET_KEY'])

            response = jsonify({
                'token': token,
                'user': {
                    'id': user.id,
                    'firstName': user.first_name,
                    'lastName': user.last_name,
                    'email': user.email,
                    'age': user.age,
                    'careerInterests': user.career_interests,
                    'skills': user.skills
                }
            })
            
            # Add CORS headers to the response
            response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', 'http://localhost:3000'))
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response, 200
        else:
            error_response = jsonify({'error': 'Invalid email or password'})
            error_response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', 'http://localhost:3000'))
            error_response.headers.add('Access-Control-Allow-Credentials', 'true')
            return error_response, 401
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        error_response = jsonify({'error': 'Login failed'})
        error_response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', 'http://localhost:3000'))
        error_response.headers.add('Access-Control-Allow-Credentials', 'true')
        return error_response, 500

# Protected routes
@app.route('/user/profile', methods=['GET'])
@token_required
def get_user_profile(current_user):
    """
    Retrieve the profile information for the current user.

    This endpoint fetches the user's profile details, including personal
    information and the associated reference profile data, if available.
    The response includes the user's name, email, age, skills, career interests,
    and profile details such as dominance, extraversion, patience, and formality.

    Args:
        current_user: The currently authenticated user.

    Returns:
        A JSON response containing the user's profile information or an error
        message if the profile retrieval fails.
    """
    try:
        profile = ReferenceProfile.query.get(current_user.reference_profile_id)
        profile_data = {
            "id": profile.id,
            "name": profile.name,
            "description": profile.description,
            "dominance": profile.dominance,
            "extraversion": profile.extraversion,
            "patience": profile.patience,
            "formality": profile.formality
        } if profile else None
        
        return jsonify({
            "user": {
                "firstName": current_user.first_name,
                "lastName": current_user.last_name,
                "email": current_user.email,
                "age": current_user.age,
                "skills": current_user.skills.split(", ") if current_user.skills else [],
                "careerInterests": current_user.career_interests,
                "profile": profile_data
            }
        })
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return jsonify({"error": "Failed to get user profile"}), 500

@app.route('/user/profile', methods=['PUT'])
@token_required
def update_user_profile(current_user):
    """
    Update the profile information for the current user.

    This endpoint allows the user to update their personal information,
    including name, age, skills, and career interests. The request body should
    contain the fields to be updated, with the new values.

    Args:
        current_user: The currently authenticated user.

    Returns:
        A JSON response containing a success message and the updated user
        profile information, or an error message if the update fails.
    """
    try:
        data = request.json
        
        # Update user fields if provided
        for field in ['firstName', 'lastName', 'age', 'careerInterests']:
            if field in data:
                setattr(current_user, field, data[field])
        
        if 'skills' in data:
            current_user.skills = ", ".join(data['skills'])
            
        db.session.commit()
        
        return jsonify({
            "message": "Profile updated successfully",
            "user": {
                "firstName": current_user.first_name,
                "lastName": current_user.last_name,
                "email": current_user.email,
                "age": current_user.age,
                "skills": current_user.skills.split(", ") if current_user.skills else [],
                "careerInterests": current_user.career_interests
            }
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Profile update error: {str(e)}")
        return jsonify({"error": "Failed to update profile"}), 500

@app.route('/submit_assessment', methods=['POST'])
@token_required
def submit_assessment(current_user):
    """
    Handles behavioral assessment submissions
    Calculates user's behavioral profile
    """
    
    try:
        data = request.json
        responses = data.get('responses')

        if not responses:
            return jsonify({"error": "Responses are required"}), 400

        # Clear existing assessments
        BehavioralAssessment.query.filter_by(user_id=current_user.id).delete()

        for response in responses:
            adjective = response['adjective']
            question_type = response['question_type']
            factor = get_factor(adjective)
            assessment_entry = BehavioralAssessment(
                user_id=current_user.id,
                adjective=adjective,
                question_type=question_type,
                factor=factor
            )
            db.session.add(assessment_entry)

        db.session.commit()

        profile_id = calculate_reference_profile(current_user.id)
        current_user.reference_profile_id = profile_id
        db.session.commit()

        profile = ReferenceProfile.query.get(profile_id)
        
        return jsonify({
            "message": "Assessment submitted successfully",
            "profile": {
                "id": profile.id,
                "name": profile.name,
                "description": profile.description
            }
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Assessment submission error: {str(e)}")
        return jsonify({"error": "Failed to submit assessment"}), 500

@app.route('/recommend', methods=['GET'])
@token_required
def recommend(current_user):
    """
    Get a career recommendation for the current user.

    Returns:
        A JSON object with the following properties:
            name (str): The full name of the current user
            career_recommendation (str): The recommended career
            recommendation_rating (float): The rating of the recommendation
            related_courses_and_schools (list of objects): A list of related courses
                with the following properties:
                    course (str): The name of the course
                    school (str): The name of the university offering the course
                    duration (int): The duration of the course in years
                    keySkills (list of str): The key skills required for the course
    """
    try:
        if not current_user.reference_profile_id:
            return jsonify({"error": "Please complete the assessment first"}), 400
            
        career, rating = career_recommendation(current_user.id)
        if career is None:
            return jsonify({"error": "Recommendation could not be generated"}), 500

        related_courses = Course.query.filter_by(recommended_career=career).all()
        courses_and_schools = [
            {
                "course": course.name,
                "school": University.query.get(course.university_id).name,
                "duration": course.duration,
                "keySkills": course.key_skills.split(", ") if course.key_skills else []
            }
            for course in related_courses
        ]

        return jsonify({
            "name": f"{current_user.first_name} {current_user.last_name}",
            "career_recommendation": career,
            "recommendation_rating": rating,
            "related_courses_and_schools": courses_and_schools
        })
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        return jsonify({"error": "Failed to generate recommendation"}), 500

# Utility functions
def get_factor(adjective):
    # Convert adjective to lowercase and remove any whitespace
    """
    Determine the behavioral factor associated with a given adjective.

    Args:
        adjective (str): A descriptive word characterizing behavior or personality.

    Returns:
        str: The corresponding behavioral factor, which can be one of the following:
             "Dominance", "Extraversion", "Patience", or "Formality". Defaults to 
             "Dominance" if the adjective is not recognized.

    Notes:
        Logs a warning if an unrecognized adjective is encountered.
    """
    adjective = adjective.lower().strip()
    
    factor_mapping = {
        # Dominance factors
        "assertive": "Dominance",
        "confident": "Dominance",
        "decisive": "Dominance",
        "ambitious": "Dominance",
        "bold": "Dominance",
        "commanding": "Dominance",
        "competitive": "Dominance",
        "determined": "Dominance",
        "independent": "Dominance",
        "fast-paced": "Dominance",
        "achievement": "Dominance",
        
        # Extraversion factors
        "sociable": "Extraversion",
        "outgoing": "Extraversion",
        "friendly": "Extraversion",
        "communicative": "Extraversion",
        "enthusiastic": "Extraversion",
        "persuasive": "Extraversion",
        "lively": "Extraversion",
        "talkative": "Extraversion",
        "engaging": "Extraversion",
        "energetic": "Extraversion",
        "teamwork": "Extraversion",
        
        # Patience factors
        "calm": "Patience",
        "steady": "Patience",
        "patient": "Patience",
        "consistent": "Patience",
        "reliable": "Patience",
        "composed": "Patience",
        "accommodating": "Patience",
        "predictable": "Patience",
        "supportive": "Patience",
        "stable": "Patience",
        "consistency": "Patience",
        
        # Formality factors
        "structured": "Formality",
        "precise": "Formality",
        "detail-oriented": "Formality",
        "methodical": "Formality",
        "organized": "Formality",
        "careful": "Formality",
        "disciplined": "Formality",
        "conscientious": "Formality",
        "rule-following": "Formality",
        "excellence": "Formality",
        "collaborative": "Formality"
    }
    
    factor = factor_mapping.get(adjective)
    if not factor:
        logger.warning(f"Unknown adjective encountered: {adjective}")
        return "Dominance"  # Default factor if unknown
    return factor

@app.route('/career_path', methods=['GET'])
@token_required
def get_career_path_route(current_user):
    """
    API endpoint to get career path data for a user.

    Route: /career_path
    Method: GET

    Returns:
        - current_career: str, the recommended career for the user
        - match_rating: float, the match rating for the recommended career
        - progression: List[Dict[str, Any]], a list of career stages with title, years of experience, and salary

    Raises:
        400: If the user has not completed the assessment
        500: If there is an internal server error
    """
    try:
        # Check if user has completed assessment
        if not current_user.reference_profile_id:
            return jsonify({
                "error": "Please complete the assessment first",
                "redirect": "/assessment"
            }), 400
            
        # Get career recommendation
        career, rating = career_recommendation(current_user.id)
        if not career:
            logger.error(f"Unable to generate career recommendation for user {current_user.id}")
            return jsonify({
                "error": "Unable to generate career path",
                "redirect": "/assessment"
            }), 400
            
        # Get career progression data
        progression = get_career_progression(career)
        
        if not progression:
            logger.error(f"Unable to generate career progression for career: {career}")
            return jsonify({"error": "Failed to generate career progression"}), 500
        
        # Return both career recommendation and progression
        return jsonify({
            "current_career": career,
            "match_rating": rating,
            "progression": progression
        })
        
    except Exception as e:
        logger.error(f"Error in career path route: {str(e)}")
        return jsonify({"error": "Failed to load career data"}), 500

@app.route('/dashboard_data', methods=['GET'])
@token_required
def get_dashboard_data(current_user):
    """
    API endpoint to get user profile data and career recommendation.

    Route: /dashboard_data
    Method: GET

    Returns:
        - user: Dict[str, Any], user profile data
        - recommendation: Dict[str, Any], career recommendation data

    Raises:
        500: If there is an internal server error
    """
    
    try:
        # Get user profile data
        profile = None
        if current_user.reference_profile_id:
            profile = ReferenceProfile.query.get(current_user.reference_profile_id)
            
        profile_data = {
            "id": profile.id,
            "name": profile.name,
            "description": profile.description
        } if profile else None

        # Get career recommendation
        career_data = None
        if current_user.reference_profile_id:
            try:
                career, rating = career_recommendation(current_user.id)
                if career:
                    related_courses = Course.query.filter_by(recommended_career=career).all()
                    career_data = {
                        "career_recommendation": career,
                        "recommendation_rating": rating,
                        "related_courses_and_schools": [{
                            "course": course.name,
                            "school": University.query.get(course.university_id).name,
                            "duration": course.duration,
                            "keySkills": course.key_skills.split(", ") if course.key_skills else []
                        } for course in related_courses]
                    }
            except Exception as e:
                logger.error(f"Error getting career recommendation: {str(e)}")

        return jsonify({
            "user": {
                "firstName": current_user.first_name,
                "lastName": current_user.last_name,
                "email": current_user.email,
                "age": current_user.age,
                "skills": current_user.skills.split(", ") if current_user.skills else [],
                "careerInterests": current_user.career_interests,
                "profile": profile_data
            },
            "recommendation": career_data
        })

    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        return jsonify({"error": "Failed to load dashboard data"}), 500
    
AVAILABLE_SKILLS = [
    "Programming",
    "Data Structures",
    "Legal Research",
    "Negotiation",
    "Financial Analysis",
    "Excel",
    "Python",
    "Machine Learning",
    "Data Analysis",
    "System Design",
    "Problem Solving",
    "SQL",
    "Contract Law",
    "Communication",
    "Compliance",
    "Risk Management",
    "Auditing",
    "Policy Development",
    "Critical Thinking",
    "Financial Reporting",
    "Accounting Principles",
    "Tax",
    "Supply Chain Management",
    "Inventory Management",
    "Project Management",
    "AutoCAD",
    "Structural Analysis",
    "Patient Care",
    "Clinical Skills",
    "Health Assessment",
    "Diagnosis",
    "Technical Drawing",
    "Equipment Maintenance",
    "Welding",
    "Blueprint Reading",
    "Environmental Science",
    "Research Methods",
    "Classroom Management",
    "Curriculum Planning",
    "Child Development",
    "Technical Support",
    "Troubleshooting",
    "Customer Service",
    "Networking",
    "System Administration"
]

# Add this route to your app.py
@app.route('/skills', methods=['GET'])
@token_required
def get_skills(current_user):
    """Return list of available skills"""
    try:
        return jsonify(AVAILABLE_SKILLS)
    except Exception as e:
        logger.error(f"Error getting skills: {str(e)}")
        return jsonify({"error": "Failed to load skills"}), 500
    
@app.route('/submit_skills', methods=['POST'])
@token_required
def submit_skills(current_user):
    """
    Update user's skills with the given list of skills

    :param current_user: The user submitting the skills
    :return: A JSON response with the updated skills
    """
    try:
        data = request.json
        skills = data.get('skills', [])
        
        # Validate skills
        invalid_skills = [skill for skill in skills if skill not in AVAILABLE_SKILLS]
        if invalid_skills:
            return jsonify({"error": f"Invalid skills: {', '.join(invalid_skills)}"}), 400
            
        # Update user's skills
        current_user.skills = ", ".join(skills)
        db.session.commit()
        
        return jsonify({
            "message": "Skills updated successfully",
            "skills": skills
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error submitting skills: {str(e)}")
        return jsonify({"error": "Failed to update skills"}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    with app.app_context():
        try:
            # Initialize database tables
            db.create_all()

            # Load reference profiles
            if ReferenceProfile.query.count() == 0:
                init_data.init_reference_profiles(app)

            # Load universities
            if University.query.count() == 0:
                init_data.init_universities(app)

            # Load courses
            if Course.query.count() == 0:
                init_data.init_courses(app)

            logger.info("Application initialized successfully")
        except Exception as e:
            logger.error(f"Error during initialization: {str(e)}")

    # Start the app
    app.run(debug=True)