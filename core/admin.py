"""Настройка административной панели."""
from django.contrib import admin
from .models import (
    Topic, Article, Problem, Test, TestProblem,
    TestAttempt, TestAnswer, BrainstormAttempt, BrainstormAnswer
)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """Администрирование тем."""
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Администрирование статей."""
    list_display = ('title', 'topic', 'created_at')
    list_filter = ('topic',)


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    """Администрирование задач."""
    list_display = ('title', 'topic', 'author', 'created_at')
    list_filter = ('topic', 'author')
    search_fields = ('title', 'condition')


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    """Администрирование контрольных работ."""
    list_display = ('title', 'topic', 'created_by')
    list_filter = ('topic',)


@admin.register(TestProblem)
class TestProblemAdmin(admin.ModelAdmin):
    """Администрирование порядка задач в контрольной."""
    list_display = ('test', 'problem', 'order')
    list_filter = ('test',)


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    """Администрирование попыток контрольных."""
    list_display = ('user', 'test', 'score', 'completed_at')
    list_filter = ('test', 'user')


@admin.register(TestAnswer)
class TestAnswerAdmin(admin.ModelAdmin):
    """Администрирование ответов в контрольной."""
    list_display = ('attempt', 'problem', 'is_correct')


@admin.register(BrainstormAttempt)
class BrainstormAttemptAdmin(admin.ModelAdmin):
    """Администрирование попыток мозгового штурма."""
    list_display = ('user', 'num_questions', 'score', 'completed_at')


@admin.register(BrainstormAnswer)
class BrainstormAnswerAdmin(admin.ModelAdmin):
    """Администрирование ответов в мозговом штурме."""
    list_display = ('attempt', 'problem', 'is_correct')