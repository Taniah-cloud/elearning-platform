# frontend/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Pages publiques
    path('', views.home, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Pages étudiant
    path('dashboard/', views.dashboard, name='dashboard'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('courses/<int:course_id>/unenroll/', views.unenroll_course, name='unenroll_course'),
    
    # Quiz étudiant
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    # Ajoute cette ligne après les autres URLs de quiz
    path('quiz/<int:quiz_id>/save/', views.save_quiz_progress, name='save_quiz_progress'),

    # URLs pour gérer les quiz (enseignants)
    path('teacher/quizzes/', views.teacher_manage_quizzes, name='teacher_manage_quizzes'),
    path('teacher/quizzes/create/', views.create_quiz_general, name='create_quiz_general'),
    path('teacher/quizzes/<int:quiz_id>/questions/', views.add_questions_to_quiz, name='add_questions_to_quiz'),
    path('teacher/quizzes/question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('teacher/quizzes/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    
    # Certificats
    path('certificate/<str:certificate_id>/', views.view_certificate, name='view_certificate'),
    path('certificate/<str:certificate_id>/download/', views.download_certificate, name='download_certificate'),
    path('verify-certificate/<str:certificate_id>/', views.verify_certificate, name='verify_certificate'),
    
    # Forum
    path('courses/<int:course_id>/forum/', views.course_forum, name='course_forum'),
    path('courses/<int:course_id>/forum/add-message/', views.add_forum_message, name='add_forum_message'),
    
    # Analytics
    path('analytics/', views.progress_analytics, name='progress_analytics'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    
    # Pages enseignant
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/create-quiz/', views.teacher_create_quiz_simple, name='teacher_create_quiz_simple'),
    path('teacher/quizzes/', views.teacher_manage_quizzes, name='teacher_manage_quizzes'),
    
    # Gestion cours
    path('courses/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('courses/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    
    # Pages admin
    path('superadmin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Progress chapters
    path('chapters/<int:chapter_id>/mark-completed/', views.mark_chapter_completed, name='mark_chapter_completed'),
]