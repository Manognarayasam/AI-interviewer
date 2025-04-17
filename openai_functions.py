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
def motivationalFeedbackGen(transcription):
    print("Inside motivationalFeedbackGen")
    messages = [
    {
        "role": "system",
        "content": "You are an expert in motivational feedback. Your job is to provide short, lightly encouraging, behavior-focused micro-feedback on behavioral interview responses. Do not evaluate the overall quality of the answer. Do not praise personality traits. Do not use vague or emotional praise."
    },
    {
        "role": "user",
        "content": """
    Your task:
    - You will be given a transcribed behavioral interview response.
    - Analyze it as a neutral, professional interview evaluator.
    - Write a one-sentence motivational feedback.
    - Your sentence must focus only on the candidate's observable actions, decisions, or communication structure.
    - Your sentence must begin with **exactly one of the following openers**: "Nice work," "It’s great," or "Good job"
    - After the opener, write a simple, encouraging comment about what the person did (e.g., resolved conflict, explained clearly, followed up).

    Output format:
    Feedback: [One-sentence feedback starting with “Nice work,” “It’s great,” or “Good job”]

    Keep in mind:
    - Do not mention if the response is good or bad
    - Do not summarize the whole story
    - Avoid emotional or subjective praise like “amazing,” “awesome,” “well done”
    - Keep the tone human, light, and professional
    - Max 12–15 words
    - Use simple sentence structure

    ---

    Few-Shot Examples:

    Example 1:  
    Response: There was a time during a cross-functional project where a teammate kept making changes to shared documents without notifying the rest of us, which caused a lot of confusion. Initially, I hesitated to confront the issue because I didn’t want to create tension, but the workflow was clearly being disrupted. I eventually asked if we could have a quick sync-up. In the meeting, I started by thanking them for their contributions and then brought up the versioning problems in a neutral tone. We agreed to use a shared tracker going forward, which solved the issue and improved team communication.
    Feedback: It’s great that you found a direct and respectful way to handle the conflict.

    ---

    Example 2:  
    Response: I once accidentally sent an email campaign to the wrong audience segment due to a filtering error. As soon as I realized the mistake, I paused the campaign, notified my manager, and sent out a clarification message to the recipients. After resolving the immediate issue, I created a pre-launch checklist that included an extra step for reviewing the audience segment criteria. Since then, I’ve used that checklist consistently and haven’t repeated the mistake.   
    Feedback: Nice work taking fast action and building a way to avoid the same mistake.

    ---

    Example 3:  
    Response: During my internship, I was juggling multiple tasks, including a product demo, a final report, and my part-time coursework. I realized early on that everything would overlap in the same week, so I used time-blocking to divide my week into dedicated focus areas. I also proactively communicated with my supervisor to reprioritize lower-urgency items and align on expectations. That planning helped me stay on top of all my responsibilities without burning out, and everything was submitted on time.  
    Feedback: Good job structuring your time clearly and creating a plan that helped you manage multiple deadlines.

    ---

    Now evaluate the following response:

    "{transcription}"
    """
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error occurred: {str(e)}"
    

#Informational Feedback
def informationalFeedbackGen(question, transcription):
    print("Inside informationalFeedbackGen")
    messages = [
    {
            "role": "user",
            "content": f"""
    Evaluate the following response to the interview question.

    Question: "{question}"

    Feedback: "{transcription}"

    Internally assess the response using these 5 criteria (always quote them exactly):
    1. "Clarity and Structure"
    2. "Action and Initiative"
    3. "Outcome and Reflection"
    4. "Communication Fluency"
    5. "Relevance and Focus"

    Your feedback must:
    - Be a **single sentence**
    - Be **no more than 15 words**
    - Include at least **two quoted criteria**
    - Start with **"You..."**
    - Focus only on observable behavior or response structure
    - Avoid praise words (e.g., “great,” “excellent”) and **never** use numeric scores

    If your response exceeds 20 words, it is incorrect.

    ---

    Follow the examples below for structure, tone, and length:

    Example 1: 
    Question: Describe an occasion when you failed at a task. What did you learn from it?  
    Response: I underestimated how long a reporting task would take and missed the client deadline. I owned up to the mistake, explained what went wrong, and delivered it later that day. Since then, I’ve started adding buffer time for anything involving cross-team input.  
    Feedback: You showed "Outcome and Reflection" by explaining your process adjustment while ensuring "Communication Fluency".

    Example 2:
    Question: Tell me about a time you took the initiative in your career. What was your motivation for doing so?  
    Response: When I noticed that new interns kept asking similar onboarding questions, I started compiling a quick-start doc. I pulled info from existing resources and filled in the gaps with team input. I wasn’t asked to do it, but I figured it’d save everyone time. 
    Feedback: You demonstrated "Action and Initiative" and stayed aligned with "Relevance and Focus."

    Example 3: 
    Question: Describe a time when you used your leadership skills to motivate your team or colleagues.  
    Response: Halfway through a group assignment, progress stalled and people were losing interest. I proposed a short call to regroup, made sure everyone felt heard, and helped break the work into manageable parts. 
    Feedback: You used "Clarity and Structure" and "Communication Fluency" to guide the team forward.

    ---

    Now evaluate the current response using the same format and constraints.
    """
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300,
            temperature=0.5,
        )
        # Access the response content
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error occurred: {str(e)}"
    
def analyze_transcript_feedback_3(question, transcript):
    print("Inside analyze_transcript_feedback_3")
    feedback_1_response=motivationalFeedbackGen(transcript)
    feedback_2_response=informationalFeedbackGen(question,transcript)
    return feedback_1_response+"\n"+feedback_2_response

def summarizeFeedback(text):
    print("Inside SummarizeFeedback")
    messages = [
        {
            "role": "user",
            "content": f"""
    Summarize the following behavioral interview response into 3–5 concise bullet points.

    Instructions:
    - Use second-person point of view (e.g., “You described...”, “You handled...”, “Your response showed...”)
    - Focus only on observable facts (situation, actions, decisions, results)
    - Do not include praise, feedback, or personal opinions
    - Each bullet must be under 20 words
    - Keep tone neutral, professional, and clear
    - Follow the bullet format exactly

    Response:
    {text}

    ---

    Output format (copy this exactly):

    Summary:
    - You [summary of key situation or decision]
    - You [summary of a specific action taken]
    - Your response showed [summary of outcome or insight]
    - You [summary of another action or clarification]
    """
        }
    ]



    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300,
            temperature=0.5,
        )
        # Access the response content
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error occurred: {str(e)}"