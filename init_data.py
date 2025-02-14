import pandas as pd
from extensions import db
from models import ReferenceProfile, University, Course
import logging
import os

logger = logging.getLogger(__name__)

def check_data_files():
    """Check if required data files exist"""
    required_files = [
        'data/Reference_profiles.csv',
        'data/Universities.csv',
        'data/courses_cleaned.csv'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
            
    if missing_files:
        logger.error(f"Missing required data files: {', '.join(missing_files)}")
        return False
    return True

def init_reference_profiles(app):
    """Initialize reference profiles from CSV data with personality scores"""
    try:
        # Read the CSV file
        df = pd.read_csv('data/Reference_profiles.csv', delimiter=';')
        
        with app.app_context():
            # Clear existing profiles first
            ReferenceProfile.query.delete()
            
            # Define personality scores for each profile group
            personality_scores = {
                'Analytical': {'dominance': 7, 'extraversion': 4, 'patience': 6, 'formality': 9},
                'Social': {'dominance': 6, 'extraversion': 8, 'patience': 7, 'formality': 5},
                'Persistent': {'dominance': 8, 'extraversion': 5, 'patience': 8, 'formality': 7},
                'Stabilizing': {'dominance': 5, 'extraversion': 6, 'patience': 9, 'formality': 8}
            }
            
            for _, row in df.dropna(subset=['Profiles']).drop_duplicates(subset=['Profiles']).iterrows():
                group = row['Reference Groups']
                scores = personality_scores.get(group, personality_scores['Analytical'])
                
                profile = ReferenceProfile(
                    name=row['Profiles'],
                    description=row['Description'] if pd.notna(row['Description']) else f"A {row['Profiles']} profile type",
                    dominance=scores['dominance'],
                    extraversion=scores['extraversion'],
                    patience=scores['patience'],
                    formality=scores['formality']
                )
                db.session.add(profile)
            
            db.session.commit()
            logger.info("Reference profiles initialized successfully")
            
    except Exception as e:
        logger.error(f"Error initializing reference profiles: {str(e)}")
        db.session.rollback()

def init_universities(app):
    """Initialize universities from CSV"""
    try:
        df = pd.read_csv('data/Universities.csv')
        
        with app.app_context():
            University.query.delete()
            
            for _, row in df.iterrows():
                university = University(
                    id=str(row['ID']).strip(),
                    name=str(row['Name']).strip(),
                    tel_number=str(row['Tel Number']).strip(),
                    website=str(row['Website']).strip() if pd.notna(row['Website']) else ''
                )
                db.session.add(university)
            
            db.session.commit()
            logger.info("Universities initialized successfully")
            
    except Exception as e:
        logger.error(f"Error initializing universities: {str(e)}")
        db.session.rollback()

def init_courses(app):
    """Initialize courses from CSV"""
    try:
        # Read the CSV file with different error handling
        df = pd.read_csv('data/courses_cleaned.csv', 
                        delimiter=';', 
                        on_bad_lines='skip')
        
        # Clean up the Key Skills column
        df['Key Skills'] = df['Key Skills'].apply(lambda x: str(x).split(',')[0] if pd.notna(x) else '')
        
        # Remove any trailing commas and clean up the data
        for column in df.columns:
            df[column] = df[column].apply(lambda x: str(x).strip().rstrip(',') if pd.notna(x) else '')
        
        with app.app_context():
            Course.query.delete()
            
            for _, row in df.iterrows():
                try:
                    # Skip malformed rows
                    if pd.isna(row['Course']) or pd.isna(row['Universities_ID']):
                        continue
                        
                    course = Course(
                        name=str(row['Course']).strip(),
                        university_id=str(row['Universities_ID']).strip(),
                        faculty=str(row['Faculty/Department']).strip(),
                        duration=int(float(row['Duration'])) if pd.notna(row['Duration']) else 0,
                        recommended_career=str(row['Recommended Career']).strip(),
                        key_skills=str(row['Key Skills']).strip()
                    )
                    db.session.add(course)
                except Exception as e:
                    logger.error(f"Error processing course {row['Course']}: {str(e)}")
                    logger.error(f"Row data: {row.to_dict()}")
                    continue
            
            try:
                db.session.commit()
                logger.info("Courses initialized successfully")
            except Exception as e:
                logger.error(f"Error committing courses: {str(e)}")
                db.session.rollback()
            
    except Exception as e:
        logger.error(f"Error initializing courses: {str(e)}")
        db.session.rollback()

def init_database(app):
    """Initialize all database tables"""
    try:
        # Check for required files first
        if not check_data_files():
            logger.error("Database initialization aborted due to missing files")
            return

        with app.app_context():
            # Initialize in order
            init_reference_profiles(app)
            init_universities(app)
            init_courses(app)
            
            # Verify data
            profiles_count = ReferenceProfile.query.count()
            universities_count = University.query.count()
            courses_count = Course.query.count()
            
            logger.info("\nDatabase Initialization Summary:")
            logger.info(f"Reference Profiles: {profiles_count}")
            logger.info(f"Universities: {universities_count}")
            logger.info(f"Courses: {courses_count}")
            
    except Exception as e:
        logger.error(f"Error during database initialization: {str(e)}")