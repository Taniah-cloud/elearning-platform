from kivy.uix.screenmanager import Screen
from kivymd.toast import toast
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivy.metrics import dp
from kivy.app import App
from utils.api import api

class QuizListScreen(Screen):
    def on_enter(self):
        self.load_quizzes()
    
    def load_quizzes(self):
        container = self.ids.content_area
        container.clear_widgets()
        
        if api.role != 'student':
            container.add_widget(MDLabel(
                text="Accès réservé aux étudiants",
                halign="center",
                theme_text_color="Error"
            ))
            return
        
        enrollments_res = api.get_my_enrollments()
        if not enrollments_res.get('success'):
            container.add_widget(MDLabel(
                text="Impossible de charger vos inscriptions",
                halign="center"
            ))
            return
        
        enrollments = enrollments_res.get('enrollments', [])
        if not enrollments:
            container.add_widget(MDLabel(
                text="Vous n'êtes inscrit à aucun cours",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(100)
            ))
            return
        
        for enrollment in enrollments:
            course = enrollment.get('course')
            if not course:
                continue
            
            course_title = enrollment.get('course_title', f"Cours #{course}")
            container.add_widget(MDLabel(
                text=f"[b]{course_title}[/b]",
                markup=True,
                font_style="H6",
                size_hint_y=None,
                height=dp(40)
            ))
            
            quizzes = api.get_course_quizzes(course)
            if not quizzes:
                container.add_widget(MDLabel(
                    text="  Aucun quiz pour ce cours",
                    theme_text_color="Hint",
                    size_hint_y=None,
                    height=dp(30)
                ))
                continue
            
            for quiz in quizzes:
                quiz_id = quiz.get('id')
                title = quiz.get('title', 'Sans titre')
                total_q = quiz.get('total_questions', 0)
                
                card = MDCard(
                    orientation="vertical",
                    padding=dp(16),
                    spacing=dp(8),
                    size_hint=(1, None),
                    height=dp(120),
                    md_bg_color=[1,1,1,1]
                )
                card.add_widget(MDLabel(
                    text=title,
                    font_style="Subtitle1",
                    bold=True
                ))
                card.add_widget(MDLabel(
                    text=f"{total_q} question(s)",
                    font_style="Caption",
                    theme_text_color="Hint"
                ))
                btn = MDRaisedButton(
                    text="COMMENCER",
                    size_hint=(0.4, None),
                    height=dp(36),
                    md_bg_color=App.get_running_app().theme_colors['success']
                )
                btn.bind(on_release=lambda x, qid=quiz_id, qtitle=title: self.start_quiz(qid, qtitle))
                card.add_widget(btn)
                container.add_widget(card)
    
    def start_quiz(self, quiz_id, quiz_title):
        screen = self.manager.get_screen('take_quiz')
        screen.quiz_id = quiz_id
        screen.quiz_title = quiz_title
        self.manager.current = 'take_quiz'