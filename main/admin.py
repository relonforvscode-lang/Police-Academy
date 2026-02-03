from django.contrib import admin
from .models import Application, Question, TestSession, ApplicantAnswer
from .models import ApplicationSetting, AuditLog, AuditTemplate


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
	list_display = ('id', 'character_name', 'discord_id', 'status', 'submitted_at')
	list_filter = ('status',)
	search_fields = ('character_name', 'discord_id')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = ('id', 'text', 'correct_index')
	search_fields = ('text',)


@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
	list_display = ('id', 'application', 'started_at', 'finished_at', 'is_active', 'score')
	search_fields = ('application__character_name', 'application__discord_id')


@admin.register(ApplicantAnswer)
class ApplicantAnswerAdmin(admin.ModelAdmin):
	list_display = ('id', 'session', 'question', 'selected_index', 'is_correct', 'answered_at')


@admin.register(ApplicationSetting)
class ApplicationSettingAdmin(admin.ModelAdmin):
	list_display = ('status', 'reopen_at', 'updated_at')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
	list_display = ('id', 'actor', 'action', 'target', 'created_at')
	search_fields = ('action', 'target', 'actor__username')
	readonly_fields = ('actor', 'action', 'target', 'details', 'created_at')


@admin.register(AuditTemplate)
class AuditTemplateAdmin(admin.ModelAdmin):
	list_display = ('key', 'updated_at')
	search_fields = ('key',)
