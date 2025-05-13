import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import logging
from google import genai
from decouple import config
from django.utils import timezone
from AiQuetionare.models import Question, Category, Assessment, CandidateAnswer, Candidate, JobDescription
from AiQuetionare.serializer import AssessmentSerializer, QuestionSerializer

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
        
        # Get job description and candidate from request data
        job_id = data.get('job_id')
        candidate_id = data.get('candidate_id')
        
        assessment = None
        if job_id and candidate_id:
            try:
                job_description = JobDescription.objects.get(id=job_id)
                candidate = Candidate.objects.get(user_id=candidate_id)
                
                # Create an assessment if one doesn't exist for this candidate and job
                assessment, created = Assessment.objects.get_or_create(
                    candidate=candidate,
                    job_description=job_description,
                    is_complete=False,
                    defaults={'current_question': question}
                )
                
                if not created:
                    # Update the current question if assessment already exists
                    assessment.current_question = question
                    assessment.save()
            except (JobDescription.DoesNotExist, Candidate.DoesNotExist) as e:
                logger.error(f"Error getting job or candidate: {e}")
        
        # Serialize the data
        question_serz = QuestionSerializer(question)
        assessment_serz = None
        if assessment:
            assessment_serz = AssessmentSerializer(assessment)
        
        response_data = {
            "id": question.id,
            "question": question.question_text,
            "category": category.name,
            "difficulty": difficulty_level.capitalize(),
            "question_data": question_serz.data
        }
        
        if assessment_serz:
            response_data["assessment"] = assessment_serz.data
            response_data["assessment_id"] = assessment.id
            
        return JsonResponse(response_data)

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
        question_text = data.get('question')  # Allow both question_id and question text
        answer_text = data.get('answer', '')
        assessment_id = data.get('assessment_id')
        
        logger.info(f"Data received: question_id={question_id}, assessment_id={assessment_id}")
        
        # Handle case where frontend sends text instead of ID
        question = None
        if not question_id and question_text:
            # Try to find question by text
            question = Question.objects.filter(question_text__icontains=question_text[:100]).first()
            if not question:
                # Create a new question if we can't find an existing one
                category, _ = Category.objects.get_or_create(name="General")
                question = Question.objects.create(
                    question_number=f"Q{Question.objects.count() + 1}",
                    question_text=question_text,
                    answer="",
                    category=category,
                    difficulty=1  # Medium difficulty
                )
        else:
            question = Question.objects.filter(id=question_id).first()
        
        # Get assessment object
        if isinstance(assessment_id, dict) and 'id' in assessment_id:
            # Handle case where frontend sends assessment object
            assessment_id = assessment_id['id']
            
        assessment = None
        if assessment_id:
            assessment = Assessment.objects.filter(id=assessment_id).first()
        
        if not question:
            return JsonResponse({
                "error": "Question not found",
                "score": 0.5,
                "feedback": "We couldn't find the question in our system. Please try again."
            }, status=400)

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

        gemini_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        response_text = gemini_response.text

        if not response_text.strip().startswith('{'):
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx]
            else:
                response_text = '{"score": 0.5, "feedback": "Could not generate proper feedback."}'

        result = json.loads(response_text)
        score = max(0, min(1, float(result.get("score", 0.5))))
        feedback = result.get("feedback", "Your answer shows understanding but could be improved with more specific details.")

        # Store the candidate's answer in the database if we have an assessment
        if assessment:
            CandidateAnswer.objects.create(
                assessment=assessment,
                question=question,
                answer_text=answer_text,
                similarity_score=score,
                question_score=score,
            )
            logger.info(f"Stored answer for assessment {assessment.id}, question {question.id}")
        else:
            logger.warning("No assessment found, answer not stored in database")

        return JsonResponse({
            "score": score,
            "feedback": feedback,
            "question_id": question.id,
            "assessment_id": assessment.id if assessment else None
        })

    except Exception as e:
        logger.error(f"Error in evaluate_answer: {e}")
        return JsonResponse({
            "error": "Failed to evaluate answer.",
            "score": 0.5,
            "feedback": "There was an error evaluating your answer. The system will continue, but please notify the administrator."
        })

@csrf_exempt
@require_POST
def generate_result(request):
    logger.info("Generating final result...")
    try:
        data = json.loads(request.body)
        evaluations = data.get('evaluations', [])
        job_details = data.get('jobDetails', {})
        assessment_id = data.get('assessment_id')
        candidate_id = data.get('candidate_id')

        # Find the assessment if provided
        assessment = None
        if assessment_id:
            try:
                assessment = Assessment.objects.get(id=assessment_id)
            except Assessment.DoesNotExist:
                logger.warning(f"Assessment with ID {assessment_id} not found")
        
        # If no assessment was found but we have a candidate_id and job_details, try to find or create one
        if not assessment and candidate_id and job_details.get('id'):
            try:
                candidate = Candidate.objects.get(user_id=candidate_id)
                job_description = JobDescription.objects.get(id=job_details.get('id'))
                
                assessment, created = Assessment.objects.get_or_create(
                    candidate=candidate,
                    job_description=job_description,
                    is_complete=False
                )
                logger.info(f"{'Created' if created else 'Found'} assessment for candidate {candidate_id} and job {job_details.get('id')}")
            except (Candidate.DoesNotExist, JobDescription.DoesNotExist) as e:
                logger.warning(f"Could not find or create assessment: {e}")

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
            if start_idx >= 0 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx]
            else:
                response_text = '{"decision": "Not Hire", "probability": [0.7, 0.3], "summary": "Could not properly analyze interview results."}'

        result = json.loads(response_text)
        
        if result.get("decision") not in ["Hire", "Not Hire"]:
            result["decision"] = "Hire" if avg_score >= 0.7 else "Not Hire"

        prob = result.get("probability", [1 - avg_score, avg_score])
        prob_sum = sum(prob)
        result["probability"] = [p / prob_sum for p in prob] if prob_sum else [0.5, 0.5]

        result["summary"] = result.get("summary", f"The candidate scored an average of {avg_score:.2f} across {len(scores)} questions.")

        # Update the assessment with the results if we have one
        if assessment:
            assessment.is_complete = True
            assessment.end_time = timezone.now()
            assessment.weighted_score = avg_score
            assessment.hire_decision = result["decision"] == "Hire"
            assessment.hire_probability = result["probability"][1]  # Probability of hire
            assessment.save()
            logger.info(f"Assessment {assessment.id} updated with result: {result['decision']}, score: {avg_score}")
            
            # Include assessment ID in response
            result["assessment_id"] = assessment.id

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Error in generate_result: {e}")
        return JsonResponse({
            "decision": "Not Hire",
            "probability": [0.7, 0.3],
            "summary": "Error generating result. Defaulting to cautious hiring decision."
        })
