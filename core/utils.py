"""Вспомогательные функции для генерации случайных задач."""
import random
from .models import Topic, Problem


def generate_brainstorm_problems(topics, num_questions):
    """
    Генерирует список уникальных задач для мозгового штурма.

    Аргументы:
        topics: QuerySet или список тем Topic.
        num_questions: общее количество задач (не менее количества тем).

    Возвращает:
        Список объектов Problem (уникальных).

    Исключения:
        ValueError: если для какой-либо темы нет задач.
    """
    selected_topics = list(topics)
    problems_by_topic = {}
    for topic in selected_topics:
        problems_list = list(topic.problems.all())
        if not problems_list:
            raise ValueError(f'Нет задач по теме "{topic.name}"')
        problems_by_topic[topic] = problems_list

    # Берём по одной случайной задаче с каждой темы
    mandatory_problems = [
        random.choice(problems_by_topic[topic]) for topic in selected_topics
    ]

    # Все задачи из выбранных тем (без дубликатов)
    all_problems = set()
    for topic in selected_topics:
        all_problems.update(problems_by_topic[topic])
    all_problems = list(all_problems)

    # Оставшиеся задачи
    remaining_pool = [p for p in all_problems if p not in mandatory_problems]
    needed = num_questions - len(mandatory_problems)
    if needed > 0:
        if needed > len(remaining_pool):
            extra_problems = random.choices(remaining_pool, k=needed)
        else:
            extra_problems = random.sample(remaining_pool, needed)
    else:
        extra_problems = []

    result = mandatory_problems + extra_problems
    random.shuffle(result)
    return result