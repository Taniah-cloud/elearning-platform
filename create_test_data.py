import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elearning.settings')
django.setup()

from core.models import User, Course, Module, Chapter, Quiz, Question, Choice, Enrollment, Certificate
from datetime import datetime

def create_test_data():
    print("Création des données de test...")
    
    # Créer un admin
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='admin123'
    )
    admin_user.role = 'teacher'
    admin_user.save()
    
    # Créer un enseignant
    teacher = User.objects.create_user(
        username='teacher1',
        email='teacher@test.com',
        password='teacher123',
        role='teacher'
    )
    
    # Créer un étudiant
    student = User.objects.create_user(
        username='student1',
        email='student@test.com',
        password='student123',
        role='student'
    )
    
    # Créer un cours
    course = Course.objects.create(
        title='Introduction à Python',
        description='Apprenez les bases de la programmation Python',
        teacher=teacher,
        content='''# Introduction à Python

## Chapitre 1: Les Bases
- Variables et types de données
- Opérateurs
- Structures de contrôle

## Chapitre 2: Fonctions
- Définition de fonctions
- Paramètres et arguments
- Portée des variables

## Chapitre 3: Structures de données
- Listes, tuples, dictionnaires
- Compréhensions de listes
- Manipulation de fichiers
'''
    )
    
    # Créer des modules et chapitres
    module1 = Module.objects.create(
        course=course,
        title='Module 1: Les Fondamentaux'
    )
    
    chapter1 = Chapter.objects.create(
        module=module1,
        title='Chapitre 1: Variables et Types',
        content='Variables et types de données en Python'
    )
    
    # Créer un quiz
    quiz1 = Quiz.objects.create(
        chapter=chapter1,
        title='Quiz: Variables et Types'
    )
    
    # Créer des questions
    q1 = Question.objects.create(
        quiz=quiz1,
        text='Quel est le type de la valeur "Hello" en Python?'
    )
    Choice.objects.create(question=q1, text='int', is_correct=False)
    Choice.objects.create(question=q1, text='float', is_correct=False)
    Choice.objects.create(question=q1, text='str', is_correct=True)
    Choice.objects.create(question=q1, text='bool', is_correct=False)
    
    q2 = Question.objects.create(
        quiz=quiz1,
        text='Quelle est la bonne syntaxe pour créer une liste?'
    )
    Choice.objects.create(question=q2, text='list = 1,2,3', is_correct=False)
    Choice.objects.create(question=q2, text='list = [1,2,3]', is_correct=True)
    Choice.objects.create(question=q2, text='list = {1,2,3}', is_correct=False)
    Choice.objects.create(question=q2, text='list = (1,2,3)', is_correct=False)
    
    # Inscrire l'étudiant au cours
    enrollment = Enrollment.objects.create(
        student=student,
        course=course,
        progress=30.0
    )
    
    # Créer un certificat de test
    Certificate.objects.create(
        student=student,
        course=course,
        date_awarded=datetime.now()
    )
    
    print("✅ Données de test créées avec succès!")
    print(f"   Admin: admin / admin123")
    print(f"   Enseignant: teacher1 / teacher123")
    print(f"   Étudiant: student1 / student123")
    print(f"   Cours: {course.title}")

if __name__ == '__main__':
    create_test_data()