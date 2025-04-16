from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()
# MongoDB connection setup
uri = os.getenv('MONGO_DB_URI')

def get_db_client():
    """Get MongoDB client connection"""
    try:
        print("Inside get_db_client")
        print(uri)
        client = MongoClient(uri, server_api=ServerApi('1'), tls=True, tlsAllowInvalidCertificates=True)
        # Send a ping to confirm connection
        client.admin.command('ping')
        
        print("Connected to MongoDB successfully!")
        return client
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return None

def save_survey_results(user_info, set_number, questions, answers, feedback_data,collection_name):
    """
    Save complete survey results to MongoDB
    
    Args:
        user_info (dict): User's name and email
        set_number (int): The set configuration number
        questions (list): List of interview questions
        answers (dict): Dictionary of answers indexed by question number
        feedback_data (dict): Dictionary of feedback data indexed by question number
    
    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        client = get_db_client()
        if not client:
            return False
            
        # Access the database and collection
        db = client.ai_interviewer_survey
        collection = db[collection_name]
        
        # Calculate overall score
        total_score = 0
        question_count = 0
        
        for idx in feedback_data:
            if "score" in feedback_data[idx]:
                total_score += feedback_data[idx]["score"]
                question_count += 1
        
        average_score = total_score / question_count if question_count > 0 else 0
        
        # Prepare all question responses with their feedback
        question_responses = []
        for idx, question in enumerate(questions):
            if idx in answers:
                response_data = {
                    "question_number": idx + 1,
                    "question_text": question,
                    "answer": answers.get(idx, "No response recorded"),
                    "feedback": feedback_data.get(idx, {}),
                    "mode": set_number  # Add mode to each response
                }
                question_responses.append(response_data)
        
        # Create document to insert
        survey_doc = {
            "user": {
                "name": user_info.get("name", ""),
                "email": user_info.get("email", "")
            },
            #"set_configuration": set_number,
            "mode_used": set_number,  # 1 = Edit, 2 = Read-only, 3 = Edit & Re-record
            "timestamp": datetime.datetime.now(),
            "overall_score": average_score,
            "questions_answered": question_count,
            "responses": question_responses
        }
        
        # Insert the document
        result = collection.insert_one(survey_doc)
        print(f"Survey results saved with ID: {result.inserted_id}")
        return True
        
    except Exception as e:
        print(f"Error saving survey results: {e}")
        return False
    finally:
        if client:
            client.close()

def get_survey_result_by_email(email):
    """Retrieve survey results for a specific email"""
    try:
        client = get_db_client()
        if not client:
            return None
            
        db = client.ai_interviewer_survey
        collection = db.user_survey_analysis
        
        # Find all survey results for this email
        results = list(collection.find({"user.email": email}))
        
        # Convert ObjectId to string for JSON serialization
        for result in results:
            result["_id"] = str(result["_id"])
            
        return results
        
    except Exception as e:
        print(f"Error retrieving survey results: {e}")
        return None
    finally:
        if client:
            client.close()