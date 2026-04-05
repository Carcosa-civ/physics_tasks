"""Команда для загрузки тестовых данных."""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Topic, Article, Problem, Test, TestProblem


class Command(BaseCommand):
    """Загружает начальные темы, статьи, задачи и контрольные работы."""

    help = 'Загружает тестовые данные: темы, статьи, задачи, контрольные'

    def handle(self, *args, **options):
        """Основной метод команды."""
        admin, created = User.objects.get_or_create(username='admin')
        if created:
            admin.set_password('admin')
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
            self.stdout.write('Создан администратор: admin / admin')

        topics_data = [
            ('Ускорение свободного падения', 'free-fall'),
            ('Первый закон Ньютона', 'newton-1'),
            ('Второй закон Ньютона', 'newton-2'),
            ('Третий закон Ньютона', 'newton-3'),
            ('Энергия: Полная, Кинетическая, Потенциальная', 'energy'),
        ]

        for topic_name, topic_slug in topics_data:
            topic, _ = Topic.objects.get_or_create(name=topic_name, slug=topic_slug)
            article_content = (
                f"<p>Это учебная статья по теме '{topic_name}'. "
                "Здесь содержится подробное объяснение.</p>"
            )
            Article.objects.get_or_create(
                topic=topic,
                defaults={
                    'title': f'Статья: {topic_name}',
                    'content': article_content,
                }
            )

            problems_map = {
                'Ускорение свободного падения': [
                    ('Задача 1: g на Земле',
                     'Чему равно ускорение свободного падения на Земле (приблизительно)?',
                     '9.8'),
                    ('Задача 2: Высота',
                     'Тело падает с высоты 45 м. Сколько времени оно падает? (g=10 м/с²)',
                     '3'),
                ],
                'Первый закон Ньютона': [
                    ('Закон инерции',
                     'Сформулируйте первый закон Ньютона.',
                     'Существуют такие системы отсчёта, относительно которых тело сохраняет '
                     'скорость неизменной, если на него не действуют другие тела'),
                    ('Пример инерции',
                     'Почему пассажир отклоняется назад при разгоне автобуса?',
                     'Инерция'),
                ],
                'Второй закон Ньютона': [
                    ('Формула', 'Напишите формулу второго закона Ньютона.', 'F=ma'),
                    ('Сила и ускорение',
                     'Под действием силы 10 Н тело массой 2 кг движется с каким ускорением?',
                     '5'),
                ],
                'Третий закон Ньютона': [
                    ('Формулировка',
                     'Сформулируйте третий закон Ньютона.',
                     'Силы действия и противодействия равны по модулю и противоположны '
                     'по направлению'),
                    ('Пример',
                     'Человек отталкивается от лодки. Какая сила действует на лодку?',
                     'Сила отталкивания'),
                ],
                'Энергия: Полная, Кинетическая, Потенциальная': [
                    ('Кинетическая энергия', 'Формула кинетической энергии.', 'mv^2/2'),
                    ('Потенциальная энергия',
                     'Формула потенциальной энергии в поле тяжести.',
                     'mgh'),
                ],
            }

            for title, condition, correct in problems_map.get(topic_name, []):
                Problem.objects.get_or_create(
                    title=title,
                    topic=topic,
                    defaults={
                        'condition': condition,
                        'correct_answer': correct,
                        'author': admin,
                    }
                )

            test, _ = Test.objects.get_or_create(
                topic=topic,
                title=f'Контрольная по теме "{topic_name}"',
                defaults={'created_by': admin}
            )
            problems_in_topic = Problem.objects.filter(topic=topic)[:2]
            for idx, problem in enumerate(problems_in_topic):
                TestProblem.objects.get_or_create(test=test, problem=problem, order=idx)

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно загружены'))