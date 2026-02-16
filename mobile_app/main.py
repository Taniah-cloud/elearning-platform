from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from screens.login_screen import LoginScreen
from screens.home_screen import HomeScreen
from screens.add_course_screen import AddCourseScreen
from screens.edit_course_screen import EditCourseScreen
from screens.quiz_list_screen import QuizListScreen
from screens.take_quiz_screen import TakeQuizScreen
from screens.quiz_results_screen import QuizResultsScreen
import os

KV_DIR = os.path.join(os.path.dirname(__file__), "kv")

class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = None
        self.role = None

    def build(self):
        # URL fixe en local
        from utils.api import api
        api.base_url = "http://127.0.0.1:8000/api/"
        print("💻 Mode PC - URL:", api.base_url)
        
        # Charger les couleurs du thème
        from utils.theme import COLORS
        
        def hex_to_rgba(hex_color):
            try:
                hex_color = hex_color.lstrip('#')
                if len(hex_color) != 6:
                    return [0.17, 0.24, 0.31, 1]
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
                return [r, g, b, 1]
            except:
                return [0.17, 0.24, 0.31, 1]
        
        self.theme_colors = {
            'primary': hex_to_rgba(COLORS['primary']),
            'primary_dark': hex_to_rgba(COLORS['primary_dark']),
            'secondary': hex_to_rgba(COLORS['secondary']),
            'success': hex_to_rgba(COLORS['success']),
            'danger': hex_to_rgba(COLORS['danger']),
            'warning': hex_to_rgba(COLORS['warning']),
            'info': hex_to_rgba(COLORS['info']),
            'gray': hex_to_rgba(COLORS['gray']),
            'gray_light': hex_to_rgba(COLORS['gray_light']),
            'background': hex_to_rgba(COLORS['background']),
        }
        
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        # Charger les KV
        Builder.load_file(os.path.join(KV_DIR, "login.kv"))
        Builder.load_file(os.path.join(KV_DIR, "home.kv"))
        Builder.load_file(os.path.join(KV_DIR, "add_course.kv"))
        Builder.load_file(os.path.join(KV_DIR, "edit_course.kv"))
        Builder.load_file(os.path.join(KV_DIR, "quiz_list.kv"))
        Builder.load_file(os.path.join(KV_DIR, "take_quiz.kv"))
        Builder.load_file(os.path.join(KV_DIR, "quiz_results.kv"))
        
        # ScreenManager
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(AddCourseScreen(name="add_course"))
        self.sm.add_widget(EditCourseScreen(name="edit_course"))
        self.sm.add_widget(QuizListScreen(name="quiz_list"))
        self.sm.add_widget(TakeQuizScreen(name="take_quiz"))
        self.sm.add_widget(QuizResultsScreen(name="quiz_results"))
        
        return self.sm
    
    def login_user(self, username, password):
        from utils.api import api
        res = api.login(username, password)
        if res.get("success"):
            from kivymd.toast import toast
            self.username = api.username
            self.role = api.role
            role_fr = {
                "admin": "Administrateur",
                "teacher": "Enseignant",
                "student": "Étudiant"
            }.get(self.role, self.role)
            toast(f"Bienvenue {self.username} ({role_fr}) !")
            self.sm.current = "home"
            # Rafraîchir le dashboard
            self.sm.get_screen("home").refresh_dashboard()
        else:
            from kivymd.toast import toast
            toast("Nom d'utilisateur ou mot de passe incorrect")
    
    def logout(self):
        from utils.api import api
        from kivymd.toast import toast
        toast("Déconnexion réussie")
        api.token = None
        api.username = None
        api.role = None
        self.username = None
        self.role = None
        self.sm.current = "login"

if __name__ == "__main__":
    MainApp().run()