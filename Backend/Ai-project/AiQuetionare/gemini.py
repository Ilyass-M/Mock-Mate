from google import genai
from decouple import config
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Configure the Gemini API
try:
    GEMINI_API_KEY = config('GEMINI_API_KEY')
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Successfully initialized Gemini API")
except Exception as e:
    logger.error(f"Failed to initialize Gemini API: {e}")


def gemini_generate(jd, cv, skill):
    """Generate an interview question based on job description, CV and skill"""
    try:
        prompt = f"""
        You are an expert technical interviewer for a tech company.

        Job Description: {jd}
        Candidate Resume: {cv}
        Skill to test: {skill}

        Generate a technical interview question that:
        1. Is specific to the skill mentioned above
        2. Tests both theoretical knowledge and practical application
        3. Can be answered in a few paragraphs
        4. Is appropriate for the candidate's experience level based on their resume

        Format your response as JSON with these fields:
        - question: the interview question
        - category: the technical category (e.g., "Frontend Development", "Algorithms", etc.)
        - difficulty: the difficulty level ("Beginner", "Intermediate", "Advanced")
        """

        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        response_text = response.text if hasattr(response, 'text') else ""

        # Extract JSON from response
        if not response_text.strip().startswith('{'):
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx]
            else:
                raise ValueError("Failed to extract JSON from response")

        result = json.loads(response_text)
        
        # Validate required fields
        for field in ["question", "category", "difficulty"]:
            if field not in result:
                if field == "difficulty":
                    result[field] = "Intermediate"
                else:
                    result[field] = "Not provided"
                    
        return result
    except Exception as e:
        logger.error(f"Error in gemini_generate: {e}")
        # Fallback response
        return {
            "question": f"Explain your experience with {skill}. What projects have you worked on and what challenges did you face?",
            "category": skill,
            "difficulty": "Intermediate"
        }


def gemini_evaluate(question, answer):
    """Evaluate an interview answer"""
    try:
        prompt = f"""
        You are an expert technical interviewer evaluating a candidate's response.
        
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
        
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        response_text = response.text if hasattr(response, 'text') else ""
        
        # Extract JSON from response
        if not response_text.strip().startswith('{'):
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx]
            else:
                raise ValueError("Failed to extract JSON from response")
        
        result = json.loads(response_text)
        
        # Validate score is a number between 0 and 1
        if "score" in result:
            try:
                score = float(result["score"])
                if score < 0 or score > 1:
                    result["score"] = max(0, min(1, score))
            except (ValueError, TypeError):
                result["score"] = 0.5
        else:
            result["score"] = 0.5
            
        # Ensure feedback exists
        if "feedback" not in result or not result["feedback"]:
            result["feedback"] = "The answer demonstrates understanding but could be improved with more specific details."
            
        return result
    except Exception as e:
        logger.error(f"Error in gemini_evaluate: {e}")
        # Fallback response
        return {
            "score": 0.5,
            "feedback": "Thank you for your answer. It covers some key points, but could benefit from more specific examples."
        }


def gemini_generate_result(question_answers):
    """Generate final interview result based on all answers"""
    try:
        evaluations_formatted = "\n\n".join([
            f"Q: {qa['question']}\nA: {qa['answer']}\nScore: {qa['score']}"
            for qa in question_answers
        ])
        
        avg_score = sum(qa["score"] for qa in question_answers) / len(question_answers) if question_answers else 0
        
        prompt = f"""
        You are an expert technical hiring manager making a decision after a candidate interview.
        
        Interview Results:
        {evaluations_formatted}
        
        Average Score: {avg_score:.2f}
        
        Based on the candidate's responses, provide a comprehensive analysis and hiring decision.
        
        Format your response as JSON with these fields:
        - decision: either "Hire" or "Not Hire"
        - probability: an array with two values representing [P(not hire), P(hire)], summing to 1.0
        - summary: a detailed summary of the candidate's performance (3-5 sentences)
        """
        
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        response_text = response.text if hasattr(response, 'text') else ""
        
        # Extract JSON from response
        if not response_text.strip().startswith('{'):
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx]
            else:
                raise ValueError("Failed to extract JSON from response")
        
        result = json.loads(response_text)
        
        # Validate decision field
        if "decision" not in result or result["decision"] not in ["Hire", "Not Hire"]:
            result["decision"] = "Hire" if avg_score >= 0.7 else "Not Hire"
            
        # Validate probability field
        if "probability" not in result or not isinstance(result["probability"], list) or len(result["probability"]) != 2:
            hire_prob = max(min(avg_score, 0.95), 0.05)
            result["probability"] = [1-hire_prob, hire_prob]
        else:
            # Ensure probabilities sum to 1.0
            prob_sum = sum(result["probability"])
            if abs(prob_sum - 1.0) > 0.01:  # Allow small rounding errors
                result["probability"] = [p/prob_sum for p in result["probability"]]
                
        # Ensure summary exists
        if "summary" not in result or not result["summary"]:
            result["summary"] = f"The candidate scored an average of {avg_score:.2f} across {len(question_answers)} questions, showing {'strong' if avg_score >= 0.7 else 'moderate'} technical proficiency."
            
        return result
    except Exception as e:
        logger.error(f"Error in gemini_generate_result: {e}")
        # Fallback response
        hire_decision = "Hire" if avg_score >= 0.7 else "Not Hire"
        hire_prob = max(min(avg_score, 0.95), 0.05)
        return {
            "decision": hire_decision,
            "probability": [1-hire_prob, hire_prob],
            "summary": f"The candidate scored an average of {avg_score:.2f} across the interview questions. Based on this performance, our recommendation is to {hire_decision.lower()} the candidate."
        }
