from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password

# ================= USER =================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name', 'date_joined']
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# ================= COURSE =================
class CourseSerializer(serializers.ModelSerializer):
    teacher = serializers.SlugRelatedField(
        slug_field="username",
        queryset=User.objects.filter(role="teacher"),
        required=False
    )
    total_chapters = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_chapters(self, obj):
        return obj.get_total_chapters()

# ================= MODULE =================
class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = "__all__"

# ================= CHAPTER =================
class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = "__all__"

# ================= CHOICE =================
class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']

# ================= QUESTION =================
class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'points', 'explanation', 'choices']
        read_only_fields = ['choices']

# ================= QUIZ =================
class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    total_questions = serializers.SerializerMethodField()
    total_points = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = "__all__"
    
    def get_total_questions(self, obj):
        return obj.get_total_questions()
    
    def get_total_points(self, obj):
        return obj.get_total_points()

# ================= QUIZ ATTEMPT =================
class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    student_name = serializers.CharField(source='student.username', read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = "__all__"
        read_only_fields = ['started_at', 'completed_at']

# ================= QUIZ SUBMISSION =================
class QuizSubmissionSerializer(serializers.Serializer):
    answers = serializers.DictField(
        child=serializers.ListField(child=serializers.IntegerField()),
        help_text="Format: {'question_id': [choice_id1, choice_id2]}"
    )
    time_taken = serializers.IntegerField(min_value=0)

# ================= ENROLLMENT =================
class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    student_name = serializers.CharField(source='student.username', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = "__all__"

# ================= CHAPTER PROGRESS =================
class ChapterProgressSerializer(serializers.ModelSerializer):
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)
    
    class Meta:
        model = ChapterProgress
        fields = "__all__"

# ================= FORUM =================
class ForumMessageSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = ForumMessage
        fields = "__all__"
        read_only_fields = ['created_at']
    
    def get_replies(self, obj):
        replies = ForumMessage.objects.filter(parent=obj).order_by('created_at')
        return ForumMessageSerializer(replies, many=True).data

# ================= CERTIFICATE =================
class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Certificate
        fields = "__all__"
        read_only_fields = ['certificate_id', 'issued_at']

# ================= DASHBOARD STATS =================
class DashboardStatsSerializer(serializers.Serializer):
    total_courses = serializers.IntegerField()
    enrolled_courses = serializers.IntegerField()
    completed_courses = serializers.IntegerField()
    average_score = serializers.FloatField()
    total_quizzes = serializers.IntegerField()
    passed_quizzes = serializers.IntegerField()
    recent_certificates = CertificateSerializer(many=True)
    progress_by_course = serializers.DictField()

# ================= NOTIFICATION =================
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"