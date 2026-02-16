from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg, Q
from django.http import HttpResponse
from django.template.loader import render_to_string
# Version garantie sans erreur :
import sys

# DÉSACTIVER WEAZYPRINT COMPLÈTEMENT POUR WINDOWS
# La classe HTML factice empêche l'import de WeasyPrint
class HTML:
    @staticmethod
    def write_pdf(*args, **kwargs):
        raise ImportError("WeasyPrint désactivé. Utilisez frontend/views.py pour ReportLab")

HAS_WEASYPRINT = False

import json
import os
from .models import *
from .serializers import *
from .permissions import IsTeacherOrReadOnly, IsOwnerOrReadOnly

from .models import *
from .serializers import *
from .permissions import IsTeacherOrReadOnly, IsOwnerOrReadOnly
# ---------------------------
# LOGIN TOKEN
# ---------------------------
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'role': user.role,
            'email': user.email
        })

# ---------------------------
# USERS
# ---------------------------
class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == 'admin':
            return User.objects.all()
        else:
            return User.objects.filter(id=user.id)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]

# ---------------------------
# COURSES
# ---------------------------
class CourseViewSet(ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'enroll', 'unenroll', 'forum']:
            return [IsAuthenticated()]
        return [IsTeacherOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        course = self.get_object()
        student = request.user
        
        if student.role != 'student':
            return Response({"error": "Seuls les étudiants peuvent s'inscrire"}, status=400)
        
        enrollment, created = Enrollment.objects.get_or_create(
            student=student,
            course=course,
            defaults={
                'total_chapters': course.get_total_chapters()
            }
        )
        
        if created:
            # Créer une notification
            Notification.objects.create(
                user=course.teacher,
                notification_type='new_course',
                title=f"Nouvel étudiant inscrit",
                message=f"{student.username} s'est inscrit à votre cours '{course.title}'"
            )
            
            return Response({"success": "Inscription réussie"}, status=201)
        else:
            return Response({"error": "Déjà inscrit"}, status=400)

    @action(detail=True, methods=['post'])
    def unenroll(self, request, pk=None):
        course = self.get_object()
        student = request.user
        
        try:
            enrollment = Enrollment.objects.get(student=student, course=course)
            enrollment.delete()
            return Response({"success": "Désinscription réussie"})
        except Enrollment.DoesNotExist:
            return Response({"error": "Non inscrit"}, status=400)

    @action(detail=True, methods=['get'])
    def forum(self, request, pk=None):
        course = self.get_object()
        messages = ForumMessage.objects.filter(course=course, parent=None).order_by('-created_at')
        serializer = ForumMessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_forum_message(self, request, pk=None):
        course = self.get_object()
        serializer = ForumMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, course=course)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def quizzes(self, request, pk=None):
        """Récupère tous les quiz d'un cours (pour l'app mobile)"""
        course = self.get_object()
        quizzes = Quiz.objects.filter(chapter__module__course=course)
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)
# ---------------------------
# QUIZZES
# ---------------------------
class QuizViewSet(ModelViewSet):
    serializer_class = QuizSerializer
    queryset = Quiz.objects.all()
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'take', 'submit']:
            return [IsAuthenticated()]
        return [IsTeacherOrReadOnly()]

    @action(detail=True, methods=['get'])
    def take(self, request, pk=None):
        quiz = self.get_object()
        
        # Vérifier si l'étudiant est inscrit au cours
        if quiz.chapter:
            course = quiz.chapter.module.course
            if not Enrollment.objects.filter(student=request.user, course=course).exists():
                return Response({"error": "Vous devez être inscrit au cours"}, status=403)
        
        # Vérifier les tentatives précédentes
        if request.user.role == 'student':
            attempt = QuizAttempt.objects.filter(
                student=request.user,
                quiz=quiz
            ).first()
            
            if attempt and attempt.completed_at:
                return Response({
                    "error": "Vous avez déjà complété ce quiz",
                    "previous_score": attempt.percentage
                }, status=400)
        
        # Sérialiser le quiz avec questions et choix
        serializer = self.get_serializer(quiz)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        quiz = self.get_object()
        student = request.user
        
        if student.role != 'student':
            return Response({"error": "Seuls les étudiants peuvent soumettre des quiz"}, status=403)
        
        # Vérifier si déjà complété
        attempt = QuizAttempt.objects.filter(student=student, quiz=quiz).first()
        if attempt and attempt.completed_at:
            return Response({"error": "Quiz déjà complété"}, status=400)
        
        # Créer ou récupérer la tentative
        if not attempt:
            attempt = QuizAttempt.objects.create(
                student=student,
                quiz=quiz
            )
        
        # Calculer le score
        submission_serializer = QuizSubmissionSerializer(data=request.data)
        if submission_serializer.is_valid():
            time_taken = submission_serializer.validated_data['time_taken']
            answers = submission_serializer.validated_data['answers']
            
            percentage = attempt.calculate_score(answers)
            attempt.time_taken = time_taken
            attempt.save()
            
            # Vérifier si un certificat doit être généré
            if quiz.chapter and percentage >= quiz.passing_score:
                course = quiz.chapter.module.course
                enrollment = Enrollment.objects.get(student=student, course=course)
                enrollment.completed_chapters += 1
                enrollment.update_progress()
                
                # Vérifier si le cours est complété pour le certificat
                if enrollment.progress >= 100:
                    Certificate.objects.get_or_create(
                        student=student,
                        course=course
                    )
            
            return Response({
                "success": True,
                "score": attempt.score,
                "max_score": attempt.max_score,
                "percentage": attempt.percentage,
                "passed": attempt.passed,
                "time_taken": attempt.time_taken
            })
        
        return Response(submission_serializer.errors, status=400)

# ---------------------------
# CERTIFICATES
# ---------------------------
class CertificateViewSet(ModelViewSet):
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Certificate.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Certificate.objects.filter(student=user)
        elif user.role == 'teacher':
            return Certificate.objects.filter(course__teacher=user)
        else:
            return Certificate.objects.all()

    # Dans views.py, trouve cette fonction (~ ligne 250)
@action(detail=True, methods=['get'])
def download(self, request, pk=None):
    certificate = self.get_object()
    
    # Vérifier les permissions
    if request.user != certificate.student and request.user.role not in ['teacher', 'admin']:
        return Response({"error": "Permission refusée"}, status=403)
    
    # Incrémenter le compteur de téléchargement
    certificate.increment_download()
    
    # Retourner les infos du certificat (sans PDF)
    return Response({
        "success": True,
        "message": "Certificat disponible - PDF désactivé sur ce système",
        "certificate": {
            "id": certificate.id,
            "certificate_id": str(certificate.certificate_id),
            "student": certificate.student.username,
            "course": certificate.course.title,
            "issued_at": certificate.issued_at,
            "download_count": certificate.download_count
        },
        "html_url": f"/certificate/{certificate.certificate_id}/",
        "note": "Pour générer des PDFs, installer GTK sur Windows ou utiliser Linux/Mac"
    })

    @action(detail=False, methods=['get'])
    def verify(self, request):
        certificate_id = request.query_params.get('id')
        if not certificate_id:
            return Response({"error": "ID de certificat requis"}, status=400)
        
        try:
            certificate = Certificate.objects.get(certificate_id=certificate_id)
            return Response({
                "valid": certificate.verified,
                "student": certificate.student.username,
                "course": certificate.course.title,
                "issued_at": certificate.issued_at,
                "download_count": certificate.download_count
            })
        except Certificate.DoesNotExist:
            return Response({"valid": False, "error": "Certificat non trouvé"}, status=404)

# ---------------------------
# DASHBOARD & STATS
# ---------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    user = request.user
    
    if user.role == 'student':
        # Stats pour étudiant
        enrollments = Enrollment.objects.filter(student=user)
        total_courses = enrollments.count()
        completed_courses = enrollments.filter(progress=100).count()
        
        attempts = QuizAttempt.objects.filter(student=user)
        total_quizzes = attempts.count()
        passed_quizzes = attempts.filter(passed=True).count()
        average_score = attempts.aggregate(Avg('percentage'))['percentage__avg'] or 0
        
        recent_certificates = Certificate.objects.filter(student=user).order_by('-issued_at')[:5]
        
        progress_by_course = {}
        for enrollment in enrollments:
            progress_by_course[enrollment.course.title] = enrollment.progress
        
        data = {
            "total_courses": total_courses,
            "enrolled_courses": total_courses,  # Même chose dans ce contexte
            "completed_courses": completed_courses,
            "average_score": round(average_score, 1),
            "total_quizzes": total_quizzes,
            "passed_quizzes": passed_quizzes,
            "recent_certificates": CertificateSerializer(recent_certificates, many=True).data,
            "progress_by_course": progress_by_course
        }
        
    elif user.role == 'teacher':
        # Stats pour enseignant
        courses = Course.objects.filter(teacher=user)
        total_courses = courses.count()
        
        total_students = Enrollment.objects.filter(course__teacher=user).values('student').distinct().count()
        
        certificates = Certificate.objects.filter(course__teacher=user)
        total_certificates = certificates.count()
        
        forum_messages = ForumMessage.objects.filter(course__teacher=user).count()
        
        data = {
            "total_courses": total_courses,
            "total_students": total_students,
            "total_certificates": total_certificates,
            "forum_messages": forum_messages,
            "courses": CourseSerializer(courses, many=True).data[:10]
        }
        
    else:  # admin
        # Stats pour admin
        total_users = User.objects.count()
        total_courses = Course.objects.count()
        total_enrollments = Enrollment.objects.count()
        total_certificates = Certificate.objects.count()
        
        data = {
            "total_users": total_users,
            "total_courses": total_courses,
            "total_enrollments": total_enrollments,
            "total_certificates": total_certificates,
            "users_by_role": {
                "students": User.objects.filter(role='student').count(),
                "teachers": User.objects.filter(role='teacher').count(),
                "admins": User.objects.filter(role='admin').count()
            }
        }
    
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def progress_chart(request):
    user = request.user
    
    if user.role == 'student':
        enrollments = Enrollment.objects.filter(student=user)
        labels = [e.course.title for e in enrollments]
        progress = [e.progress for e in enrollments]
        
        data = {
            "labels": labels,
            "datasets": [{
                "label": "Progression (%)",
                "data": progress,
                "backgroundColor": "rgba(54, 162, 235, 0.5)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 1
            }]
        }
        
        return Response(data)
    
    return Response({"error": "Non disponible"}, status=403)

# ---------------------------
# VIEWSETS DE BASE
# ---------------------------
class ModuleViewSet(ModelViewSet):
    serializer_class = ModuleSerializer
    queryset = Module.objects.all()
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]

class ChapterViewSet(ModelViewSet):
    serializer_class = ChapterSerializer
    queryset = Chapter.objects.all()
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]

class QuestionViewSet(ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]

class ChoiceViewSet(ModelViewSet):
    serializer_class = ChoiceSerializer
    queryset = Choice.objects.all()
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]

class EnrollmentViewSet(ModelViewSet):
    serializer_class = EnrollmentSerializer
    queryset = Enrollment.objects.all()
    permission_classes = [IsAuthenticated]

class ForumMessageViewSet(ModelViewSet):
    serializer_class = ForumMessageSerializer
    queryset = ForumMessage.objects.all()
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class NotificationViewSet(ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        return Response({"success": True})
    
# ---------------------------
# VUES POUR TEACHER (Création de quiz)
# ---------------------------
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def teacher_create_quiz(request):
    """Vue pour créer un quiz simple"""
    if request.method == 'POST':
        # Récupère les données
        course_id = request.POST.get('course_id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        if course_id and title:
            try:
                # Trouve le cours
                course = Course.objects.get(id=course_id)
                # Trouve un chapitre du cours
                chapter = Chapter.objects.filter(module__course=course).first()
                
                if chapter:
                    # Crée le quiz
                    quiz = Quiz.objects.create(
                        title=title,
                        description=description,
                        chapter=chapter,
                        passing_score=60,
                        time_limit=15
                    )
                    
                    # Ajoute une question par défaut
                    question = Question.objects.create(
                        quiz=quiz,
                        text="Question exemple - Modifiez-moi via l'admin",
                        question_type='truefalse',
                        points=10
                    )
                    
                    Choice.objects.create(question=question, text="Vrai", is_correct=True)
                    Choice.objects.create(question=question, text="Faux", is_correct=False)
                    
                    messages.success(request, f'Quiz "{title}" créé avec succès!')
                    return redirect('teacher_dashboard')
                else:
                    messages.error(request, 'Ce cours n\'a pas de chapitres')
            except Course.DoesNotExist:
                messages.error(request, 'Cours non trouvé')
        else:
            messages.error(request, 'Titre et cours requis')
    
    # GET: Affiche le formulaire
    # Récupère les cours où l'utilisateur est teacher
    teacher_courses = Course.objects.filter(teacher=request.user)
    return redirect('teacher_create_quiz_simple') 

@login_required
def teacher_manage_quizzes(request):
    """Vue pour voir tous les quizzes du teacher"""
    # Récupère les cours du teacher
    teacher_courses = Course.objects.filter(teacher=request.user)
    
    # Récupère tous les quizzes de ces cours
    quizzes = Quiz.objects.filter(chapter__module__course__in=teacher_courses)
    
    return render(request, 'teacher/manage_quizzes.html', {
        'quizzes': quizzes,
        'teacher_courses': teacher_courses
    })