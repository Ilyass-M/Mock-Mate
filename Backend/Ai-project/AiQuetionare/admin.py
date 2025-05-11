from django.contrib import admin

from AiQuetionare.models import (
    CustomUser,
    Skill,
    JobDescription,
    Category,
    Question,
    QuestionRelationship,
    Candidate,
    Assessment,
    CandidateAnswer,
    MLModel
)

admin.site.register(CustomUser)
admin.site.register(Skill)
admin.site.register(JobDescription)
admin.site.register(Category)
admin.site.register(Question)
admin.site.register(QuestionRelationship)
admin.site.register(Candidate)
admin.site.register(Assessment)
admin.site.register(CandidateAnswer)
admin.site.register(MLModel)