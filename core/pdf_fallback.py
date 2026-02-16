"""
Fallback pour la génération de PDF lorsque WeasyPrint n'est pas disponible
"""

class PDFFallback:
    @staticmethod
    def generate_certificate_html(certificate):
        """Génère un HTML simple pour le certificat"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Certificat - {certificate.course.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 50px; }}
                .certificate {{ border: 20px solid #2c3e50; padding: 50px; }}
                h1 {{ color: #2c3e50; text-align: center; }}
                .student {{ font-size: 28px; text-align: center; margin: 30px 0; }}
                .course {{ color: #3498db; text-align: center; font-size: 24px; }}
                .info {{ margin-top: 40px; }}
                .footer {{ margin-top: 60px; display: flex; justify-content: space-between; }}
            </style>
        </head>
        <body>
            <div class="certificate">
                <h1>CERTIFICAT DE COMPLÉTION</h1>
                <p style="text-align: center;">Ce certificat est décerné à</p>
                <div class="student">{certificate.student.get_full_name() or certificate.student.username}</div>
                <p style="text-align: center;">pour avoir complété avec succès</p>
                <div class="course">{certificate.course.title}</div>
                
                <div class="info">
                    <p><strong>Date d'émission:</strong> {certificate.issued_at.strftime('%d %B %Y')}</p>
                    <p><strong>Identifiant:</strong> {str(certificate.certificate_id)[:8].upper()}</p>
                    <p><strong>Enseignant:</strong> {certificate.course.teacher.get_full_name() or certificate.course.teacher.username}</p>
                </div>
                
                <div class="footer">
                    <div>
                        <hr style="width: 200px;">
                        <p>Signature de l'enseignant</p>
                    </div>
                    <div>
                        <hr style="width: 200px;">
                        <p>Date</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """