from kivy.uix.screenmanager import Screen
from kivy.logger import Logger
from utils.api import api
from kivy.app import App
from kivy.clock import mainthread
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from kivymd.toast import toast

class HomeScreen(Screen):
    def on_enter(self, *args):
        print(f"\n=== ACCUEIL ===")
        print(f"Utilisateur: {api.username}")
        print(f"Rôle: {api.role}")
        
        self.update_add_button()
        self.refresh_dashboard()
    
    def update_add_button(self):
        if hasattr(self.ids, 'add_course_btn'):
            is_admin_or_teacher = api.role in ["admin", "teacher"]
            print(f"Bouton Ajouter: visible={is_admin_or_teacher}")
            self.ids.add_course_btn.opacity = 1 if is_admin_or_teacher else 0
            self.ids.add_course_btn.disabled = not is_admin_or_teacher
    
    def refresh_dashboard(self):
        try:
            data = api.get_dashboard() or {}
            self.ids.courses_label.text = str(data.get("courses", 0))
            self.ids.stats_label.text = str(data.get("stats", 0))
        except Exception as e:
            Logger.error(f"Erreur dashboard: {e}")
        
        try:
            courses = api.get_courses() or []
            self.populate_courses(courses)
        except Exception as e:
            Logger.error(f"Erreur cours: {e}")
    
    @mainthread
    def populate_courses(self, courses):
        container = self.ids.courses_container
        container.clear_widgets()
        
        if not courses:
            empty_label = MDLabel(
                text="Aucun cours disponible",
                halign="center",
                size_hint_y=None,
                height=dp(100),
                theme_text_color="Secondary",
                font_style="H6"
            )
            container.add_widget(empty_label)
            return
        
        app = App.get_running_app()
        theme_colors = getattr(app, 'theme_colors', {})
        
        primary_color = theme_colors.get('primary', [0.17, 0.24, 0.31, 1])
        success_color = theme_colors.get('success', [0.15, 0.68, 0.38, 1])
        danger_color = theme_colors.get('danger', [0.91, 0.3, 0.24, 1])
        warning_color = theme_colors.get('warning', [0.95, 0.61, 0.07, 1])
        
        enrolled_courses = []
        if api.role == "student":
            enrollments_res = api.get_my_enrollments()
            if enrollments_res.get("success"):
                enrolled_courses = [e.get("course") for e in enrollments_res.get("enrollments", [])]
        
        for c in courses:
            title = c.get("title", "Sans titre")
            desc = c.get("description", "") or ""
            course_id = c.get("id")
            teacher = c.get("teacher", "Inconnu")
            is_enrolled = course_id in enrolled_courses
            
            card = MDCard(
                orientation="vertical",
                size_hint=(1, None),
                height=dp(200),
                padding=0,
                md_bg_color=[1, 1, 1, 1]
            )
            
            header_box = MDBoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(60),
                md_bg_color=primary_color,
                padding=dp(16)
            )
            
            header_label = MDLabel(
                text=title,
                font_style="H6",
                theme_text_color="Custom",
                text_color=[1, 1, 1, 1],
                bold=True,
                size_hint_y=None,
                height=dp(30)
            )
            header_box.add_widget(header_label)
            card.add_widget(header_box)
            
            body_box = MDBoxLayout(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(10)
            )
            
            desc_short = desc[:100] + ("..." if len(desc) > 100 else "")
            desc_label = MDLabel(
                text=desc_short,
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(50),
                line_height=1.4
            )
            body_box.add_widget(desc_label)
            
            teacher_label = MDLabel(
                text=f"Enseignant: {teacher}",
                font_style="Caption",
                theme_text_color="Hint",
                size_hint_y=None,
                height=dp(20)
            )
            body_box.add_widget(teacher_label)
            
            btn_box = MDBoxLayout(
                size_hint_y=None,
                height=dp(40),
                spacing=dp(10),
                padding=[0, dp(5), 0, 0]
            )
            
            user_role = api.role
            
            if user_role in ["admin", "teacher"]:
                edit_btn = MDRaisedButton(
                    text="Éditer",
                    size_hint_x=0.5,
                    elevation=0,
                    md_bg_color=primary_color
                )
                edit_btn.bind(on_release=lambda x, cid=course_id: self.edit_course(cid))
                
                delete_btn = MDRaisedButton(
                    text="Supprimer",
                    size_hint_x=0.5,
                    md_bg_color=danger_color
                )
                delete_btn.bind(on_release=lambda x, cid=course_id: self.delete_course(cid))
                
                btn_box.add_widget(edit_btn)
                btn_box.add_widget(delete_btn)
                
            elif user_role == "student":
                if is_enrolled:
                    enrolled_btn = MDRaisedButton(
                        text="Déjà inscrit",
                        size_hint_x=0.5,
                        elevation=0,
                        md_bg_color=success_color,
                        disabled=True
                    )
                    
                    unenroll_btn = MDRaisedButton(
                        text="Se désinscrire",
                        size_hint_x=0.5,
                        elevation=0,
                        md_bg_color=warning_color
                    )
                    unenroll_btn.bind(on_release=lambda x, cid=course_id: self.unenroll_course(cid))
                    
                    btn_box.add_widget(enrolled_btn)
                    btn_box.add_widget(unenroll_btn)
                else:
                    enroll_btn = MDRaisedButton(
                        text="S'inscrire",
                        size_hint_x=0.5,
                        elevation=0,
                        md_bg_color=success_color
                    )
                    enroll_btn.bind(on_release=lambda x, cid=course_id: self.enroll_course(cid))
                    
                    details_btn = MDRaisedButton(
                        text="Détails",
                        size_hint_x=0.5,
                        elevation=0,
                        md_bg_color=primary_color
                    )
                    details_btn.bind(on_release=lambda x, cid=course_id: self.show_course_details(cid))
                    
                    btn_box.add_widget(enroll_btn)
                    btn_box.add_widget(details_btn)
            else:
                details_btn = MDRaisedButton(
                    text="Voir détails",
                    size_hint_x=1,
                    elevation=0,
                    md_bg_color=primary_color
                )
                details_btn.bind(on_release=lambda x, cid=course_id: self.show_course_details(cid))
                btn_box.add_widget(details_btn)
            
            body_box.add_widget(btn_box)
            card.add_widget(body_box)
            container.add_widget(card)
    
    def logout(self):
        app = App.get_running_app()
        app.logout()
    
    def add_course(self):
        if api.role in ["admin", "teacher"]:
            self.manager.current = "add_course"
        else:
            toast("Permission refusée")
    
    def edit_course(self, course_id):
        if api.role in ["admin", "teacher"]:
            screen = self.manager.get_screen("edit_course")
            screen.set_course(course_id)
            self.manager.current = "edit_course"
        else:
            toast("Permission refusée")
    
    def show_course_details(self, course_id):
        course = api.get_course(course_id)
        if course:
            title = course.get("title", "Sans titre")
            description = course.get("description", "")
            teacher = course.get("teacher", "Inconnu")
            
            dialog = MDDialog(
                title=title,
                text=f"Enseignant: {teacher}\n\n{description}",
                size_hint=(0.8, 0.6),
                buttons=[
                    MDFlatButton(
                        text="FERMER",
                        theme_text_color="Primary",
                        on_release=lambda x: dialog.dismiss()
                    ),
                ],
            )
            dialog.open()
        else:
            toast("Impossible de charger les détails du cours")
    
    def enroll_course(self, course_id):
        if api.role != "student":
            toast("Seuls les étudiants peuvent s'inscrire")
            return
        
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._process_enroll(course_id), 0.1)
    
    def _process_enroll(self, course_id):
        res = api.enroll_to_course(course_id)
        if res.get("success"):
            toast("Inscription réussie !")
            self.refresh_dashboard()
        else:
            error = res.get("error", "Erreur d'inscription")
            toast(f"Erreur: {error}")
    
    def unenroll_course(self, course_id):
        if api.role != "student":
            toast("Seuls les étudiants peuvent se désinscrire")
            return
        
        app = App.get_running_app()
        theme_colors = getattr(app, 'theme_colors', {})
        warning_color = theme_colors.get('warning', [0.95, 0.61, 0.07, 1])
        
        def confirm_unenroll(instance):
            res = api.unenroll_from_course(course_id)
            if res.get("success"):
                toast("Désinscription réussie")
                self.refresh_dashboard()
            else:
                error = res.get("error", "Erreur de désinscription")
                toast(f"Erreur: {error}")
            dialog.dismiss()
        
        dialog = MDDialog(
            title="Confirmer la désinscription",
            text="Êtes-vous sûr de vouloir vous désinscrire de ce cours ?",
            buttons=[
                MDFlatButton(
                    text="ANNULER",
                    theme_text_color="Primary",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="SE DÉSINSCRIRE",
                    elevation=0,
                    md_bg_color=warning_color,
                    on_release=confirm_unenroll
                ),
            ],
        )
        dialog.open()
    
    def delete_course(self, course_id):
        if api.role not in ["admin", "teacher"]:
            toast("Permission refusée")
            return
        
        app = App.get_running_app()
        theme_colors = getattr(app, 'theme_colors', {})
        danger_color = theme_colors.get('danger', [0.91, 0.3, 0.24, 1])
        
        def confirm_delete(instance):
            res = api.delete_course(course_id)
            if res.get("success"):
                toast("Cours supprimé")
                self.refresh_dashboard()
            else:
                toast(f"{res.get('error', 'Erreur')}")
            dialog.dismiss()
        
        dialog = MDDialog(
            title="Confirmer la suppression",
            text="Êtes-vous sûr de vouloir supprimer ce cours ?",
            buttons=[
                MDFlatButton(
                    text="ANNULER",
                    theme_text_color="Primary",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="SUPPRIMER",
                    elevation=0,
                    md_bg_color=danger_color,
                    on_release=confirm_delete
                ),
            ],
        )
        dialog.open()
    
    def open_quiz_list(self):
        if api.role == 'student':
            self.manager.current = 'quiz_list'
        else:
            toast('Réservé aux étudiants')