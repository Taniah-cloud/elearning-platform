# Plateforme E-learning – 100% Python

## 📌 Description
Plateforme d'apprentissage en ligne développée en 100% Python :
- **Backend** : Django REST Framework
- **Frontend Web** : Django Templates + Plotly (sans Bootstrap)
- **Application Mobile** : Kivy + KivyMD
- **Base de données** : SQLite / PostgreSQL

## 🎯 Fonctionnalités

### ✅ Backend (API REST)
- Authentification par token
- Gestion des utilisateurs (admin, enseignant, étudiant)
- CRUD complet : cours, modules, chapitres
- Système de quiz (QCM) avec notation automatique
- Inscription / désinscription aux cours
- Suivi de progression
- Forum de discussion par cours
- Certificats de complétion (fallback HTML sur Windows)

### ✅ Frontend Web
- Dashboard étudiant : cours inscrits, progression, certificats
- Dashboard enseignant : création/édition de cours, gestion des quiz
- Dashboard admin : gestion utilisateurs et cours
- Graphiques Plotly interactifs
- Interface responsive (CSS pur, zéro Bootstrap)

### ✅ Application Mobile (KivyMD)
- Connexion / déconnexion
- Liste des cours avec inscriptions
- Création/édition/suppression de cours (admin/enseignant)
- Passage de quiz complet avec timer
- Affichage des résultats
- Interface Material Design

## 🛠️ Technologies utilisées

| Composant       | Technologie               |
|-----------------|---------------------------|
| Backend API     | Django + Django REST      |
| Base de données | SQLite / PostgreSQL       |
| Frontend Web    | Django Templates + Plotly |
| Mobile          | Kivy + KivyMD 1.2.0       |
| PDF             | WeasyPrint (fallback HTML)|
| Authentification| Token (DRF)              |
| Markdown        | python-markdown          |

## 📦 Installation

### 1. Cloner le projet
```bash
git clone <votre-repo>
cd e_learning_project

## 🌐 Endpoints API (Django REST)

### Authentification
| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/api/login/` | Connexion, retourne token et rôle |

### Cours
| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/courses/` | Liste tous les cours |
| POST | `/api/courses/` | Crée un cours (admin/teacher) |
| GET | `/api/courses/{id}/` | Détail d'un cours |
| PUT | `/api/courses/{id}/` | Modifie un cours (admin/teacher) |
| DELETE | `/api/courses/{id}/` | Supprime un cours (admin/teacher) |
| POST | `/api/courses/{id}/enroll/` | Inscription étudiant |
| POST | `/api/courses/{id}/unenroll/` | Désinscription |
| GET | `/api/courses/{id}/quizzes/` | Liste des quiz du cours |

### Quiz
| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/quizzes/{id}/take/` | Récupère les questions d'un quiz |
| POST | `/api/quizzes/{id}/submit/` | Soumet les réponses, retourne le score |

### Inscriptions
| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/my-enrollments/` | Cours auxquels l'étudiant est inscrit |

### Certificats
| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/certificates/{id}/download/` | Télécharge un certificat (fallback HTML) |
| GET | `/api/certificates/verify/?id={uuid}` | Vérifie un certificat |

### Dashboard
| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/dashboard/` | Statistiques selon le rôle |
| GET | `/api/progress-chart/` | Données pour graphique Plotly |