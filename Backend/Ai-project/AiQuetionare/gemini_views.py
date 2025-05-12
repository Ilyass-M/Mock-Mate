from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import google.generativeai as genai
from decouple import config
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Configure the Gemini API
try:
    # Get API key from environment variables or .env file
    GEMINI_API_KEY = config('GENAI_API_KEY')
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    logger.error(f"Failed to initialize Gemini API: {e}")
    model = None

@csrf_exempt
@require_POST
def generate_question(request):
    """Generate an interview question using Gemini API"""
    if not model:
        return JsonResponse({"error": "Gemini API not configured"}, status=500)
    
    try:
        data = json.loads(request.body)
        context = data.get('context', '')
        previous_questions = data.get('previousQuestions', [])
        difficulty = data.get('difficulty', 'beginner')
        
        # Construct the prompt for Gemini
        prompt = f"""
        You are an expert technical interviewer for a tech company.
        
        Job Context: {context}
        
        Previous questions asked in this interview: {previous_questions}
        
        Generate a {difficulty} level technical interview question that:
        1. Is relevant to the job context
        2. Is different from previous questions
        3. Tests both theoretical knowledge and practical application
        4. Can be answered in a few paragraphs
        
        Format your response as JSON with these fields:
        - question: the interview question
        - category: the technical category (e.g., "Frontend Development", "Algorithms", etc.)
        - difficulty: the difficulty level ("Beginner", "Intermediate", "Advanced")
        """
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        response_text = response.text
        
        # If response is not in proper JSON format, try to extract it
        if not response_text.strip().startswith('{'):
            # Try to find JSON in the text
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx]
            else:
                # Fallback to a default structure
                return JsonResponse({
                    "question": "Explain your approach to solving complex technical problems.",
                    "category": "Problem Solving",
                    "difficulty": difficulty.capitalize()
                })
        
        # Parse the response
        try:
            result = json.loads(response_text)
            return JsonResponse(result)
        except json.JSONDecodeError:
            # Fallback
            return JsonResponse({
                "question": response_text[:1000],  # Truncate if too long
                "category": "General",
                "difficulty": difficulty.capitalize()
            })
        
    except Exception as e:
        logger.error(f"Error in generate_question: {e}")
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_POST
def evaluate_answer(request):
    """Evaluate an interview answer using Gemini API"""
    if not model:
        return JsonResponse({"error": "Gemini API not configured"}, status=500)
    
    try:
        data = json.loads(request.body)
        question = data.get('question', '')
        answer = data.get('answer', '')
        context = data.get('context', '')
        
        # Construct the prompt for Gemini
        prompt = f"""
        You are an expert technical interviewer evaluating a candidate's response.
        
        Job Context: {context}
        
        Question: {question}
        
        Candidate's Answer: {answer}
        
        Evaluate the answer based on:
        1. Technical accuracy
        2. Completeness
        3. Clarity of explanation
        4. Practical application
        
        Format your response as JSON with these fields:
        - score: a value between 0.0 and 1.0 representing the quality of the answer
        - feedback: constructive feedback for the candidate (2-3 sentences)
        """
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        response_text = response.text
        
        # If response is not in proper JSON format, try to extract it
        if not response_text.strip().startswith('{'):
            # Try to find JSON in the text
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx]
            else:
                # Fallback to a default structure
                return JsonResponse({
                    "score": 0.7,
                    "feedback": "Your answer was generally good but could use more specific examples."
                })
        
        # Parse the response
        try:
            result = json.loads(response_text)
            return JsonResponse(result)
        except json.JSONDecodeError:
            # Fallback
            return JsonResponse({
                "score": 0.7,
                "feedback": "Evaluation system encountered an issue. Your answer has been recorded."
            })
    
    except Exception as e:
        logger.error(f"Error in evaluate_answer: {e}")
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_POST
def generate_result(request):
    """Generate final interview result using Gemini API"""
    if not model:
        return JsonResponse({"error": "Gemini API not configured"}, status=500)
    
    try:
        data = json.loads(request.body)
        evaluations = data.get('evaluations', [])
        job_details = data.get('jobDetails', {})
        
        # Extract job information
        job_title = job_details.get('title', 'Unknown Position')
        job_description = job_details.get('description', '')
        
        # Extract evaluation data
        questions_and_answers = []
        scores = []
        
        for eval in evaluations:
            questions_and_answers.append({
                "question": eval.get('question', ''),
                "answer": eval.get('answer', ''),
                "score": eval.get('similarity_score', 0)
            })
            scores.append(eval.get('similarity_score', 0))
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Construct the prompt for Gemini
        evaluations_formatted = "\n\n".join([
            f"Q: {qa['question']}\nA: {qa['answer']}\nScore: {qa['score']}"
            for qa in questions_and_answers
        ])
        
        prompt = f"""
        You are an expert technical hiring manager making a decision after a candidate interview.
        
        Job Information:
        - Position: {job_title}
        - Description: {job_description}
        
        Interview Results:
        {evaluations_formatted}
        
        Average Score: {avg_score:.2f}
        
        Based on the candidate's responses and their alignment with the job requirements, 
        provide a comprehensive analysis and hiring decision.
        
        Format your response as JSON with these fields:
        - decision: either "Hire" or "Not Hire"
        - probability: an array with two values representing [P(not hire), P(hire)], summing to 1.0
        - summary: a detailed summary of the candidate's performance (3-5 sentences)
        """
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        response_text = response.text
        
        # If response is not in proper JSON format, try to extract it
        if not response_text.strip().startswith('{'):
            # Try to find JSON in the text
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx]
            else:
                # Fallback to a default structure
                hire_decision = "Hire" if avg_score >= 0.7 else "Not Hire"
                hire_prob = max(min(avg_score, 0.95), 0.05)
                return JsonResponse({
                    "decision": hire_decision,
                    "probability": [1-hire_prob, hire_prob],
                    "summary": f"The candidate scored an average of {avg_score:.2f} across {len(scores)} questions."
                })
        
        # Parse the response
        try:
            result = json.loads(response_text)
            return JsonResponse(result)
        except json.JSONDecodeError:
            # Fallback
            hire_decision = "Hire" if avg_score >= 0.7 else "Not Hire"
            hire_prob = max(min(avg_score, 0.95), 0.05)
            return JsonResponse({
                "decision": hire_decision,
                "probability": [1-hire_prob, hire_prob],
                "summary": f"The candidate scored an average of {avg_score:.2f} across {len(scores)} questions."
            })
    
    except Exception as e:
        logger.error(f"Error in generate_result: {e}")
        return JsonResponse({"error": str(e)}, status=500)
