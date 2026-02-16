import requests
from kivy.logger import Logger

class APIClient:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000/api/"
        self.token = None
        self.username = None
        self.role = None
    
    def set_token(self, token):
        self.token = token
    
    def headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        return headers
    
    # ========== AUTH ==========
    def login(self, username, password):
        url = self.base_url + "login/"
        try:
            Logger.info(f"Connexion pour: {username}")
            response = requests.post(url, json={"username": username, "password": password}, timeout=6)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                self.username = data.get("username")
                self.role = data.get("role", "student")
                Logger.info(f"Rôle détecté: {self.role}")
                return {
                    "success": True,
                    "username": self.username,
                    "token": self.token,
                    "role": self.role
                }
            else:
                error_msg = "Nom d'utilisateur ou mot de passe incorrect"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", error_msg)
                except:
                    pass
                Logger.error(f"Erreur connexion: {error_msg}")
                return {"success": False, "error": error_msg}
        except requests.exceptions.RequestException as e:
            Logger.error(f"Erreur réseau: {e}")
            return {"success": False, "error": str(e)}
    
    # ========== DASHBOARD ==========
    def get_dashboard(self):
        url = self.base_url + "dashboard/"
        try:
            response = requests.get(url, headers=self.headers(), timeout=6)
            if response.status_code == 200:
                return response.json()
            return {"courses": 0, "stats": 0}
        except requests.exceptions.RequestException as e:
            Logger.error(f"Erreur dashboard: {e}")
            return {"courses": 0, "stats": 0}
    
    # ========== COURSES ==========
    def get_courses(self):
        url = self.base_url + "courses/"
        try:
            response = requests.get(url, headers=self.headers(), timeout=6)
            if response.status_code == 200:
                return response.json()
            return []
        except requests.exceptions.RequestException as e:
            Logger.error(f"Erreur cours: {e}")
            return []
    
    def get_course(self, course_id):
        url = self.base_url + f"courses/{course_id}/"
        try:
            response = requests.get(url, headers=self.headers())
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            Logger.error(f"Erreur récupération cours: {e}")
            return {}
    
    def add_course(self, title, description):
        url = self.base_url + "courses/"
        try:
            response = requests.post(url, json={"title": title, "description": description}, headers=self.headers())
            if response.status_code in (200, 201):
                return {"success": True}
            return {"success": False, "error": response.text}
        except Exception as e:
            Logger.error(f"Erreur création cours: {e}")
            return {"success": False, "error": str(e)}
    
    def update_course(self, course_id, title, description):
        url = self.base_url + f"courses/{course_id}/"
        try:
            response = requests.put(url, json={"title": title, "description": description}, headers=self.headers())
            if response.status_code == 200:
                return {"success": True}
            return {"success": False, "error": response.text}
        except Exception as e:
            Logger.error(f"Erreur mise à jour cours: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_course(self, course_id):
        url = self.base_url + f"courses/{course_id}/"
        try:
            response = requests.delete(url, headers=self.headers())
            if response.status_code == 204:
                return {"success": True}
            return {"success": False, "error": response.text}
        except Exception as e:
            Logger.error(f"Erreur suppression cours: {e}")
            return {"success": False, "error": str(e)}
    
    # ========== ENROLLMENTS ==========
    def get_my_enrollments(self):
        url = self.base_url + "my-enrollments/"
        try:
            response = requests.get(url, headers=self.headers(), timeout=6)
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "enrollments": data.get("enrollments", [])}
            return {"success": False, "error": "Erreur de récupération"}
        except Exception as e:
            Logger.error(f"Erreur récupération inscriptions: {e}")
            return {"success": False, "error": str(e)}
    
    def enroll_to_course(self, course_id):
        url = self.base_url + f"courses/{course_id}/enroll/"
        try:
            response = requests.post(url, headers=self.headers(), timeout=6)
            if response.status_code == 201:
                return {"success": True, "message": "Inscription réussie"}
            else:
                error_data = response.json()
                return {"success": False, "error": error_data.get("error", "Erreur d'inscription")}
        except Exception as e:
            Logger.error(f"Erreur inscription: {e}")
            return {"success": False, "error": str(e)}
    
    def unenroll_from_course(self, course_id):
        url = self.base_url + f"courses/{course_id}/unenroll/"
        try:
            response = requests.post(url, headers=self.headers(), timeout=6)
            if response.status_code == 200:
                return {"success": True, "message": "Désinscription réussie"}
            else:
                error_data = response.json()
                return {"success": False, "error": error_data.get("error", "Erreur de désinscription")}
        except Exception as e:
            Logger.error(f"Erreur désinscription: {e}")
            return {"success": False, "error": str(e)}
    
    # ========== QUIZZES ==========
    def get_course_quizzes(self, course_id):
        url = self.base_url + f"courses/{course_id}/quizzes/"
        try:
            response = requests.get(url, headers=self.headers(), timeout=6)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            Logger.error(f"Erreur get_course_quizzes: {e}")
            return []
    
    def get_quiz_questions(self, quiz_id):
        url = self.base_url + f"quizzes/{quiz_id}/take/"
        try:
            response = requests.get(url, headers=self.headers(), timeout=6)
            if response.status_code == 200:
                return response.json().get("questions", [])
            return []
        except Exception as e:
            Logger.error(f"Erreur get_quiz_questions: {e}")
            return []
    
    def submit_quiz(self, quiz_id, answers, time_taken=0):
        url = self.base_url + f"quizzes/{quiz_id}/submit/"
        try:
            response = requests.post(url, json={"answers": answers, "time_taken": time_taken}, headers=self.headers(), timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"success": False, "error": "Erreur de soumission"}
        except Exception as e:
            Logger.error(f"Erreur submit_quiz: {e}")
            return {"success": False, "error": str(e)}

api = APIClient()