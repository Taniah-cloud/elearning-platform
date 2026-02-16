from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid

# ---------------------------
# USER
# ---------------------------
class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    def __str__(self):
        return self.username

# ---------------------------
# COURSE
# ---------------------------
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField(blank=True)
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='courses',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def get_total_chapters(self):
        return Chapter.objects.filter(module__course=self).count()
    
    def get_completed_chapters(self, student):
        # À implémenter avec le suivi de progression
        return 0

# ---------------------------
# MODULE
# ---------------------------
class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

# ---------------------------
# CHAPTER
# ---------------------------
class Chapter(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    video_url = models.URLField(blank=True, null=True)
    pdf_file = models.FileField(upload_to='chapter_pdfs/', blank=True, null=True)
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

# ---------------------------
# QUIZ
# ---------------------------
class Quiz(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    passing_score = models.PositiveIntegerField(default=70)  # Score minimum pour réussir
    time_limit = models.PositiveIntegerField(default=30, help_text="Temps en minutes")  # Temps limité
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def get_total_questions(self):
        return self.questions.count()
    
    def get_total_points(self):
        return self.questions.count() * 10  # 10 points par question

# ---------------------------
# QUESTION
# ---------------------------
class Question(models.Model):
    TYPE_CHOICES = (
        ('mcq', 'Multiple Choice'),
        ('truefalse', 'True/False'),
        ('short', 'Short Answer'),
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='mcq')
    points = models.PositiveIntegerField(default=10)
    explanation = models.TextField(blank=True, help_text="Explication après réponse")
    
    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.text[:50]

# ---------------------------
# CHOICE
# ---------------------------
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', null=True, blank=True)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.text

# ---------------------------
# ENROLLMENT
# ---------------------------
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', null=True, blank=True)
    progress = models.FloatField(default=0.0)
    completed_chapters = models.PositiveIntegerField(default=0)
    total_chapters = models.PositiveIntegerField(default=0)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-enrolled_at']

    def __str__(self):
        student_name = self.student.username if self.student else "Unknown"
        course_name = self.course.title if self.course else "Unknown"
        return f"{student_name} -> {course_name}"
    
    def update_progress(self):
        if self.total_chapters > 0:
            self.progress = (self.completed_chapters / self.total_chapters) * 100
        else:
            self.progress = 0
        
        if self.progress >= 100:
            self.completed_at = timezone.now()
        self.save()

# ---------------------------
# QUIZ ATTEMPT
# ---------------------------
class QuizAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.FloatField(default=0)
    max_score = models.FloatField(default=0)
    percentage = models.FloatField(default=0)
    passed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_taken = models.PositiveIntegerField(default=0, help_text="Temps en secondes")
    
    class Meta:
        ordering = ['-started_at']
        unique_together = ('student', 'quiz')

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}: {self.percentage}%"
    
    def calculate_score(self, answers):
        """Calcule le score à partir des réponses"""
        total_points = 0
        earned_points = 0
        
        for question_id, choice_ids in answers.items():
            try:
                question = Question.objects.get(id=question_id)
                total_points += question.points
                
                correct_choices = Choice.objects.filter(
                    question=question, 
                    is_correct=True
                ).values_list('id', flat=True)
                
                # Convertir les choix de l'étudiant en set d'IDs
                student_choices = set(map(int, choice_ids))
                correct_choices_set = set(correct_choices)
                
                # Pour MCQ, toutes les bonnes réponses doivent être sélectionnées
                if student_choices == correct_choices_set:
                    earned_points += question.points
            except Question.DoesNotExist:
                continue
        
        self.score = earned_points
        self.max_score = total_points
        self.percentage = (earned_points / total_points * 100) if total_points > 0 else 0
        self.passed = self.percentage >= self.quiz.passing_score
        self.completed_at = timezone.now()
        self.save()
        
        return self.percentage

# ---------------------------
# CHAPTER PROGRESS
# ---------------------------
class ChapterProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chapter_progress')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='progress')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.PositiveIntegerField(default=0, help_text="Temps en secondes")
    
    class Meta:
        unique_together = ('student', 'chapter')

    def __str__(self):
        status = "✓" if self.completed else "✗"
        return f"{self.student.username} - {self.chapter.title} [{status}]"

# ---------------------------
# FORUM MESSAGE
# ---------------------------
class ForumMessage(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='forum_messages', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['created_at']

    def __str__(self):
        username = self.user.username if self.user else "Unknown"
        return f"{username}: {self.message[:20]}"

# ---------------------------
# CERTIFICATE
# ---------------------------
class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name='certificates')
    certificate_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=True)
    download_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-issued_at']

    def __str__(self):
        student_name = self.student.username if self.student else "Unknown"
        course_name = self.course.title if self.course else "Unknown"
        return f"Certificat: {student_name} - {course_name}"
    
    def increment_download(self):
        self.download_count += 1
        self.save()

# ---------------------------
# NOTIFICATION
# ---------------------------
class Notification(models.Model):
    TYPE_CHOICES = (
        ('new_course', 'Nouveau cours'),
        ('quiz_graded', 'Quiz noté'),
        ('certificate', 'Certificat disponible'),
        ('forum_reply', 'Réponse forum'),
        ('deadline', 'Date limite'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.title}"