import json
import urllib.parse
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from AiQuetionare.models import *
from AiQuetionare.serializer import *
from asgiref.sync import sync_to_async

class InterviewConsumer(AsyncWebsocketConsumer):
    async def get_job_description(self, job_desc_id):
        try:
            job_description = await sync_to_async(JobDescription.objects.get)(id=job_desc_id)
            return job_description
        except JobDescription.DoesNotExist:
            return None
    
    async def get_next_question(self, assessment):
        # Get the next question for the current assessment
        try:
            if assessment.current_question:
                # Fetch next question based on the relationship graph
                next_relationship = await sync_to_async(
                    lambda: QuestionRelationship.objects.filter(from_question=assessment.current_question).first()
                )()
                return next_relationship.to_question if next_relationship else None
            else:
                # If this is the first question, pick any from the job's categories
                job_description = assessment.job_description
                return await sync_to_async(
                    lambda: Question.objects.filter(category__in=job_description.skills.all()).first()
                )()
        except Exception as e:
            print(f"Error in get_next_question: {e}")
            return None
    
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

            # Get or create the candidate and assessment
            candidate, _ = await sync_to_async(Candidate.objects.get_or_create)(user_id=user_id)
            assessment, _ = await sync_to_async(Assessment.objects.get_or_create)(
                candidate=candidate, job_description=get_job_description
            )

            # Send the first question
            next_question = await self.get_next_question(assessment)
            if next_question:
                assessment.current_question = next_question
                await sync_to_async(assessment.save)()
                await self.send(json.dumps({
                    "type": "question",
                    "question": next_question.question_text
                }))
            else:
                await self.send(json.dumps({
                    "type": "end",
                    "message": "No more questions available."
                }))
            await self.accept()
        except Exception as e:
            print(f"Error in connect: {e}")
            await self.close()
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            user_id = self.scope['user'].id
            assessment = await sync_to_async(Assessment.objects.get)(
                candidate__user_id=user_id,
                job_description_id=self.room_name
            )
            
            # Save the candidate's answer
            question = assessment.current_question
            candidate_answer = CandidateAnswer(
                assessment=assessment,
                question=question,
                answer_text=data.get("answer"),
                similarity_score=0.0  # Placeholder, calculate similarity using Gemini
            )
            await sync_to_async(candidate_answer.save)()
            
            # Fetch the next question
            next_question = await self.get_next_question(assessment)
            if next_question:
                assessment.current_question = next_question
                await sync_to_async(assessment.save)()
                await self.send(json.dumps({
                    "type": "question",
                    "question": next_question.question_text
                }))
            else:
                # End the interview if no more questions
                assessment.is_complete = True
                await sync_to_async(assessment.save)()
                await self.send(json.dumps({
                    "type": "end",
                    "message": "Interview complete. You will be notified soon."
                }))
            
        except Exception as e:
            print(f"Error in receive: {e}")
    
    async def disconnect(self, close_code):
        try:
            self.room_group_name = f'interview_{self.room_name}_userid{self.scope['user'].id}'
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            print(f"Error in disconnect: {e}")
