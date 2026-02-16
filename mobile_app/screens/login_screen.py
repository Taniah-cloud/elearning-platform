from kivy.uix.screenmanager import Screen
from kivymd.toast import toast
from kivy.app import App

class LoginScreen(Screen):
    def login_user(self):
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()
        if not username or not password:
            toast("Remplis tous les champs !")
            return
        app = App.get_running_app()
        app.login_user(username, password)