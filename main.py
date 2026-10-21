from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
import requests
from datetime import datetime
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
import uuid

SUPABASE_URL = "https://welydrxvqwbwvmlssakl.supabase.co"
SUPABASE_KEY = "sb_publishable_9bvR26XdSX8cPWjBVKsBAg_hGFgVVkD"

class AuthScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "auth"
        layout = MDBoxLayout(orientation='vertical', padding="20dp", spacing="15dp", pos_hint={"center_y": 0.6})
        layout.add_widget(MDLabel(text="Pondeuse Pro", font_style="H4", halign="center", size_hint_y=None, height="60dp"))
        self.email = MDTextField(hint_text="Email", mode="rectangle", size_hint_x=0.9, pos_hint={"center_x": 0.5})
        layout.add_widget(self.email)
        self.password = MDTextField(hint_text="Mot de passe", mode="rectangle", password=True, size_hint_x=0.9, pos_hint={"center_x": 0.5})
        layout.add_widget(self.password)
        btn_login = MDRaisedButton(text="SE CONNECTER", pos_hint={"center_x": 0.5}, size_hint=(0.8, None))
        btn_login.bind(on_press=self.connexion)
        layout.add_widget(btn_login)
        btn_signup = MDRaisedButton(text="CRÉER UN COMPTE", pos_hint={"center_x": 0.5}, size_hint=(0.8, None), md_bg_color=(0.5, 0.5, 0.5, 1))
        btn_signup.bind(on_press=self.inscription)
        layout.add_widget(btn_signup)
        self.message = MDLabel(text="", halign="center", theme_text_color="Custom", text_color=(1, 0, 0, 1))
        layout.add_widget(self.message)
        self.add_widget(layout)

    def connexion(self, instance):
        app = MDApp.get_running_app()
        try:
            url = f"{app.url}/auth/v1/token?grant_type=password"
            headers = {"apikey": app.key, "Content-Type": "application/json"}
            data = {"email": self.email.text, "password": self.password.text}
            res = requests.post(url, headers=headers, json=data)
            if res.status_code == 200:
                app.token = res.json()['access_token']
                app.user_id = res.json()['user']['id']
                self.message.text = "Connexion réussie !"
                self.message.text_color = (0, 0.7, 0, 1)
                app.verifier_ferme()
            else:
                self.message.text = "Erreur : Identifiants incorrects."
        except Exception:
            self.message.text = "Erreur réseau."

    def inscription(self, instance):
        app = MDApp.get_running_app()
        try:
            url = f"{app.url}/auth/v1/signup"
            headers = {"apikey": app.key, "Content-Type": "application/json"}
            data = {"email": self.email.text, "password": self.password.text}
            res = requests.post(url, headers=headers, json=data)
            if res.status_code == 200:
                self.message.text = "Compte créé ! Connectez-vous."
                self.message.text_color = (0, 0.7, 0, 1)
            else:
                self.message.text = "Erreur : " + res.json().get('msg', 'Erreur inconnue')
        except Exception:
            self.message.text = "Erreur réseau."

class FermeSetupScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "ferme_setup"
        layout = MDBoxLayout(orientation='vertical', padding="20dp", spacing="15dp", pos_hint={"center_y": 0.5})
        layout.add_widget(MDLabel(text="Rejoindre ou Créer", font_style="H5", halign="center", size_hint_y=None, height="50dp"))
        self.nom_ferme = MDTextField(hint_text="Nom de la ferme", mode="rectangle", size_hint_x=0.9, pos_hint={"center_x": 0.5})
        layout.add_widget(self.nom_ferme)
        btn_creer = MDRaisedButton(text="CRÉER LA FERME", pos_hint={"center_x": 0.5}, size_hint=(0.8, None))
        btn_creer.bind(on_press=self.creer_ferme)
        layout.add_widget(btn_creer)
        layout.add_widget(MDLabel(text="--- OU ---", halign="center", theme_text_color="Secondary"))
        self.code_input = MDTextField(hint_text="Code de la ferme", mode="rectangle", size_hint_x=0.9, pos_hint={"center_x": 0.5})
        layout.add_widget(self.code_input)
        btn_rejoindre = MDRaisedButton(text="REJOINDRE", pos_hint={"center_x": 0.5}, size_hint=(0.8, None), md_bg_color=(0.2, 0.5, 0.8, 1))
        btn_rejoindre.bind(on_press=self.rejoindre_ferme)
        layout.add_widget(btn_rejoindre)
        self.message = MDLabel(text="", halign="center", theme_text_color="Custom", text_color=(1, 0, 0, 1))
        layout.add_widget(self.message)
        self.add_widget(layout)

    def creer_ferme(self, instance):
        app = MDApp.get_running_app()
        if not self.nom_ferme.text: return
        try:
            code = str(uuid.uuid4().hex[:6]).upper()
            headers = {"apikey": app.key, "Authorization": f"Bearer {app.token}", "Content-Type": "application/json", "Prefer": "return=representation"}
            res = requests.post(f"{app.url}/rest/v1/fermes", headers=headers, json={"nom": self.nom_ferme.text, "code_ferme": code})
            if res.status_code == 201:
                ferme_id = res.json()[0]['id']
                headers_patch = {"apikey": app.key, "Authorization": f"Bearer {app.token}", "Content-Type": "application/json"}
                requests.patch(f"{app.url}/rest/v1/profiles?id=eq.{app.user_id}", headers=headers_patch, json={"ferme_id": ferme_id, "role": "directeur"})
                app.ferme_id = ferme_id
                app.ferme_code = code
                app.user_role = "directeur"
                app.sm.current = "main"
                app.sm.get_screen("main").mettre_a_jour_interface()
            else:
                self.message.text = "Erreur de création."
        except Exception as e:
            self.message.text = f"Erreur : {str(e)[:30]}"

    def rejoindre_ferme(self, instance):
        app = MDApp.get_running_app()
        if not self.code_input.text: return
        try:
            headers = {"apikey": app.key, "Authorization": f"Bearer {app.token}"}
            res = requests.get(f"{app.url}/rest/v1/fermes?code_ferme=eq.{self.code_input.text.upper()}&select=id", headers=headers)
            if res.status_code == 200 and len(res.json()) > 0:
                ferme_id = res.json()[0]['id']
                headers_patch = {"apikey": app.key, "Authorization": f"Bearer {app.token}", "Content-Type": "application/json"}
                requests.patch(f"{app.url}/rest/v1/profiles?id=eq.{app.user_id}", headers=headers_patch, json={"ferme_id": ferme_id, "role": "agent"})
                app.ferme_id = ferme_id
                app.ferme_code = self.code_input.text.upper()
                app.user_role = "agent"
                app.sm.current = "main"
                app.sm.get_screen("main").mettre_a_jour_interface()
            else:
                self.message.text = "Code introuvable."
        except Exception as e:
            self.message.text = f"Erreur : {str(e)[:30]}"

class ProductionTab(MDBottomNavigationItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'production'
        self.text = 'Prod'
        self.icon = 'egg'
        scroll = ScrollView()
        layout = MDBoxLayout(orientation='vertical', spacing="15dp", padding="15dp", size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        layout.add_widget(MDLabel(text="Production", font_style="H5", theme_text_color="Primary", size_hint_y=None))
        self.oeufs = MDTextField(hint_text="Nombre d'œufs", input_filter='int', mode="rectangle")
        layout.add_widget(self.oeufs)
        btn = MDRaisedButton(text="ENREGISTRER", pos_hint={"center_x": 0.5})
        btn.bind(on_press=self.enregistrer)
        layout.add_widget(btn)
        self.msg = MDLabel(text="", theme_text_color="Custom", text_color=(0, 0.7, 0, 1), halign="center")
        layout.add_widget(self.msg)
        scroll.add_widget(layout)
        self.add_widget(scroll)

    def enregistrer(self, instance):
        app = MDApp.get_running_app()
        try:
            data = {"ferme_id": app.ferme_id, "date": datetime.now().strftime("%d/%m %H:%M"), "oeufs": int(self.oeufs.text or 0), "mortes": 0, "total_poules": 100}
            headers = {"apikey": app.key, "Authorization": f"Bearer {app.token}", "Content-Type": "application/json"}
            requests.post(f"{app.url}/rest/v1/production", headers=headers, json=data)
            self.msg.text = "✅ Sauvegardé !"
            self.oeufs.text = ""
        except Exception:
            self.msg.text = "Erreur"

class AlimentationTab(MDBottomNavigationItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'alimentation'
        self.text = 'Alim'
        self.icon = 'food-apple'
        scroll = ScrollView()
        layout = MDBoxLayout(orientation='vertical', spacing="15dp", padding="15dp", size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        layout.add_widget(MDLabel(text="Alimentation", font_style="H5", theme_text_color="Primary", size_hint_y=None))
        self.sacs = MDTextField(hint_text="Nombre de sacs", input_filter='float', mode="rectangle")
        layout.add_widget(self.sacs)
        self.prix = MDTextField(hint_text="Prix d'un sac", input_filter='int', mode="rectangle")
        layout.add_widget(self.prix)
        btn = MDRaisedButton(text="ENREGISTRER", pos_hint={"center_x": 0.5})
        btn.bind(on_press=self.enregistrer)
        layout.add_widget(btn)
        self.msg = MDLabel(text="", theme_text_color="Custom", text_color=(0, 0.7, 0, 1), halign="center")
        layout.add_widget(self.msg)
        scroll.add_widget(layout)
        self.add_widget(scroll)

    def enregistrer(self, instance):
        app = MDApp.get_running_app()
        try:
            sacs = float(self.sacs.text or 0)
            prix = int(self.prix.text or 0)
            data = {"ferme_id": app.ferme_id, "date": datetime.now().strftime("%d/%m %H:%M"), "type_aliment": "Standard", "sacs": sacs, "prix_sac": prix, "cout_total": int(sacs * prix)}
            headers = {"apikey": app.key, "Authorization": f"Bearer {app.token}", "Content-Type": "application/json"}
            requests.post(f"{app.url}/rest/v1/alimentation", headers=headers, json=data)
            self.msg.text = "✅ Sauvegardé !"
            self.sacs.text = ""
            self.prix.text = ""
        except Exception:
            self.msg.text = "Erreur"

class SanteTab(MDBottomNavigationItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'sante'
        self.text = 'Santé'
        self.icon = 'medical-bag'
        scroll = ScrollView()
        layout = MDBoxLayout(orientation='vertical', spacing="15dp", padding="15dp", size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        layout.add_widget(MDLabel(text="Santé", font_style="H5", theme_text_color="Primary", size_hint_y=None))
        self.type_int = MDTextField(hint_text="Type", mode="rectangle")
        layout.add_widget(self.type_int)
        self.cout = MDTextField(hint_text="Coût (FCFA)", input_filter='int', mode="rectangle")
        layout.add_widget(self.cout)
        btn = MDRaisedButton(text="ENREGISTRER", pos_hint={"center_x": 0.5})
        btn.bind(on_press=self.enregistrer)
        layout.add_widget(btn)
        self.msg = MDLabel(text="", theme_text_color="Custom", text_color=(0, 0.7, 0, 1), halign="center")
        layout.add_widget(self.msg)
        scroll.add_widget(layout)
        self.add_widget(scroll)

    def enregistrer(self, instance):
        app = MDApp.get_running_app()
        try:
            data = {"ferme_id": app.ferme_id, "date": datetime.now().strftime("%d/%m %H:%M"), "type_intervention": self.type_int.text or "N/A", "produit": "-", "cout": int(self.cout.text or 0), "rappel_date": "-"}
            headers = {"apikey": app.key, "Authorization": f"Bearer {app.token}", "Content-Type": "application/json"}
            requests.post(f"{app.url}/rest/v1/sante", headers=headers, json=data)
            self.msg.text = "✅ Sauvegardé !"
            self.type_int.text = ""
            self.cout.text = ""
        except Exception:
            self.msg.text = "Erreur"

class PoidsTab(MDBottomNavigationItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'poids'
        self.text = 'Poids'
        self.icon = 'scale'
        scroll = ScrollView()
        layout = MDBoxLayout(orientation='vertical', spacing="15dp", padding="15dp", size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        layout.add_widget(MDLabel(text="Poids", font_style="H5", theme_text_color="Primary", size_hint_y=None))
        self.age = MDTextField(hint_text="Âge", input_filter='int', mode="rectangle")
        layout.add_widget(self.age)
        self.poids = MDTextField(hint_text="Poids (g)", input_filter='int', mode="rectangle")
        layout.add_widget(self.poids)
        btn = MDRaisedButton(text="ENREGISTRER", pos_hint={"center_x": 0.5})
        btn.bind(on_press=self.enregistrer)
        layout.add_widget(btn)
        self.msg = MDLabel(text="", theme_text_color="Custom", text_color=(0, 0.7, 0, 1), halign="center")
        layout.add_widget(self.msg)
        scroll.add_widget(layout)
        self.add_widget(scroll)

    def enregistrer(self, instance):
        app = MDApp.get_running_app()
        try:
            data = {"ferme_id": app.ferme_id, "date": datetime.now().strftime("%d/%m %H:%M"), "age_semaines": int(self.age.text or 0), "poids_moyen": int(self.poids.text or 0)}
            headers = {"apikey": app.key, "Authorization": f"Bearer {app.token}", "Content-Type": "application/json"}
            requests.post(f"{app.url}/rest/v1/poids", headers=headers, json=data)
            self.msg.text = "✅ Sauvegardé !"
            self.age.text = ""
            self.poids.text = ""
        except Exception:
            self.msg.text = "Erreur"

class VentesTab(MDBottomNavigationItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'ventes'
        self.text = 'Ventes'
        self.icon = 'cash-multiple'
        scroll = ScrollView()
        layout = MDBoxLayout(orientation='vertical', spacing="15dp", padding="15dp", size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        layout.add_widget(MDLabel(text="Ventes", font_style="H5", theme_text_color="Primary", size_hint_y=None))
        self.plateaux = MDTextField(hint_text="Plateaux", input_filter='int', mode="rectangle")
        layout.add_widget(self.plateaux)
        self.prix = MDTextField(hint_text="Prix", input_filter='int', mode="rectangle")
        layout.add_widget(self.prix)
        btn = MDRaisedButton(text="ENREGISTRER", pos_hint={"center_x": 0.5})
        btn.bind(on_press=self.enregistrer)
        layout.add_widget(btn)
        self.msg = MDLabel(text="", theme_text_color="Custom", text_color=(0, 0.7, 0, 1), halign="center")
        layout.add_widget(self.msg)
        scroll.add_widget(layout)
        self.add_widget(scroll)

    def enregistrer(self, instance):
        app = MDApp.get_running_app()
        try:
            plat = int(self.plateaux.text or 0)
            prix = int(self.prix.text or 0)
            data = {"ferme_id": app.ferme_id, "date": datetime.now().strftime("%d/%m %H:%M"), "plateaux": plat, "prix_plateau": prix, "recette_totale": plat * prix}
            headers = {"apikey": app.key, "Authorization": f"Bearer {app.token}", "Content-Type": "application/json"}
            requests.post(f"{app.url}/rest/v1/ventes", headers=headers, json=data)
            self.msg.text = "✅ Sauvegardé !"
            self.plateaux.text = ""
            self.prix.text = ""
        except Exception:
            self.msg.text = "Erreur"

class BilanTab(MDBottomNavigationItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'bilan'
        self.text = 'Bilan'
        self.icon = 'chart-pie'
        layout = MDBoxLayout(orientation='vertical', padding="20dp", spacing="15dp")
        self.l_rec = MDLabel(text="Recettes : 0 F", font_style="H6")
        self.l_dep = MDLabel(text="Dépenses : 0 F", font_style="H6")
        self.l_ben = MDLabel(text="Bénéfice : 0 F", font_style="H5", bold=True)
        layout.add_widget(self.l_rec)
        layout.add_widget(self.l_dep)
        layout.add_widget(self.l_ben)
        btn = MDRaisedButton(text="ACTUALISER", pos_hint={"center_x": 0.5})
        btn.bind(on_press=self.calculer)
        layout.add_widget(btn)
        self.add_widget(layout)

    def calculer(self, instance):
        app = MDApp.get_running_app()
        try:
            headers = {"apikey": app.key, "Authorization": f"Bearer {app.token}"}
            v = requests.get(f"{app.url}/rest/v1/ventes?ferme_id=eq.{app.ferme_id}&select=recette_totale", headers=headers).json()
            rec = sum([row['recette_totale'] for row in v]) if v else 0
            
            a = requests.get(f"{app.url}/rest/v1/alimentation?ferme_id=eq.{app.ferme_id}&select=cout_total", headers=headers).json()
            dep_a = sum([row['cout_total'] for row in a]) if a else 0
            
            s = requests.get(f"{app.url}/rest/v1/sante?ferme_id=eq.{app.ferme_id}&select=cout", headers=headers).json()
            dep_s = sum([row['cout'] for row in s]) if s else 0
            
            dep = dep_a + dep_s
            ben = rec - dep
            
            self.l_rec.text = f"Recettes : {rec:,} F"
            self.l_dep.text = f"Dépenses : {dep:,} F"
            self.l_ben.text = f"Bénéfice : {ben:,} F"
            self.l_ben.text_color = (0, 0.6, 0, 1) if ben >= 0 else (0.8, 0, 0, 1)
        except Exception:
            self.l_ben.text = "Erreur de calcul"

class RapportTab(MDBottomNavigationItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'rapport'
        self.text = 'Rapport'
        self.icon = 'file-document'
        layout = MDBoxLayout(orientation='vertical', padding="15dp", spacing="15dp")
        self.txt = MDTextField(text="Cliquez sur 'Générer'", readonly=True, multiline=True)
        layout.add_widget(self.txt)
        btn = MDRaisedButton(text="GÉNÉRER", pos_hint={"center_x": 0.5})
        btn.bind(on_press=self.generer)
        layout.add_widget(btn)
        self.status = MDLabel(text="", halign="center")
        layout.add_widget(self.status)
        self.add_widget(layout)

    def generer(self, instance):
        app = MDApp.get_running_app()
        try:
            headers = {"apikey": app.key, "Authorization": f"Bearer {app.token}"}
            v = requests.get(f"{app.url}/rest/v1/ventes?ferme_id=eq.{app.ferme_id}&select=recette_totale,plateaux", headers=headers).json()
            rec = sum([row['recette_totale'] for row in v]) if v else 0
            plat = sum([row['plateaux'] for row in v]) if v else 0
            
            a = requests.get(f"{app.url}/rest/v1/alimentation?ferme_id=eq.{app.ferme_id}&select=cout_total,sacs", headers=headers).json()
            dep_a = sum([row['cout_total'] for row in a]) if a else 0
            sacs = sum([row['sacs'] for row in a]) if a else 0
            
            s = requests.get(f"{app.url}/rest/v1/sante?ferme_id=eq.{app.ferme_id}&select=cout", headers=headers).json()
            dep_s = sum([row['cout'] for row in s]) if s else 0
            
            p = requests.get(f"{app.url}/rest/v1/production?ferme_id=eq.{app.ferme_id}&select=oeufs", headers=headers).json()
            oeufs = sum([row['oeufs'] for row in p]) if p else 0

            dep = dep_a + dep_s
            ben = rec - dep
            date_jour = datetime.now().strftime("%d/%m/%Y")

            texte = f"🐔 *RAPPORT PONDEUSE PRO* 🐔\nFerme : {app.ferme_code}\nDate : {date_jour}\n"
            texte += f"-------------------------\n"
            texte += f"🥚 *PRODUCTION* : {oeufs} œufs\n"
            texte += f"🌾 *ALIM* : {sacs} sacs ({dep_a} FCFA)\n"
            texte += f"💉 *SANTE* : {dep_s} FCFA\n"
            texte += f"💰 *FINANCES* :\n"
            texte += f"- Recettes : {rec} FCFA\n"
            texte += f"- Dépenses : {dep} FCFA\n"
            texte += f"-------------------------\n"
            texte += f"✅ *BÉNÉFICE : +{ben} FCFA*\n" if ben >= 0 else f"❌ *PERTE : {ben} FCFA*\n"

            self.txt.text = texte
            self.status.text = "✅ Généré !"
        except Exception:
            self.status.text = "Erreur"

class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "main"
        self.root_layout = MDBoxLayout(orientation='vertical')
        self.toolbar = MDTopAppBar(title="Ferme", right_action_items=[["logout", lambda x: self.deconnexion()]])
        self.root_layout.add_widget(self.toolbar)
        self.add_widget(self.root_layout)
        self.nav = None

    def mettre_a_jour_interface(self):
        app = MDApp.get_running_app()
        self.toolbar.title = f"Ferme : {app.ferme_code} ({app.user_role.capitalize()})"
        if self.nav is not None:
            self.root_layout.remove_widget(self.nav)
        self.nav = MDBottomNavigation()
        self.nav.add_widget(ProductionTab())
        self.nav.add_widget(AlimentationTab())
        self.nav.add_widget(SanteTab())
        self.nav.add_widget(PoidsTab())
        self.nav.add_widget(VentesTab())
        if app.user_role == 'directeur':
            self.nav.add_widget(BilanTab())
            self.nav.add_widget(RapportTab())
        self.root_layout.add_widget(self.nav)

    def deconnexion(self):
        app = MDApp.get_running_app()
        app.token = None
        app.user_id = None
        app.ferme_id = None
        app.ferme_code = None
        app.user_role = "agent"
        auth_screen = app.sm.get_screen("auth")
        auth_screen.email.text = ""
        auth_screen.password.text = ""
        auth_screen.message.text = ""
        app.sm.current = "auth"

class PondeuseApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Green"
        self.url = SUPABASE_URL
        self.key = SUPABASE_KEY
        self.token = None
        self.user_id = None
        self.ferme_id = None
        self.ferme_code = None
        self.user_role = "agent"
        self.sm = MDScreenManager()
        self.sm.add_widget(AuthScreen())
        self.sm.add_widget(FermeSetupScreen())
        self.sm.add_widget(MainScreen())
        return self.sm

    def verifier_ferme(self):
        try:
            headers = {"apikey": self.key, "Authorization": f"Bearer {self.token}"}
            res = requests.get(f"{self.url}/rest/v1/profiles?id=eq.{self.user_id}&select=ferme_id,role", headers=headers)
            if res.status_code == 200 and len(res.json()) > 0:
                data = res.json()[0]
                if data.get('ferme_id'):
                    self.ferme_id = data['ferme_id']
                    self.user_role = data['role']
                    f = requests.get(f"{self.url}/rest/v1/fermes?id=eq.{self.ferme_id}&select=code_ferme", headers=headers).json()
                    self.ferme_code = f[0]['code_ferme']
                    self.sm.current = "main"
                    self.sm.get_screen("main").mettre_a_jour_interface()
                else:
                    self.sm.current = "ferme_setup"
            else:
                self.sm.current = "ferme_setup"
        except Exception:
            self.sm.current = "ferme_setup"

if __name__ == '__main__':
    PondeuseApp().run()
