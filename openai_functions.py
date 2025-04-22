# Import additional libraries
import streamlit as st
import os
import json
import tempfile
from openai import OpenAI
from dotenv import load_dotenv

from dotenv import load_dotenv

load_dotenv()


# Initialize OpenAI client
client = OpenAI()

# Transcription function using OpenAI API
def transcribe_audio(audio_bytes):
    """Transcribe audio using OpenAI's Whisper API"""
    if audio_bytes is None:
        raise ValueError("No audio data provided for transcription")
        
    try:
        print("Inside")
        # Save audio bytes to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
             temp_audio.write(audio_bytes)
             temp_audio_path = temp_audio.name
            
        # # Send to OpenAI for transcription
        with open(temp_audio_path, "rb") as audio_file:
             transcript = client.audio.transcriptions.create(
                 model="whisper-1",  # Changed from gpt-4o-transcribe to whisper-1
                 file=audio_file
             )
        
        # # Clean up temporary file
        os.unlink(temp_audio_path)
        print(transcript)
        return transcript.text

        # return "testing transcribed data"
        
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        raise  # Re-raise the exception to be handled by the caller

# Feedback function using OpenAI API
def get_ai_feedback(question, answer):
    """Get AI feedback on the answer using OpenAI's API"""
    if not answer:
        raise ValueError("No answer text provided for feedback")
        
    try:
        # prompt = f"""
        #     You are an expert interview coach analyzing responses to job interview questions.
        #     Analyze the following response to this interview question.

        #     QUESTION: {question}

        #     RESPONSE: {answer}

        #     Provide the following in JSON format with EXACT field names:
        #     1. A score from 0-100 based on the quality of the response (field name: "score")
        #     2. A brief analysis of the response (field name: "feedback")
        #     3. 2-3 key strengths of the response (field name: "strengths")
        #     4. 2-3 specific areas for improvement (field name: "areasforimprovement" - use exactly this field name)

        #     Format your response as a JSON object with these exact field names.
        #     """

        prompt=f"""
            Analyze the following comment:
            "{answer}"
            
            1. You are acting as a neutral, professional interview evaluator.
            2. Analyze the following transcribed response to a behavioral interview question.
                3. Generate a short and single-sentence micro feedback directed at the interviewee (second person).
            4. The feedback should:
                    – Be lightly encouraging but not overly enthusiastic
                    – Remain impersonal and professional (no excessive praise or emotional language)
                    – Not reveal whether the overall answer was good or bad
                    – Focus on observable behavior, actions, or approach (not personal traits)
                    – Avoid fluff or vague compliments
                    - Add a very brief bullet points if you are focusing on multiple aspects"""

        # Use the Responses API
        response = client.responses.create(
            model="gpt-4o",
            input=prompt
        )
        
        # Get the raw content from the response
        output_text = response.output_text
        print("Output_text")
        print(output_text)
        return output_text
        
        #return "Mock Feedback"
        # # Try to find JSON content and sanitize it
        # import re
        # json_match = re.search(r'```json\s*(.*?)\s*```', output_text, re.DOTALL)
        # if json_match:
        #     json_str = json_match.group(1)
        # else:
        #     json_str = output_text
            
        # # Strip any remaining markdown formatting
        # json_str = re.sub(r'[^{}[\],:"0-9a-zA-Z\s.-]', '', json_str)
        
        # # Parse the sanitized JSON
        # feedback_data = json.loads(json_str)
        
        # print("Feedback data")
        # print(feedback_data)
        
        # # # Field name normalization before validation
        # # if "areasofimprovement" in feedback_data and "areasforimprovement" not in feedback_data:
        # #     feedback_data["areasforimprovement"] = feedback_data["areasofimprovement"]
        
        # # Now validate fields
        # required_fields = ["score", "feedback", "strengths", "areasforimprovement"]
        # for field in required_fields:
        #     if field not in feedback_data:
        #         raise ValueError(f"Required field '{field}' missing from API response")
        
        # return feedback_data
        
    except Exception as e:
        st.error(f"Error getting feedback: {str(e)}")
        # Return fallback feedback
        # return {
        #     "score": 50,
        #     "feedback": "Fallback feedback due to API error. Please try again.",
        #     "strengths": ["Clear communication"],
        #     "areasforimprovement": ["Add more specific details"]
        # }


# Motivational Feedback
def motivationalFeedbackGen(transcription, label=""):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert in behavioral interview evaluation. "
                "Your task is to generate a short, encouraging feedback sentence "
                "based only on observable behavior in the interview response.\n\n"
                "Instructions:\n"
                "- If the response includes meaningful, observable actions (e.g., problem-solving, communication, planning), give one-sentence motivational feedback.\n"
                "- Begin the sentence with one of these phrases: 'Nice work,' 'It’s great,' or 'Good job.'\n"
                "- The sentence should be encouraging and focused only on what the candidate did (not who they are).\n"
                "- If the response is incoherent, off-topic, or lacks meaningful content, do NOT give fake praise. "
                "Instead, provide a soft, encouraging nudge like: 'Keep going, and do your best in the next question.'\n"
                "- Do not mention whether the answer is right or wrong.\n"
                "- Do not include extra explanations. Output only the feedback sentence.\n"
                "- Keep it under 15 words. Use simple and professional language."
            )
        },
        {
            "role": "user",
            "content": f"Response: {transcription}\n\nFeedback:"
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=60,
            temperature=0.5,
        )
        feedback = response.choices[0].message.content.strip()
        return f"{label} {feedback}"
    except Exception as e:
        return f"Error occurred: {str(e)}"

    
#Informational Feedback
def informationalFeedbackGen(question, transcription, label =""):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a behavioral interview evaluator. Your task is to give concise, structured, "
                "criteria-based feedback on a candidate’s response to an interview question.\n\n"
                "Use the 5 evaluation criteria (quoted exactly):\n"
                "1. \"Clarity and Structure\"\n"
                "2. \"Action and Initiative\"\n"
                "3. \"Outcome and Reflection\"\n"
                "4. \"Communication Fluency\"\n"
                "5. \"Relevance and Focus\"\n\n"
                "Instructions:\n"
                "- Your response must be a **single sentence**, no more than **15 words**.\n"
                "- It must start with **'You...'**\n"
                "- It must include at least **two quoted criteria**.\n"
                "- Focus only on observable behaviors or the structure of the response.\n"
                "- **Do not** include praise words (e.g., 'great', 'excellent') or numeric scores.\n"
                "- If the response is vague, off-topic, or lacks substance, say:\n"
                "  'You should improve both \"Relevance and Focus\" and \"Clarity and Structure\" next time.'\n"
                "- Return only the sentence. No explanation, no intro, no formatting.\n"
            )
        },
        {
            "role": "user",
            "content": f"""
Evaluate the following interview response.

Question: "{question}"

Response: "{transcription}"

Now generate the feedback using the exact format and rules above.
"""
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=60,
            temperature=0.5,
        )
        feedback = response.choices[0].message.content.strip()
        return f"{label} {feedback}"
    except Exception as e:
        return f"Error occurred: {str(e)}"

    
def analyze_transcript_feedback_3(question, transcript):
    print("Inside analyze_transcript_feedback_3")
    feedback_1_response=motivationalFeedbackGen(transcript)
    feedback_2_response=informationalFeedbackGen(question,transcript)
    return feedback_1_response+"\n"+feedback_2_response

def summarizeFeedback(feedback_text, feedbackType):
    messages = [
        {
            "role": "user",
            "content": f"""
Summarize the following feedback into 3–5 concise bullet points.

Instructions:
- Use second-person point of view (e.g., “You showed...”, “You demonstrated...”, “Your response reflected...”)
- Focus only on key **observations or analysis** from the feedback (not on advice, praise, or evaluation)
- Do not add new opinions or judge performance
- Each bullet must be under 20 words
- Keep tone neutral, factual, and professional
- Start each bullet on a **new line**
- Follow the exact bullet format shown below

Feedback:
{feedback_text}

---

Output format (copy this exactly):

Overall Feedback "("{feedbackType}")":
- You [summary of one observation from the feedback]  
- Your response showed [another observation]  
- You [another behavior or pattern noted in the feedback]  
- Your answer included [optional additional observation]  
"""
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=150,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error occurred: {str(e)}"