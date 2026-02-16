# frontend/forms.py - VERSION CORRIGÉE
from django import forms
from core.models import User, Course, Enrollment, Quiz, Question, Choice, Chapter


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea'}),
            'content': forms.Textarea(attrs={'class': 'form-textarea'}),
        }


# ========== FORMULAIRES POUR LES QUIZ ==========

class QuizForm(forms.ModelForm):
    # Deux options selon ton besoin:
    
    # OPTION 1: Avec sélection de cours (pour créer_quiz_general)
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        required=True,
        label="Cours",
        help_text="Le quiz sera associé au premier chapitre de ce cours"
    )
    
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'time_limit', 'passing_score']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': 'Titre du quiz'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea', 
                'rows': 3,
                'placeholder': 'Description du quiz (optionnel)'
            }),
            'passing_score': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 0,
                'max': 100,
                'value': 70
            }),
            'time_limit': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'value': 30
            }),
        }
        help_texts = {
            'time_limit': 'Temps en minutes',
            'passing_score': 'Score minimal pour réussir (en %)',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrer les cours de l'enseignant connecté
            self.fields['course'].queryset = Course.objects.filter(teacher=user)
            self.fields['course'].widget.attrs['class'] = 'form-select'
            self.fields['course'].empty_label = "Sélectionnez un cours"
        else:
            self.fields['course'].queryset = Course.objects.none()


class QuizFormWithChapter(forms.ModelForm):
    # OPTION 2: Avec sélection de chapitre (pour création spécifique)
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'chapter', 'passing_score', 'time_limit']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': 'Titre du quiz'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea', 
                'rows': 3,
                'placeholder': 'Description du quiz (optionnel)'
            }),
            'passing_score': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 0,
                'max': 100,
                'value': 70
            }),
            'time_limit': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'value': 30
            }),
        }
    
    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        
        if teacher:
            # Filtrer les chapitres des cours de ce teacher
            self.fields['chapter'].queryset = Chapter.objects.filter(
                module__course__teacher=teacher
            )
            self.fields['chapter'].widget.attrs['class'] = 'form-select'
            self.fields['chapter'].empty_label = "Sélectionnez un chapitre"
        else:
            self.fields['chapter'].queryset = Chapter.objects.none()


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'points', 'explanation']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-textarea', 
                'rows': 3,
                'placeholder': 'Énoncé de la question'
            }),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'points': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'value': 10
            }),
            'explanation': forms.Textarea(attrs={
                'class': 'form-textarea', 
                'rows': 2,
                'placeholder': 'Explication (optionnel)'
            }),
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Texte du choix'
            }),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


# Formulaire pour créer plusieurs choix en une fois (pour MCQ)
class MultipleChoiceForm(forms.Form):
    choice_1 = forms.CharField(
        label='Choix 1',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=True
    )
    correct_1 = forms.BooleanField(
        label='Correct',
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        required=False
    )
    
    choice_2 = forms.CharField(
        label='Choix 2', 
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=True
    )
    correct_2 = forms.BooleanField(
        label='Correct',
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        required=False
    )
    
    choice_3 = forms.CharField(
        label='Choix 3',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=False
    )
    correct_3 = forms.BooleanField(
        label='Correct',
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        required=False
    )
    
    choice_4 = forms.CharField(
        label='Choix 4',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=False
    )
    correct_4 = forms.BooleanField(
        label='Correct',
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        required=False
    )


# Formulaire simple pour True/False
class TrueFalseForm(forms.Form):
    correct_answer = forms.ChoiceField(
        label='Réponse correcte',
        choices=[('true', 'Vrai'), ('false', 'Faux')],
        widget=forms.RadioSelect(attrs={'class': 'form-radio'}),
        initial='true'
    )