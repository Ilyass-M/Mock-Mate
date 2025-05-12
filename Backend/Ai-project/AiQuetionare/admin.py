from django.contrib import admin

from AiQuetionare.models import (
    CustomUser,
    Skill,
    JobDescription,
    Category,
    Question,
    Candidate,
    Assessment,
    CandidateAnswer,
    
)
class JobDescriptionAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name="recruiter").exists():
            return qs.filter(created_by=request.user)
        return qs

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "created_by":
            kwargs["queryset"] = CustomUser.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class AssessmentAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "job_description":
            if request.user.groups.filter(name="recruiter").exists():
                kwargs["queryset"] = JobDescription.objects.filter(created_by=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name="recruiter").exists():
            return qs.filter(job_description__created_by=request.user)
        return qs
admin.site.register(CustomUser)
admin.site.register(Skill)
admin.site.register(JobDescription, JobDescriptionAdmin)
admin.site.register(Category)
admin.site.register(Question)
# admin.site.register(QuestionRelationship)
admin.site.register(Candidate)
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(CandidateAnswer)
