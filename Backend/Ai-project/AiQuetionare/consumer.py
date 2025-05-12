import json
import urllib.parse
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
# import asyncio
from AiQuetionare.models import Candidate, JobDescription, Question, Assessment, CandidateAnswer
from AiQuetionare.serializer import CandidateSerializer, JobDescriptionSerializer, QuestionSerializer, AssessmentSerializer, CandidateAnswerSerializer
from asgiref.sync import sync_to_async, async_to_sync
from sentence_transformers import util
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import pickle
import random
from collections import defaultdict
from django.db.models import Avg

class InterviewConsumer(AsyncWebsocketConsumer):
    async def get_job_description(self, job_desc_id):
        try:
            job_description = await sync_to_async(JobDescription.objects.get)(id=job_desc_id)
            return job_description
        except JobDescription.DoesNotExist:
            return None
    
    async def get_or_create_assessment(self, job_desc_id):
        try:
            job_description = await self.get_job_description(job_desc_id)
            if not job_description:
                return None
            getcandidate = await sync_to_async(Candidate.objects.get)(user=self.scope['user'].id)
            self.candidate = getcandidate
            assessment, created = await sync_to_async(Assessment.objects.get_or_create)(
                job_description=job_description,
                candidate=self.candidate,
            )
            
            return assessment
        except Exception as e:
            print(f"Error in get_or_create_assessment: {e}")
            return None

    async def load_sentence_transformer_model(self):
        from sentence_transformers import SentenceTransformer
        try:
            if not hasattr(self, '_cached_model'):
                print("Loading SentenceTransformer model...")
                self._cached_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Model loaded successfully.")
            return self._cached_model
        except Exception as e:
            print(f"Error loading sentence transformer model: {e}")
            return None
    
    @database_sync_to_async
    def get_job_skills(self, job_description_id):
        """Get the skills required for the job"""
        try:
            job_description = JobDescription.objects.get(id=job_description_id)
            return list(job_description.skills.values_list('name', flat=True))
        except Exception as e:
            print(f"Error getting job skills: {e}")
            return []
    @database_sync_to_async
    def get_candidate_skills(self):
        """Get the candidate's skills"""
        try:
            candidate = Candidate.objects.get(user=self.scope['user'])
            return list(candidate.skills.values_list('name', flat=True))
        except Exception as e:
            print(f"Error getting candidate skills: {e}")
            return []
        
    def calculate_max_similarity(self, question_embedding, skill_embeddings):
        """Calculates the maximum cosine similarity between a question and any of the provided skills."""
        if not skill_embeddings:
            return 0.0
        similarities = [cosine_similarity([skill_embedding], [question_embedding])[0][0]
                        for skill_embedding in skill_embeddings]
        # print(max(similarities))
        return max(similarities) if similarities else 0.0
    
    def calculate_avg_similarity(self, question_embedding, user_skill_embeddings):
        """Calculates the average cosine similarity between a question and any of the user's skills."""
        if not user_skill_embeddings:
            return 0.0
        similarities = [cosine_similarity([skill_embedding], [question_embedding])[0][0]
                        for skill_embedding in user_skill_embeddings]
        # print(sum(similarities) / len(similarities) if similarities else 0.0)
        return sum(similarities) / len(similarities) if similarities else 0.0
    

    async def calculate_question_scores(self, job_skills, candidate_skills):
        """Calculate scores for questions based on skills"""
        try:
            questions = await sync_to_async(lambda: list(Question.objects.all().values('question_text', 'embedding', 'id', 'question_number', 'category', 'difficulty')))()
            # print("questions", questions)
            if not questions:
                return pd.DataFrame()
            questions_data = []
            job_skill_embeddings = [self._cached_model.encode(skill) for skill in job_skills]
            user_skill_embeddings = [self._cached_model.encode(skill) for skill in candidate_skills]
            # print("Hello1")
            for question in questions:
                # print("Hello")
                question_embedding = np.array(question['embedding']) if question['embedding'] else self._cached_model.encode(question['question_text'])
                # print("test")
                jd_score = self.calculate_max_similarity(question_embedding, job_skill_embeddings)
                user_score = self.calculate_avg_similarity(question_embedding, user_skill_embeddings)
                # print("questions", questions)
                score = 0.6 * jd_score + 0.4 * user_score
                asked = await sync_to_async(
                    lambda: CandidateAnswer.objects.filter(
                        assessment=self.assessment, question=question['id']
                    ).exists()
                )()
                if( not asked):
                    questions_data.append({
                        'question_number': question['question_number'],
                        'category': question['category'],
                        'difficulty': question['difficulty'],
                        'jd_score': jd_score,
                        'user_score': user_score,
                        'score': score,
                        'asked': asked
                    })
                # print("Questions_data", questions_data)
            return pd.DataFrame(questions_data)
        except Exception as e:
            print(f"Error calculating question scores: {e}")
            return pd.DataFrame()
        
    async def build_question_graph(self, questions_df):
        """Build a graph of questions based on difficulty and category"""
        try:
            graph = defaultdict(list)
            
            for category in questions_df["category"].unique():
                cat_qs = questions_df[questions_df["category"] == category].sort_values("difficulty")
                prev_row = None
                for _, current_row in cat_qs.iterrows():
                    if prev_row is not None:
                        graph[prev_row["question_number"]].append(current_row["question_number"])
                    prev_row = current_row
            
            return graph
        except Exception as e:
            print(f"Error building question graph: {e}")
            return defaultdict(list)
    
    def a_star_search(self, graph, start, scores, asked_nodes, threshold=0.99):
        """
        A* search algorithm to find the best question
        
        Args:
            graph: dict of adjacency list for the tree {node: [children]}
            start: starting node id
            scores: dict of scores for each node
            asked_nodes: set of nodes (question numbers) that have already been asked
            threshold: early stopping threshold if a node is highly similar
        """
        import heapq
        
        open_set = []
        heapq.heappush(open_set, (1 - scores.get(start, 0), start))
        came_from = {}
        g_score = {start: 0}
        best_node = start
        best_score = scores.get(start, 0)
        
        while open_set:
            _, current = heapq.heappop(open_set)
            
            if current in asked_nodes:
                continue
                
            if scores.get(current, 0) > best_score:
                best_node = current
                best_score = scores.get(current, 0)
                
            if scores.get(current, 0) >= threshold:
                break
                
            for neighbor in graph.get(current, []):
                if neighbor in asked_nodes:
                    continue
                    
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + (1 - scores.get(neighbor, 0))
                    heapq.heappush(open_set, (f_score, neighbor))
        
        path = []
        current = best_node
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.append(start)
        return path[::-1], best_node, best_score
    

    async def select_next_question(self, questions_df):
        """Select the next question using the A* algorithm"""
        try:
            if questions_df.empty:
                return None
            
            # Get top 5 categories
            category_scores = questions_df.groupby("category")["score"].max()
            top_5_categories = category_scores.sort_values(ascending=False).head(5).index.tolist()
            
            if not top_5_categories:
                return None
                
            # Randomly select a category
            selected_category = random.choice(top_5_categories)
            
            # Filter questions by category and get the easiest one as starting point
            cat_df = questions_df[questions_df["category"] == selected_category].sort_values("difficulty", ascending=False)
            
            if cat_df.empty:
                return None
                
            start_q = cat_df["question_number"].values[0]
            asked_nodes = set(questions_df[questions_df["asked"] == True]["question_number"])
            score_dict = dict(zip(questions_df["question_number"], questions_df["score"]))
            
            # Build graph
            graph = await self.build_question_graph(questions_df)
            
            # Run A* algorithm
            path, best_node, best_score = self.a_star_search(graph, start_q, score_dict, asked_nodes)
            
            # If question already asked, try again with an empty asked set
            if path[-1] in asked_nodes:
                path, best_node, best_score = self.a_star_search(graph, start_q, score_dict, set())
            
            # Get the question object
            question = await sync_to_async(
                lambda: Question.objects.get(question_number=path[-1])
            )()

            # print("Selected question:", question)

            # Update the current question in the assessment
            self.assessment.current_question = question
            await sync_to_async(self.assessment.save)()
            
            Question_obj = await sync_to_async(
                lambda: Question.objects.filter(question_number=path[-1]).values('id', 'question_text', 'category', 'difficulty','question_number',
                'category').first()
            )()
            return Question_obj
        except Exception as e:
            print(f"Error selecting next question: {e}")
            return None
    
    
    async def evaluate_answer(self, question, answer_text):
        from sentence_transformers import SentenceTransformer, util
        """Evaluate the candidate's answer using semantic similarity"""
        try:
            # Get original answer
            original_answer = await sync_to_async(lambda: question.answer)()

            # Load model
            model = self._cached_model or SentenceTransformer('all-MiniLM-L6-v2')

            # Compute embeddings
            embedding_orig = model.encode(original_answer)
            embedding_user = model.encode(answer_text)

            # Compute similarity score
            similarity_score = util.cos_sim(embedding_orig, embedding_user).item()

            # Calculate response time
            now = timezone.now()
            
            # Get assessment start time using sync_to_async
            assessment_start_time = await sync_to_async(lambda: self.assessment.start_time)()
            response_time = (now - assessment_start_time).total_seconds()

            # Create or update the answer using sync_to_async
            candidate_answer = await sync_to_async(CandidateAnswer.objects.update_or_create)(
                assessment=self.assessment,
                question=question,
                defaults={
                    'answer_text': answer_text,
                    'similarity_score': similarity_score,
                    'response_time_seconds': response_time
                }
            )
            answer = candidate_answer[0]  # update_or_create returns (object, created) tuple

            # Update question score based on original score + similarity
            alpha = 0.7
            beta = 0.3

            # Ensure job_skills and candidate_skills are awaited properly
            job_skills = await self.get_job_skills(await sync_to_async(lambda: self.assessment.job_description.id)())
            candidate_skills = await self.get_candidate_skills()
            questions_df = await self.calculate_question_scores(job_skills, candidate_skills)

            # Get question number using sync_to_async
            question_number = await sync_to_async(lambda: question.question_number)()
            qn_row = questions_df[questions_df["question_number"] == question_number]
            
            if not qn_row.empty:
                original_score = qn_row["score"].values[0]
                updated_score = alpha * original_score + beta * similarity_score
                
                # Update the answer with the score
                await sync_to_async(lambda: setattr(answer, 'question_score', updated_score))()
                await sync_to_async(answer.save)()

            return {
                'similarity_score': similarity_score,
                'answer_id': answer.id
            }

        except Exception as e:
            print(f"Error evaluating answer: {e}")
            return {'similarity_score': 0.0, 'answer_id': None}


    async def load_ml_model(self):
        """Load or train an ML model for hiring decisions"""
        try:
            from sklearn.tree import DecisionTreeClassifier
            import pickle
            import os
            
            # First, check if there's a saved model
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml_models', 'hiring_model.pkl')
            
            if os.path.exists(model_path):
                # Load existing model
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
                print("Loaded existing hiring model")
                self.ml_model = model
                return model
            else:
                # Create a default model with sample data
                print("Creating new hiring model with default data")
                # Sample data for model training
                fixed_data = {
                    'cv_match_score': [0.85, 0.92, 0.75, 0.60, 0.95, 0.78, 0.55, 0.88, 0.70, 0.90,
                                    0.65, 0.50, 0.82, 0.98, 0.72, 0.68, 0.80, 0.91, 0.58, 0.77],
                    'weighted_score': [0.82, 0.91, 0.70, 0.55, 0.95, 0.75, 0.48, 0.89, 0.68, 0.92,
                                    0.60, 0.45, 0.80, 0.98, 0.71, 0.62, 0.78, 0.90, 0.51, 0.73],
                    'hire_decision':  [1, 1, 1, 0, 1, 1, 0, 1, 0, 1,
                                    0, 0, 1, 1, 1, 0, 1, 1, 0, 1]
                }
                
                dataset_df = pd.DataFrame(fixed_data)
                
                # Train model
                feature_cols = ["cv_match_score", "weighted_score"]
                target_col = "hire_decision"
                
                X = dataset_df[feature_cols]
                y = dataset_df[target_col]
                
                # Simple decision tree model
                model = DecisionTreeClassifier(random_state=42, max_depth=3)
                model.fit(X, y)
                
                # Save model if directory exists
                try:
                    os.makedirs(os.path.dirname(model_path), exist_ok=True)
                    with open(model_path, 'wb') as f:
                        pickle.dump(model, f)
                    print(f"Model saved to {model_path}")
                except Exception as e:
                    print(f"Could not save model: {e}")
                
                self.ml_model = model
                return model
                
        except Exception as e:
            print(f"Error loading ML model: {e}")
            return None

    async def make_hire_decision(self):
        """Make a hiring decision based on the ML model"""
        try:
            # Calculate average scores
            answers = await sync_to_async(CandidateAnswer.objects.filter)(assessment=self.assessment)
            
            if not await sync_to_async(answers.exists)():
                return {"decision": "Not enough data", "probability": [0.5, 0.5]}
            
            # Get average question score
            avg_result = await sync_to_async(answers.aggregate)(Avg('question_score'))
            avg_weighted_score = avg_result.get('question_score__avg', 0.0) or 0.0
            
            # Get CV match score - properly handling async context
            candidate = await sync_to_async(lambda: self.assessment.candidate)()
            cv_match_score = await sync_to_async(lambda: getattr(candidate, 'cv_match_score', 0.7))()
            
            # Create data for prediction
            new_candidate_data = pd.DataFrame({
                "cv_match_score": [cv_match_score],
                "weighted_score": [avg_weighted_score]
            })
            
            # Load ML model if not already loaded
            if not hasattr(self, 'ml_model') or self.ml_model is None:
                self.ml_model = await self.load_ml_model()
            
            if not self.ml_model:
                return {"decision": "No model available", "probability": [0.5, 0.5]}
            
            # Make prediction
            prediction = self.ml_model.predict(new_candidate_data)
            probability = self.ml_model.predict_proba(new_candidate_data)
            
            # Update assessment
            await sync_to_async(lambda: setattr(self.assessment, 'weighted_score', avg_weighted_score))()
            await sync_to_async(lambda: setattr(self.assessment, 'hire_decision', bool(prediction[0] == 1)))()
            await sync_to_async(lambda: setattr(self.assessment, 'hire_probability', float(probability[0][1])))()  # Probability of hire (class 1)
            await sync_to_async(lambda: setattr(self.assessment, 'is_complete', True))()
            await sync_to_async(lambda: setattr(self.assessment, 'end_time', timezone.now()))()
            await sync_to_async(self.assessment.save)()
            
            return {
                "decision": "Hire" if prediction[0] == 1 else "Not Hire",
                "probability": probability[0].tolist()
            }
        except Exception as e:
            print(f"Error making hire decision: {e}")
            return {"decision": "Error", "probability": [0.5, 0.5]}
    async def handle_submit_answer(self, question_id, answer_text):
        """Handle submission of an answer"""
        try:
            # Get the question
            question = await sync_to_async(Question.objects.get)(id=question_id)
            
            # Evaluate the answer
            result = await self.evaluate_answer(question, answer_text)
            
            # Send response
            await self.send(text_data=json.dumps({
                'type': 'answer_evaluation',
                'question_id': question_id,
                'similarity_score': result['similarity_score'],
                'answer_id': result['answer_id']
            }))
        except Question.DoesNotExist:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Question not found'
            }))
        except Exception as e:
            print(f"Error submitting answer: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error submitting answer: {str(e)}'
            }))
    
    async def handle_finish_interview(self):
        """Handle request to finish the interview"""
        try:
            # Make hiring decision
            result = await self.make_hire_decision()
            
            # Send results
            await self.send(text_data=json.dumps({
                'type': 'interview_result',
                'decision': result['decision'],
                'probability': result['probability'],
                'assessment_id': self.assessment.id
            }))
        except Exception as e:
            print(f"Error finishing interview: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error finishing interview: {str(e)}'
            }))
    def handle_get_question(self):
        # print("hello", self.assessment.job_description.id)
        job_skills = async_to_sync(self.get_job_skills)(self.assessment.job_description.id)
        candidate_skills = async_to_sync(self.get_candidate_skills)()
        questions_df = async_to_sync(self.calculate_question_scores)(job_skills, candidate_skills)
        question = async_to_sync(self.select_next_question)(questions_df)
        # print("question selected", question)
        if question:
            question_data = {
                'question_number': question['question_number'],
                'question_text': question['question_text'],
                'category': question['category'],
                'difficulty': question['difficulty']
            }
            
            async_to_sync(self.send)(text_data=json.dumps({
                'type': 'question',
                'question': question_data
            }))
        else:
            async_to_sync(self.send)(text_data=json.dumps({
                'type': 'error',
                'message': 'No more questions available'
            }))

    async def connect(self):
        try:
            self.room_name = self.scope['url_route']['kwargs']['job_desc_id']
            if self.scope['user'].is_anonymous:
                await self.close(code=401)
                return

            get_job_description = await self.get_job_description(self.room_name)
            if not get_job_description:
                await self.close(code=404)
                return

            user_id = self.scope['user'].id
            self.room_group_name = f'interview_{self.room_name}_userid{user_id}'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            self.assessment = await self.get_or_create_assessment(self.room_name)
            if not self.assessment:
                await self.close(code=500)
                return
            self.model = await self.load_sentence_transformer_model()
            if not self.model:
                await self.close(code=500)
                return
            
        except Exception as e:
            print(f"Error in connect: {e}")
            await self.close()
    
    
    
    async def disconnect(self, close_code):
        try:
            self.room_group_name = f'interview_{self.room_name}_userid{self.scope['user'].id}'
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            print(f"Error in disconnect: {e}")

    async def receive(self, text_data=None):
        try:
            data = json.loads(text_data)  # Parse the incoming JSON data
            message_type = data.get('type')
            if message_type == 'get_question':
                await sync_to_async(self.handle_get_question)()
            # Add other message types as needed
            elif message_type == 'submit_answer':
                question_id = data.get('question_id')
                answer_text = data.get('answer')
                if not question_id or not answer_text:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'Invalid data'
                    }))
                    return
                await self.handle_submit_answer(question_id, answer_text)
            elif message_type == 'finish_interview':
                await self.handle_finish_interview()
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Unknown message type'
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            print(f"Error in receive: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'An error occurred: {str(e)}'
            }))

