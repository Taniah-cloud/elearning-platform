from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'courses', CourseViewSet)
router.register(r'modules', ModuleViewSet)
router.register(r'chapters', ChapterViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'choices', ChoiceViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'forum', ForumMessageViewSet, basename='forum')
router.register(r'certificates', CertificateViewSet, basename='certificate')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('dashboard/', dashboard, name='dashboard'),
    path('progress-chart/', progress_chart, name='progress_chart'),
    
    # Endpoints spécifiques
    path('courses/<int:pk>/enroll/', CourseViewSet.as_view({'post': 'enroll'}), name='course_enroll'),
    path('courses/<int:pk>/unenroll/', CourseViewSet.as_view({'post': 'unenroll'}), name='course_unenroll'),
    path('courses/<int:pk>/forum/', CourseViewSet.as_view({'get': 'forum'}), name='course_forum'),
    path('quizzes/<int:pk>/take/', QuizViewSet.as_view({'get': 'take'}), name='quiz_take'),
    path('quizzes/<int:pk>/submit/', QuizViewSet.as_view({'post': 'submit'}), name='quiz_submit'),
    path('certificates/<int:pk>/download/', CertificateViewSet.as_view({'get': 'download'}), name='certificate_download'),
    path('certificates/verify/', CertificateViewSet.as_view({'get': 'verify'}), name='certificate_verify'),
    path('teacher/create-quiz/', teacher_create_quiz, name='teacher_create_quiz'),
    path('teacher/quizzes/', teacher_manage_quizzes, name='teacher_manage_quizzes'),

]