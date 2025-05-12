import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import logging
from google import genai
from decouple import config
from AiQuetionare.models import Question,Category, Assessment, CandidateAnswer, Candidate, JobDescription

# Set up logging
logger = logging.getLogger(__name__)

# Configure the Gemini API
try:
    GEMINI_API_KEY = config('GEMINI_API_KEY')
    client = genai.Client(api_key=GEMINI_API_KEY)
    logger.info("Successfully initialized Gemini API client")
except Exception as e:
    logger.error(f"Failed to initialize Gemini API: {e}")

@csrf_exempt
@require_POST
def generate_question(request):
    logger.info("Generating question...")
    try:
        data = json.loads(request.body)
        context = data.get('context', '')
        previous_questions = data.get('previousQuestions', [])
        difficulty = data.get('difficulty', 'beginner')

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

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        response_text = response.text

        if not response_text:
            raise ValueError("Empty response")

        if not response_text.strip().startswith('{'):
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            response_text = response_text[start_idx:end_idx]

        result = json.loads(response_text)
        question_text = result.get("question", "")
        category_name = result.get("category", "General")
        difficulty_level = result.get("difficulty", "Beginner").lower()

        # Store the question in the database
        category, _ = Category.objects.get_or_create(name=category_name)
        question = Question.objects.create(
            question_number=f"Q{Question.objects.count() + 1}",
            question_text=question_text,
            answer="",  # Placeholder for now
            category=category,
            difficulty={"beginner": 2, "intermediate": 1, "advanced": 0}.get(difficulty_level, 2),
        )

        return JsonResponse({
            "id": question.id,
            "question": question.question_text,
            "category": category.name,
            "difficulty": difficulty.capitalize()
        })

    except Exception as e:
        logger.error(f"Error in generate_question: {e}")
        return JsonResponse({
            "error": "Failed to generate question."
        })

@csrf_exempt
@require_POST
def evaluate_answer(request):
    logger.info("Evaluating answer...")
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        answer_text = data.get('answer', '')
        assessment_id = data.get('assessment_id')

        question = Question.objects.get(id=question_id)
        assessment = Assessment.objects.get(id=assessment_id)

        prompt = f"""
        You are an expert technical interviewer evaluating a candidate's response.

        Question: {question.question_text}

        Candidate's Answer: {answer_text}

        Evaluate the answer based on:
        1. Technical accuracy
        2. Completeness
        3. Clarity of explanation
        4. Practical application

        Format your response as JSON with these fields:
        - score: a value between 0.0 and 1.0 representing the quality of the answer
        - feedback: constructive feedback for the candidate (2-3 sentences)
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        response_text = response.text

        if not response_text.strip().startswith('{'):
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            response_text = response_text[start_idx:end_idx]

        result = json.loads(response_text)
        score = max(0, min(1, float(result.get("score", 0.5))))
        feedback = result.get("feedback", "Your answer shows understanding but could be improved with more specific details.")

        # Store the candidate's answer in the database
        CandidateAnswer.objects.create(
            assessment=assessment,
            question=question,
            answer_text=answer_text,
            similarity_score=score,
            question_score=score,
        )

        return JsonResponse({
            "score": score,
            "feedback": feedback
        })

    except Exception as e:
        logger.error(f"Error in evaluate_answer: {e}")
        return JsonResponse({
            "error": "Failed to evaluate answer."
        })

@csrf_exempt
@require_POST
def generate_result(request):
    logger.info("Generating final result...")
    try:
        data = json.loads(request.body)
        evaluations = data.get('evaluations', [])
        job_details = data.get('jobDetails', {})

        job_title = job_details.get('title', 'Unknown Position')
        job_description = job_details.get('description', '')

        questions_and_answers = []
        scores = []

        for eval in evaluations:
            try:
                score = max(0, min(1, float(eval.get('similarity_score', 0.5))))
            except:
                score = 0.5
            scores.append(score)
            questions_and_answers.append({
                "question": eval.get('question', ''),
                "answer": eval.get('answer', ''),
                "score": score
            })

        avg_score = sum(scores) / len(scores) if scores else 0

        evaluations_formatted = "\n\n".join([
            f"Q: {qa['question']}\nA: {qa['answer']}\nScore: {qa['score']}" for qa in questions_and_answers
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

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        response_text = response.text

        if not response_text.strip().startswith('{'):
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            response_text = response_text[start_idx:end_idx]

        result = json.loads(response_text)

        if result.get("decision") not in ["Hire", "Not Hire"]:
            result["decision"] = "Hire" if avg_score >= 0.7 else "Not Hire"

        prob = result.get("probability", [1 - avg_score, avg_score])
        prob_sum = sum(prob)
        result["probability"] = [p / prob_sum for p in prob] if prob_sum else [0.5, 0.5]

        result["summary"] = result.get("summary", f"The candidate scored an average of {avg_score:.2f} across {len(scores)} questions.")

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Error in generate_result: {e}")
        return JsonResponse({
            "decision": "Not Hire",
            "probability": [0.7, 0.3],
            "summary": "Error generating result. Defaulting to cautious hiring decision."
        })
