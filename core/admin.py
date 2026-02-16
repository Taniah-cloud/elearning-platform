from django.contrib import admin
from .models import (
    User,
    Course,
    Module,
    Chapter,
    Quiz,
    Question,
    Choice,
    Enrollment,
    QuizAttempt,
    ChapterProgress,
    ForumMessage,
    Certificate,
    Notification
)

admin.site.register(User)
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Chapter)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Enrollment)
admin.site.register(QuizAttempt)
admin.site.register(ChapterProgress)
admin.site.register(ForumMessage)
admin.site.register(Certificate)
admin.site.register(Notification)