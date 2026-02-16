from kivy.uix.screenmanager import Screen
from kivymd.toast import toast
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock
from utils.api import api

class TakeQuizScreen(Screen):
    quiz_id = None
    quiz_title = ""
    questions = []
    answers = {}
    time_left = 0
    timer_event = None
    
    def on_enter(self):
        if not self.quiz_id:
            toast("Erreur: aucun quiz sélectionné")
            self.manager.current = 'quiz_list'
            return
        
        self.ids.quiz_title_label.text = self.quiz_title
        self.load_questions()
    
    def on_leave(self):
        if self.timer_event:
            self.timer_event.cancel()
    
    def load_questions(self):
        container = self.ids.questions_container
        container.clear_widgets()
        self.answers.clear()
        
        questions = api.get_quiz_questions(self.quiz_id)
        if not questions:
            container.add_widget(MDLabel(
                text="Aucune question disponible",
                halign="center",
                theme_text_color="Error"
            ))
            return
        
        self.questions = questions
        self.time_left = 30 * 60
        self.update_timer()
        self.timer_event = Clock.schedule_interval(self.update_timer, 1.0)
        
        colors = App.get_running_app().theme_colors
        
        for idx, q in enumerate(questions, 1):
            qid = q['id']
            text = q['text']
            points = q.get('points', 10)
            choices = q.get('choices', [])
            
            card = MDCard(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(12),
                size_hint=(1, None),
                height=dp(200 + len(choices)*30),
                md_bg_color=[1,1,1,1]
            )
            
            header = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(30)
            )
            header.add_widget(MDLabel(
                text=f"Question {idx}",
                font_style="Subtitle1",
                bold=True,
                size_hint_x=0.7
            ))
            header.add_widget(MDLabel(
                text=f"{points} pts",
                halign="right",
                theme_text_color="Secondary",
                size_hint_x=0.3
            ))
            card.add_widget(header)
            
            card.add_widget(MDLabel(
                text=text,
                size_hint_y=None,
                height=dp(50)
            ))
            
            for choice in choices:
                choice_id = choice['id']
                choice_text = choice['text']
                
                row = MDBoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=dp(40)
                )
                cb = MDCheckbox(size_hint_x=0.1)
                cb.bind(active=lambda inst, val, qid=qid, cid=choice_id: self.on_checkbox_active(qid, cid, val))
                row.add_widget(cb)
                row.add_widget(MDLabel(
                    text=choice_text,
                    size_hint_x=0.9
                ))
                card.add_widget(row)
            
            container.add_widget(card)
        
        container.add_widget(MDRaisedButton(
            text="SOUMETTRE",
            size_hint=(0.8, None),
            height=dp(48),
            pos_hint={"center_x": 0.5},
            md_bg_color=colors['success'],
            on_release=lambda x: self.submit_quiz()
        ))
    
    def on_checkbox_active(self, question_id, choice_id, active):
        if question_id not in self.answers:
            self.answers[question_id] = []
        if active:
            if choice_id not in self.answers[question_id]:
                self.answers[question_id].append(choice_id)
        else:
            if choice_id in self.answers[question_id]:
                self.answers[question_id].remove(choice_id)
    
    def update_timer(self, *args):
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.ids.timer_label.text = f"{minutes:02d}:{seconds:02d}"
        if self.time_left <= 0:
            self.timer_event.cancel()
            toast("⏰ Temps écoulé !")
            self.submit_quiz()
        self.time_left -= 1
    
    def submit_quiz(self):
        if not self.answers:
            toast("Vous n'avez répondu à aucune question")
            return
        
        submit_btn = self.ids.submit_btn
        submit_btn.disabled = True
        submit_btn.text = "SOUMISSION..."
        
        time_spent = 30*60 - self.time_left
        res = api.submit_quiz(self.quiz_id, self.answers, time_spent)
        
        if res.get('success'):
            screen = self.manager.get_screen('quiz_results')
            screen.set_results(res)
            self.manager.current = 'quiz_results'
        else:
            toast(f"❌ Erreur: {res.get('error', 'Inconnue')}")
            submit_btn.disabled = False
            submit_btn.text = "SOUMETTRE LE QUIZ"