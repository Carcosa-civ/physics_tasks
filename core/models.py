"""Модели данных для приложения core."""
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Topic(models.Model):
    """Тема учебного материала."""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        """URL детальной статьи по теме."""
        return reverse('core:article_detail', args=[self.slug])


class Article(models.Model):
    """Статья учебника, связанная с темой."""
    topic = models.OneToOneField(
        Topic, on_delete=models.CASCADE, related_name='article'
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        """URL детальной страницы статьи."""
        return reverse('core:article_detail', args=[self.topic.slug])


class Problem(models.Model):
    """Задача по определённой теме."""
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name='problems'
    )
    title = models.CharField(max_length=200)
    condition = models.TextField()
    correct_answer = models.CharField(max_length=500)
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        """URL страницы решения задачи."""
        return reverse('core:problem_detail', args=[self.id])


class Test(models.Model):
    """Контрольная работа."""
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name='tests'
    )
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    problems = models.ManyToManyField(Problem, through='TestProblem')

    def __str__(self) -> str:
        return self.title


class TestProblem(models.Model):
    """Порядок задач в контрольной."""
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        unique_together = ('test', 'order')

    def __str__(self) -> str:
        return f"{self.test.title} - {self.problem.title} (order {self.order})"


class TestAttempt(models.Model):
    """Попытка прохождения контрольной."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.test.title} - {self.score}"


class TestAnswer(models.Model):
    """Ответ на задачу в контрольной."""
    attempt = models.ForeignKey(
        TestAttempt, on_delete=models.CASCADE, related_name='answers'
    )
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self) -> str:
        status = "Correct" if self.is_correct else "Wrong"
        return f"{self.attempt.user.username} - {self.problem.title} - {status}"


class BrainstormAttempt(models.Model):
    """Попытка мозгового штурма."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topics = models.TextField(help_text="Comma-separated topic slugs")
    num_questions = models.PositiveIntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.user.username} - Brainstorm - {self.score}/{self.num_questions}"


class BrainstormAnswer(models.Model):
    """Ответ на задачу в мозговом штурме."""
    attempt = models.ForeignKey(
        BrainstormAttempt, on_delete=models.CASCADE, related_name='answers'
    )
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self) -> str:
        status = "Correct" if self.is_correct else "Wrong"
        return f"{self.attempt.user.username} - {self.problem.title} - {status}"