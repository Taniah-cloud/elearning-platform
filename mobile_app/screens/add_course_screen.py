from kivy.uix.screenmanager import Screen
from kivymd.toast import toast
from utils.api import api
from kivy.animation import Animation

class AddCourseScreen(Screen):
    def on_pre_enter(self):
        self.ids.title.text = ""
        self.ids.description.text = ""
        
        if hasattr(self, 'ids'):
            self.opacity = 0
            anim = Animation(opacity=1, duration=0.3)
            anim.start(self)
    
    def add_course(self):
        title = self.ids.title.text.strip()
        description = self.ids.description.text.strip()
        
        if not title:
            toast("Le titre est requis !")
            anim = Animation(x=self.ids.title.x + 5, duration=0.05) + \
                   Animation(x=self.ids.title.x - 5, duration=0.05) + \
                   Animation(x=self.ids.title.x, duration=0.05)
            anim.start(self.ids.title)
            return
        
        btn = self.ids.create_btn
        original_text = btn.text
        btn.text = "Création..."
        btn.disabled = True
        
        res = api.add_course(title, description)
        
        btn.text = original_text
        btn.disabled = False
        
        if res.get("success"):
            toast("Cours créé avec succès !")
            self.manager.get_screen("home").refresh_dashboard()
            self.manager.current = "home"
        else:
            toast(res.get("error", "Erreur création cours"))