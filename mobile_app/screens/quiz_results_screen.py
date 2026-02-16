from kivy.uix.screenmanager import Screen
from kivy.app import App

class QuizResultsScreen(Screen):
    def set_results(self, data):
        score = data.get('score', 0)
        max_score = data.get('max_score', 0)
        percentage = data.get('percentage', 0)
        passed = data.get('passed', False)
        
        self.ids.score_label.text = f"{int(percentage)}%"
        self.ids.details_label.text = f"Score: {score}/{max_score}"
        
        if passed:
            self.ids.status_label.text = "✅ Réussi !"
            self.ids.status_label.text_color = App.get_running_app().theme_colors['success']
            self.ids.result_icon.text = "🎓"
        else:
            self.ids.status_label.text = "❌ Échec"
            self.ids.status_label.text_color = App.get_running_app().theme_colors['danger']
            self.ids.result_icon.text = "📝"