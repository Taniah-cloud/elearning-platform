from kivy.uix.screenmanager import Screen
from kivymd.toast import toast
from utils.api import api

class EditCourseScreen(Screen):
    current_course_id = None
    
    def set_course(self, course_id):
        self.current_course_id = course_id
        course = api.get_course(course_id)
        self.ids.title.text = course.get("title", "")
        self.ids.description.text = course.get("description", "")
    
    def save_course(self):
        if not self.current_course_id:
            toast("Erreur : aucun cours sélectionné")
            return
        
        title = self.ids.title.text.strip()
        description = self.ids.description.text.strip()
        
        if not title:
            toast("Le titre est requis !")
            return
        
        btn = self.ids.save_btn
        original_text = btn.text
        btn.text = "Enregistrement..."
        btn.disabled = True
        
        res = api.update_course(self.current_course_id, title, description)
        
        btn.text = original_text
        btn.disabled = False
        
        if res.get("success"):
            toast("Cours mis à jour !")
            self.manager.get_screen("home").refresh_dashboard()
            self.manager.current = "home"
        else:
            toast(res.get("error", "Erreur mise à jour"))