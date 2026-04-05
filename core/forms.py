"""Формы для ввода данных."""
from django import forms
from .models import Problem, Topic


class ProblemSolveForm(forms.Form):
    """Форма для ввода ответа на задачу."""
    answer = forms.CharField(
        label='Ваш ответ',
        max_length=500,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


class ProblemCreateForm(forms.ModelForm):
    """Форма создания новой задачи."""
    class Meta:
        model = Problem
        fields = ['title', 'topic', 'condition', 'correct_answer']
        widgets = {
            'condition': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'correct_answer': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['topic'].queryset = Topic.objects.all()
        self.fields['topic'].widget.attrs.update({'class': 'form-control'})


class BrainstormForm(forms.Form):
    """Форма выбора тем и количества задач для мозгового штурма."""
    num_questions = forms.IntegerField(
        min_value=1, label='Количество задач'
    )
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Темы'
    )

    def clean(self):
        """Проверка: число задач не меньше количества тем."""
        cleaned_data = super().clean()
        num_questions = cleaned_data.get('num_questions')
        selected_topics = cleaned_data.get('topics')
        if num_questions and selected_topics:
            if num_questions < selected_topics.count():
                raise forms.ValidationError(
                    'Количество задач не может быть меньше количества выбранных тем.'
                )
        return cleaned_data


class RegistrationForm(forms.Form):
    """Форма регистрации нового пользователя."""
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(
        widget=forms.PasswordInput, label='Подтверждение пароля'
    )

    def clean(self):
        """Проверка совпадения паролей."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают')
        return cleaned_data