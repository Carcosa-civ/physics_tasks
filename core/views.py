"""Представления для обработки запросов."""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import (
    Topic, Article, Problem, Test, TestAttempt, TestAnswer,
    BrainstormAttempt, BrainstormAnswer
)
from .forms import ProblemSolveForm, ProblemCreateForm, BrainstormForm, RegistrationForm
from .utils import generate_brainstorm_problems


def _check_answer(user_answer, correct_answer):
    """Сравнивает ответ пользователя с правильным (без учёта пробелов)."""
    return user_answer.strip() == correct_answer.strip()


def register(request):
    """Регистрация нового пользователя."""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            from django.contrib.auth.models import User
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('core:article_list')
    else:
        form = RegistrationForm()
    return render(request, 'core/registration.html', {'form': form})


def custom_logout(request):
    """Выход из системы и перенаправление на главную."""
    logout(request)
    return redirect('core:article_list')


def article_list(request):
    """Список всех статей учебника."""
    articles = Article.objects.select_related('topic').all()
    return render(request, 'core/article_list.html', {'articles': articles})


def article_detail(request, slug):
    """Детальная страница статьи по slug темы."""
    topic = get_object_or_404(Topic, slug=slug)
    article = get_object_or_404(Article, topic=topic)
    problems = Problem.objects.filter(topic=topic)
    test = Test.objects.filter(topic=topic).first()
    return render(request, 'core/article_detail.html', {
        'article': article,
        'problems': problems,
        'test': test,
    })


def problem_list(request):
    """Список задач с фильтрацией по теме."""
    problems = Problem.objects.select_related('topic').all()
    topics = Topic.objects.all()
    selected_topic = request.GET.get('topic')
    if selected_topic:
        problems = problems.filter(topic__slug=selected_topic)
    return render(request, 'core/problem_list.html', {
        'problems': problems,
        'topics': topics,
        'selected_topic': selected_topic,
    })


def problem_detail(request, problem_id):
    """Страница решения задачи."""
    problem = get_object_or_404(Problem, pk=problem_id)
    result = None
    if request.method == 'POST':
        form = ProblemSolveForm(request.POST)
        if form.is_valid():
            user_answer = form.cleaned_data['answer']
            is_correct = _check_answer(user_answer, problem.correct_answer)
            result = {'is_correct': is_correct, 'correct': problem.correct_answer}
    else:
        form = ProblemSolveForm()
    similar_problems = Problem.objects.filter(topic=problem.topic).exclude(
        pk=problem.id
    )[:5]
    return render(request, 'core/problem_detail.html', {
        'problem': problem,
        'form': form,
        'result': result,
        'similar_problems': similar_problems,
    })


@login_required
def problem_create(request):
    """Создание новой задачи авторизованным пользователем."""
    if request.method == 'POST':
        form = ProblemCreateForm(request.POST)
        if form.is_valid():
            problem = form.save(commit=False)
            problem.author = request.user
            problem.save()
            messages.success(request, 'Задача успешно создана!')
            return redirect('core:problem_detail', problem_id=problem.pk)
    else:
        form = ProblemCreateForm()
    return render(request, 'core/problem_create.html', {'form': form})


def test_list(request):
    """Список всех контрольных работ."""
    tests = Test.objects.select_related('topic').all()
    return render(request, 'core/test_list.html', {'tests': tests})


@login_required
def test_take(request, test_id):
    """Пошаговое прохождение контрольной работы."""
    test = get_object_or_404(Test, pk=test_id)
    problems_ordered = test.testproblem_set.select_related('problem').order_by('order')
    problems_list = [item.problem for item in problems_ordered]
    total = len(problems_list)
    if total == 0:
        messages.error(request, 'В этой контрольной работе нет задач.')
        return redirect('core:test_list')

    session_key = f'test_{test_id}_answers'
    if request.method == 'POST':
        current_index = int(request.POST.get('current_index', 0))
        user_answer = request.POST.get('answer', '')
        answers = request.session.get(session_key, [])
        while len(answers) <= current_index:
            answers.append('')
        answers[current_index] = user_answer
        request.session[session_key] = answers
        if current_index + 1 >= total:
            return redirect('core:test_result', test_id=test_id)
        return redirect('core:test_take', test_id=test_id)

    # GET: текущий вопрос
    answers = request.session.get(session_key, [])
    current_index = len(answers)
    if current_index >= total:
        return redirect('core:test_result', test_id=test_id)
    current_problem = problems_list[current_index]
    form = ProblemSolveForm()
    return render(request, 'core/test_take.html', {
        'test': test,
        'problem': current_problem,
        'current_index': current_index,
        'total': total,
        'form': form,
    })


@login_required
def test_result(request, test_id):
    """Результаты контрольной работы."""
    test = get_object_or_404(Test, pk=test_id)
    session_key = f'test_{test_id}_answers'
    answers = request.session.get(session_key, [])
    problems_ordered = test.testproblem_set.select_related('problem').order_by('order')
    problems_list = [item.problem for item in problems_ordered]
    total = len(problems_list)
    if not answers or len(answers) != total:
        return redirect('core:test_take', test_id=test_id)

    results = []
    correct_count = 0
    for idx, problem in enumerate(problems_list):
        user_ans = answers[idx] if idx < len(answers) else ''
        is_correct = _check_answer(user_ans, problem.correct_answer)
        if is_correct:
            correct_count += 1
        results.append({
            'problem': problem,
            'user_answer': user_ans,
            'is_correct': is_correct,
            'correct_answer': problem.correct_answer,
        })

    attempt = TestAttempt.objects.create(
        user=request.user,
        test=test,
        completed_at=timezone.now(),
        score=correct_count
    )
    for idx, problem in enumerate(problems_list):
        TestAnswer.objects.create(
            attempt=attempt,
            problem=problem,
            user_answer=answers[idx],
            is_correct=results[idx]['is_correct']
        )
    if session_key in request.session:
        del request.session[session_key]

    return render(request, 'core/test_result.html', {
        'test': test,
        'results': results,
        'score': correct_count,
        'total': total,
    })


@login_required
def brainstorm_form(request):
    """Форма настройки мозгового штурма."""
    if request.method == 'POST':
        form = BrainstormForm(request.POST)
        if form.is_valid():
            num_questions = form.cleaned_data['num_questions']
            topics = form.cleaned_data['topics']
            try:
                problems = generate_brainstorm_problems(topics, num_questions)
            except ValueError as error:
                messages.error(request, str(error))
                return redirect('core:brainstorm_form')
            request.session['brainstorm_problems'] = [p.id for p in problems]
            request.session['brainstorm_answers'] = []
            request.session['brainstorm_topics'] = [t.id for t in topics]
            return redirect('core:brainstorm_take')
    else:
        form = BrainstormForm()
    return render(request, 'core/brainstorm_form.html', {'form': form})


@login_required
def brainstorm_take(request):
    """Пошаговое прохождение мозгового штурма."""
    problem_ids = request.session.get('brainstorm_problems')
    if not problem_ids:
        return redirect('core:brainstorm_form')
    problems = [get_object_or_404(Problem, pk=pid) for pid in problem_ids]
    answers = request.session.get('brainstorm_answers', [])
    current_index = len(answers)
    total = len(problems)
    if current_index >= total:
        return redirect('core:brainstorm_result')

    current_problem = problems[current_index]
    if request.method == 'POST':
        form = ProblemSolveForm(request.POST)
        if form.is_valid():
            user_answer = form.cleaned_data['answer']
            answers.append(user_answer)
            request.session['brainstorm_answers'] = answers
            return redirect('core:brainstorm_take')
    else:
        form = ProblemSolveForm()
    return render(request, 'core/brainstorm_take.html', {
        'problem': current_problem,
        'current_index': current_index + 1,
        'total': total,
        'form': form,
    })


@login_required
def brainstorm_result(request):
    """Результаты мозгового штурма."""
    problem_ids = request.session.get('brainstorm_problems')
    answers = request.session.get('brainstorm_answers', [])
    if not problem_ids or not answers:
        return redirect('core:brainstorm_form')
    problems = [get_object_or_404(Problem, pk=pid) for pid in problem_ids]
    if len(answers) != len(problems):
        return redirect('core:brainstorm_take')

    results = []
    correct_count = 0
    for problem, user_ans in zip(problems, answers):
        is_correct = _check_answer(user_ans, problem.correct_answer)
        if is_correct:
            correct_count += 1
        results.append({
            'problem': problem,
            'user_answer': user_ans,
            'is_correct': is_correct,
            'correct_answer': problem.correct_answer,
        })

    topic_ids = request.session.get('brainstorm_topics', [])
    topic_objects = Topic.objects.filter(id__in=topic_ids)
    topic_slugs = ','.join([topic.slug for topic in topic_objects])
    attempt = BrainstormAttempt.objects.create(
        user=request.user,
        topics=topic_slugs,
        num_questions=len(problems),
        completed_at=timezone.now(),
        score=correct_count
    )
    for problem, user_ans in zip(problems, answers):
        is_correct = _check_answer(user_ans, problem.correct_answer)
        BrainstormAnswer.objects.create(
            attempt=attempt,
            problem=problem,
            user_answer=user_ans,
            is_correct=is_correct
        )
    for key in ['brainstorm_problems', 'brainstorm_answers', 'brainstorm_topics']:
        if key in request.session:
            del request.session[key]

    return render(request, 'core/brainstorm_result.html', {
        'results': results,
        'score': correct_count,
        'total': len(problems),
    })