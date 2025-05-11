# import json
# import urllib.parse
# import base64
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from django.utils import timezone
# import asyncio
# from AiQuetionare.models import *
# from AiQuetionare.serializer import *
# from asgiref.sync import sync_to_async
# from sentence_transformers import SentenceTransformer, util
# from sklearn.metrics.pairwise import cosine_similarity
# import numpy as np
# import pandas as pd
# import pickle
# import random
# from collections import defaultdict
# from django.db.models import Avg


# class InterviewConsumer(AsyncWebsocketConsumer):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.assessment = None
#         self.model = None
        
#     async def get_job_description(self, job_desc_id):
#         try:
#             job_description = await sync_to_async(JobDescription.objects.get)(id=job_desc_id)
#             return job_description
#         except JobDescription.DoesNotExist:
#             return None
    
#     @database_sync_to_async
#     def get_or_create_assessment(self, job_description_id):
#         """Get or create an assessment for the current user and job description"""
#         try:
#             user = self.scope['user']
#             candidate = Candidate.objects.get(user=user)
#             job_description = JobDescription.objects.get(id=job_description_id)
            
#             # Check if there's an active assessment
#             assessment = Assessment.objects.filter(
#                 candidate=candidate, 
#                 job_description=job_description,
#                 is_complete=False
#             ).first()
            
#             if not assessment:
#                 # Create a new assessment with a unique WebSocket group name
#                 assessment = Assessment.objects.create(
#                     candidate=candidate,
#                     job_description=job_description,
#                     websocket_group_name=self.room_group_name
#                 )
            
#             return assessment
#         except Exception as e:
#             print(f"Error getting or creating assessment: {e}")
#             return None
    
#     @database_sync_to_async
#     def load_sentence_transformer_model(self):
#         """Load the sentence transformer model"""
#         try:
#             if not hasattr(self, '_cached_model'):
#                 print("Loading SentenceTransformer model...")
#                 self._cached_model = SentenceTransformer('all-MiniLM-L6-v2')
#             return self._cached_model
#         except Exception as e:
#             print(f"Error loading sentence transformer model: {e}")
#             return None
    
#     @database_sync_to_async
#     def load_ml_model(self):
#         """Load the active machine learning model"""
#         try:
#             ml_model = MLModel.objects.filter(is_active=True).order_by('-created_at').first()
#             if ml_model:
#                 with open(ml_model.model_file.path, 'rb') as f:
#                     return pickle.load(f)
#             return None
#         except Exception as e:
#             print(f"Error loading ML model: {e}")
#             return None
    
#     @database_sync_to_async
#     def get_candidate_skills(self):
#         """Get the candidate's skills"""
#         try:
#             candidate = Candidate.objects.get(user=self.scope['user'])
#             return list(candidate.skills.values_list('name', flat=True))
#         except Exception as e:
#             print(f"Error getting candidate skills: {e}")
#             return []
    
#     @database_sync_to_async
#     def get_job_skills(self, job_description_id):
#         """Get the skills required for the job"""
#         try:
#             job_description = JobDescription.objects.get(id=job_description_id)
#             return list(job_description.skills.values_list('name', flat=True))
#         except Exception as e:
#             print(f"Error getting job skills: {e}")
#             return []
    
#     async def calculate_question_scores(self, job_skills, candidate_skills):
#         """Calculate scores for questions based on skills"""
#         try:
#             questions = await sync_to_async(list)(Question.objects.all())
#             questions_data = []
#             model = SentenceTransformer('all-MiniLM-L6-v2')
#             job_skill_embeddings = [model.encode(skill) for skill in job_skills]
#             user_skill_embeddings = [model.encode(skill) for skill in candidate_skills]
#             for question in questions:
#                 question_embedding = np.array(question.embedding) if question.embedding else model.encode(question.question_text)
#                 jd_score = self.calculate_max_similarity(question_embedding, job_skill_embeddings)
#                 user_score = self.calculate_avg_similarity(question_embedding, user_skill_embeddings)
#                 score = 0.6 * jd_score + 0.4 * user_score
#                 asked = await sync_to_async(CandidateAnswer.objects.filter)(assessment=self.assessment, question=question)
#                 questions_data.append({
#                     'question_number': question.question_number,
#                     'category': question.category.name,
#                     'difficulty': question.difficulty,
#                     'jd_score': jd_score,
#                     'user_score': user_score,
#                     'score': score,
#                     'asked': asked.exists()
#                 })
#             return pd.DataFrame(questions_data)
#         except Exception as e:
#             print(f"Error calculating question scores: {e}")
#             return pd.DataFrame()
    
#     def calculate_max_similarity(self, question_embedding, skill_embeddings):
#         """Calculates the maximum cosine similarity between a question and any of the provided skills."""
#         if not skill_embeddings:
#             return 0.0
#         similarities = [cosine_similarity([skill_embedding], [question_embedding])[0][0]
#                         for skill_embedding in skill_embeddings]
#         return max(similarities) if similarities else 0.0
    
#     def calculate_avg_similarity(self, question_embedding, user_skill_embeddings):
#         """Calculates the average cosine similarity between a question and any of the user's skills."""
#         if not user_skill_embeddings:
#             return 0.0
#         similarities = [cosine_similarity([skill_embedding], [question_embedding])[0][0]
#                         for skill_embedding in user_skill_embeddings]
#         return sum(similarities) / len(similarities) if similarities else 0.0
    
#     async def build_question_graph(self, questions_df):
#         """Build a graph of questions based on difficulty and category"""
#         try:
#             graph = defaultdict(list)
            
#             for category in questions_df["category"].unique():
#                 cat_qs = questions_df[questions_df["category"] == category].sort_values("difficulty")
#                 prev_row = None
#                 for _, current_row in cat_qs.iterrows():
#                     if prev_row is not None:
#                         graph[prev_row["question_number"]].append(current_row["question_number"])
#                     prev_row = current_row
            
#             return graph
#         except Exception as e:
#             print(f"Error building question graph: {e}")
#             return defaultdict(list)
    
#     async def select_next_question(self, questions_df):
#         """Select the next question using the A* algorithm"""
#         try:
#             if questions_df.empty:
#                 return None
            
#             # Get top 5 categories
#             category_scores = questions_df.groupby("category")["score"].max()
#             top_5_categories = category_scores.sort_values(ascending=False).head(5).index.tolist()
            
#             if not top_5_categories:
#                 return None
                
#             # Randomly select a category
#             selected_category = random.choice(top_5_categories)
            
#             # Filter questions by category and get the easiest one as starting point
#             cat_df = questions_df[questions_df["category"] == selected_category].sort_values("difficulty", ascending=False)
            
#             if cat_df.empty:
#                 return None
                
#             start_q = cat_df["question_number"].values[0]
#             asked_nodes = set(questions_df[questions_df["asked"] == True]["question_number"])
#             score_dict = dict(zip(questions_df["question_number"], questions_df["score"]))
            
#             # Build graph
#             graph = await self.build_question_graph(questions_df)
            
#             # Run A* algorithm
#             path, best_node, best_score = self.a_star_search(graph, start_q, score_dict, asked_nodes)
            
#             # If question already asked, try again with an empty asked set
#             if path[-1] in asked_nodes:
#                 path, best_node, best_score = self.a_star_search(graph, start_q, score_dict, set())
            
#             # Get the question object
#             question = await sync_to_async(Question.objects.get)(question_number=path[-1])
            
#             # Update the current question in the assessment
#             self.assessment.current_question = question
#             await sync_to_async(self.assessment.save)()
            
#             return question
#         except Exception as e:
#             print(f"Error selecting next question: {e}")
#             return None
    
#     def a_star_search(self, graph, start, scores, asked_nodes, threshold=0.99):
#         """
#         A* search algorithm to find the best question
        
#         Args:
#             graph: dict of adjacency list for the tree {node: [children]}
#             start: starting node id
#             scores: dict of scores for each node
#             asked_nodes: set of nodes (question numbers) that have already been asked
#             threshold: early stopping threshold if a node is highly similar
#         """
#         import heapq
        
#         open_set = []
#         heapq.heappush(open_set, (1 - scores.get(start, 0), start))
#         came_from = {}
#         g_score = {start: 0}
#         best_node = start
#         best_score = scores.get(start, 0)
        
#         while open_set:
#             _, current = heapq.heappop(open_set)
            
#             if current in asked_nodes:
#                 continue
                
#             if scores.get(current, 0) > best_score:
#                 best_node = current
#                 best_score = scores.get(current, 0)
                
#             if scores.get(current, 0) >= threshold:
#                 break
                
#             for neighbor in graph.get(current, []):
#                 if neighbor in asked_nodes:
#                     continue
                    
#                 tentative_g_score = g_score[current] + 1
#                 if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
#                     came_from[neighbor] = current
#                     g_score[neighbor] = tentative_g_score
#                     f_score = tentative_g_score + (1 - scores.get(neighbor, 0))
#                     heapq.heappush(open_set, (f_score, neighbor))
        
#         path = []
#         current = best_node
#         while current in came_from:
#             path.append(current)
#             current = came_from[current]
#         path.append(start)
#         return path[::-1], best_node, best_score
    
#     async def evaluate_answer(self, question, answer_text):
#         """Evaluate the candidate's answer using semantic similarity"""
#         try:
#             # Get original answer
#             original_answer = question.answer
            
#             # Calculate similarity
#             model = self.model or SentenceTransformer('all-MiniLM-L6-v2')
#             embedding_orig = model.encode(original_answer)
#             embedding_user = model.encode(answer_text)
            
#             similarity_score = util.cos_sim(embedding_orig, embedding_user).item()
            
#             # Calculate timestamps for response time
#             now = timezone.now()
#             question_asked_at = await sync_to_async(self.assessment.answers.filter)(question=question).first()
#             response_time = None
            
#             if question_asked_at:
#                 response_time = (now - question_asked_at.asked_at).total_seconds()
            
#             # Record the answer
#             answer, created = await sync_to_async(CandidateAnswer.objects.update_or_create)(
#                 assessment=self.assessment,
#                 question=question,
#                 defaults={
#                     'answer_text': answer_text,
#                     'similarity_score': similarity_score,
#                     'response_time_seconds': response_time
#                 }
#             )
            
#             # Update question score
#             alpha = 0.7  # Weight for original score
#             beta = 0.3   # Weight for similarity score
            
#             # Get the question from DataFrame
#             questions_df = await self.calculate_question_scores(
#                 await self.get_job_skills(self.assessment.job_description.id),
#                 await self.get_candidate_skills()
#             )
            
#             qn_row = questions_df[questions_df["question_number"] == question.question_number]
#             if not qn_row.empty:
#                 original_score = qn_row["score"].values[0]
#                 updated_score = alpha * original_score + beta * similarity_score
#                 answer.question_score = updated_score
#                 await sync_to_async(answer.save)()
            
#             return {
#                 'similarity_score': similarity_score,
#                 'answer_id': answer.id
#             }
#         except Exception as e:
#             print(f"Error evaluating answer: {e}")
#             return {'similarity_score': 0.0, 'answer_id': None}
    
#     async def make_hire_decision(self):
#         """Make a hiring decision based on the ML model"""
#         try:
#             # Calculate average scores
#             answers = await sync_to_async(CandidateAnswer.objects.filter)(assessment=self.assessment)
            
#             if not await sync_to_async(answers.exists)():
#                 return {"decision": "Not enough data", "probability": [0.5, 0.5]}
            
#             avg_weighted_score = await sync_to_async(answers.aggregate)(Avg('question_score'))['question_score__avg'] or 0.0
#             cv_match_score = self.assessment.candidate.cv_match_score
            
#             # Create data for prediction
#             new_candidate_data = pd.DataFrame({
#                 "cv_match_score": [cv_match_score],
#                 "weighted_score": [avg_weighted_score]
#             })
            
#             # Load ML model if not already loaded
#             ml_model = self.ml_model or await self.load_ml_model()
            
#             if not ml_model:
#                 return {"decision": "No model available", "probability": [0.5, 0.5]}
            
#             # Make prediction
#             prediction = ml_model.predict(new_candidate_data)
#             probability = ml_model.predict_proba(new_candidate_data)
            
#             # Update assessment
#             self.assessment.weighted_score = avg_weighted_score
#             self.assessment.hire_decision = bool(prediction[0] == 1)
#             self.assessment.hire_probability = probability[0][1]  # Probability of hire (class 1)
#             self.assessment.is_complete = True
#             self.assessment.end_time = timezone.now()
#             await sync_to_async(self.assessment.save)()
            
#             return {
#                 "decision": "Hire" if prediction[0] == 1 else "Not Hire",
#                 "probability": probability[0].tolist()
#             }
#         except Exception as e:
#             print(f"Error making hire decision: {e}")
#             return {"decision": "Error", "probability": [0.5, 0.5]}
    
#     async def connect(self):
#         try:
#             self.room_name = self.scope['url_route']['kwargs']['job_desc_id']
#             if self.scope['user'].is_anonymous:
#                 await self.close(code=401)
#                 return

#             # Accept the connection early
#             await self.accept()

#             # Perform initialization tasks asynchronously
#             asyncio.create_task(self.initialize_connection())
#         except Exception as e:
#             print(f"Error in connect: {e}")
#             await self.close(code=500)

#     async def initialize_connection(self):
#         try:
#             job_description = await self.get_job_description(self.room_name)
#             if not job_description:
#                 await self.close(code=404)
#                 return

#             user_id = self.scope['user'].id
#             self.room_group_name = f'interview_{self.room_name}_userid{user_id}'
#             await self.channel_layer.group_add(self.room_group_name, self.channel_name)

#             self.assessment = await self.get_or_create_assessment(self.room_name)
#             if not self.assessment:
#                 await self.close(code=500)
#                 return

#             self.model = await self.load_sentence_transformer_model()
#             self.ml_model = await self.load_ml_model()
#         except Exception as e:
#             print(f"Error in initialize_connection: {e}")
    
#     async def disconnect(self, close_code):
#         try:
#             # Leave room group
#             if hasattr(self, 'room_group_name') and hasattr(self, 'channel_name'):
#                 await self.channel_layer.group_discard(
#                     self.room_group_name,
#                     self.channel_name
#                 )
#         except Exception as e:
#             print(f"Error in disconnect: {e}")
    
#     async def receive(self, text_data):
#         """Handle incoming WebSocket messages"""
#         try:
#             text_data_json = json.loads(text_data)
#             message_type = text_data_json.get('type', '')
            
#             if message_type == 'get_question':
#                 await self.handle_get_question()
#             elif message_type == 'submit_answer':
#                 question_id = text_data_json.get('question_id')
#                 answer_text = text_data_json.get('answer')
#                 await self.handle_submit_answer(question_id, answer_text)
#             elif message_type == 'finish_interview':
#                 await self.handle_finish_interview()
#             else:
#                 await self.send(text_data=json.dumps({
#                     'type': 'error',
#                     'message': 'Unknown message type'
#                 }))
#         except json.JSONDecodeError:
#             await self.send(text_data=json.dumps({
#                 'type': 'error',
#                 'message': 'Invalid JSON'
#             }))
#         except Exception as e:
#             print(f"Error in receive: {e}")
#             await self.send(text_data=json.dumps({
#                 'type': 'error',
#                 'message': f'An error occurred: {str(e)}'
#             }))
    
#     async def handle_get_question(self):
#         """Handle request for a new question"""
#         def get_question_data(question):
#             return {
#                 'id': question.id,
#                 'question_number': question.question_number,
#                 'question_text': question.question_text,
#                 'category': question.category.name,
#                 'difficulty': question.get_difficulty_display()
#             }
#         try:
#             # Calculate scores for questions
#             print("hello Questions")
#             job_skills = await self.get_job_skills(self.assessment.job_description.id)
#             print("hello Questions")
#             candidate_skills = await self.get_candidate_skills()
#             questions_df = await self.calculate_question_scores(job_skills, candidate_skills)
#             # Select next question
#             question = await self.select_next_question(questions_df)

#             if not question:
#                 await self.send(text_data=json.dumps({
#                     'type': 'no_more_questions',
#                     'message': 'No more questions available'
#                 }))
#                 return

#             # Serialize question using sync_to_async
#             question_data = await sync_to_async(get_question_data)(question)
#             print("hello Questions2 ")

#             # Send question to WebSocket
#             await self.send(text_data=json.dumps({
#                 'type': 'question',
#                 'question': question_data
#             }))
#         except Exception as e:
#             print(f"Error getting question: {e}")
#             await self.send(text_data=json.dumps({
#                 'type': 'error',
#                 'message': f'Error getting question: {str(e)}'
#             }))
    
#     async def handle_submit_answer(self, question_id, answer_text):
#         """Handle submission of an answer"""
#         try:
#             # Get the question
#             question = await sync_to_async(Question.objects.get)(id=question_id)
            
#             # Evaluate the answer
#             result = await self.evaluate_answer(question, answer_text)
            
#             # Send response
#             await self.send(text_data=json.dumps({
#                 'type': 'answer_evaluation',
#                 'question_id': question_id,
#                 'similarity_score': result['similarity_score'],
#                 'answer_id': result['answer_id']
#             }))
#         except Question.DoesNotExist:
#             await self.send(text_data=json.dumps({
#                 'type': 'error',
#                 'message': 'Question not found'
#             }))
#         except Exception as e:
#             print(f"Error submitting answer: {e}")
#             await self.send(text_data=json.dumps({
#                 'type': 'error',
#                 'message': f'Error submitting answer: {str(e)}'
#             }))
    
#     async def handle_finish_interview(self):
#         """Handle request to finish the interview"""
#         try:
#             # Make hiring decision
#             result = await self.make_hire_decision()
            
#             # Send results
#             await self.send(text_data=json.dumps({
#                 'type': 'interview_result',
#                 'decision': result['decision'],
#                 'probability': result['probability'],
#                 'assessment_id': self.assessment.id
#             }))
#         except Exception as e:
#             print(f"Error finishing interview: {e}")
#             await self.send(text_data=json.dumps({
#                 'type': 'error',
#                 'message': f'Error finishing interview: {str(e)}'
#             }))