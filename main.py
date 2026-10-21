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
from supabase import create_client, Client
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
            res = app.supabase.auth.sign_in_with_password({"email": self.email.text, "password": self.password.text})
            app.user_id = res.user.id
            self.message.text = "Connexion réussie !"
            self.message.text_color = (0, 0.7, 0, 1)
            app.verifier_ferme()
        except Exception:
            self.message.text = "Erreur : Identifiants incorrects."

    def inscription(self, instance):
        app = MDApp.get_running_app()
        try:
            app.supabase.auth.sign_up({"email": self.email.text, "password": self.password.text})
            self.message.text = "Compte créé ! Connectez-vous."
            self.message.text_color = (0, 0.7, 0, 1)
        except Exception as e:
            self.message.text = f"Erreur : {str(e)}"

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
        
        self.code_input = MDTextField(hint_text="Code de la ferme (ex: 8F256B)", mode="rectangle", size_hint_x=0.9, pos_hint={"center_x": 0.5})
        layout.add_widget(self.code_input)
        
        btn_rejoindre = MDRaisedButton(text="REJOINDRE L'ÉQUIPE", pos_hint={"center_x": 0.5}, size_hint=(0.8, None), md_bg_color=(0.2, 0.5, 0.8, 1))
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
            res = app.supabase.table("fermes").insert({"nom": self.nom_ferme.text, "code_ferme": code}).execute()
            ferme_id = res.data[0]['id']
            app.supabase.table("profiles").update({"ferme_id": ferme_id, "role": "directeur"}).eq("id", app.user_id).execute()
            app.ferme_id = ferme_id
            app.ferme_code = code
            app.user_role = "directeur"
            app.sm.current = "main"
            app.sm.get_screen("main").mettre_a_jour_interface()
        except Exception as e:
            self.message.text = f"Erreur : {str(e)}"

    def rejoindre_ferme(self, instance):
        app = MDApp.get_running_app()
        if not self.code_input.text: return
        try:
            res = app.supabase.table("fermes").select("id").eq("code_ferme", self.code_input.text.upper()).execute()
            if not res.data:
                self.message.text = "Code introuvable."
                return
            ferme_id = res.data[0]['id']
            app.supabase.table("profiles").update({"ferme_id": ferme_id, "role": "agent"}).eq("id", app.user_id).execute()
            app.ferme_id = ferme_id
            app.ferme_code = self.code_input.text.upper()
            app.user_role = "agent"
            app.sm.current = "main"
            app.sm.get_screen("main").mettre_a_jour_interface()
        except Exception as e:
            self.message.text = f"Erreur : {str(e)}"

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
        
        layout.add_widget(MDLabel(text="--- Derniers enregistrements ---", font_style="Subtitle1", size_hint_y=None, height="40dp"))
        self.history = MDBoxLayout(orientation='vertical', spacing="5dp", size_hint_y=None)
        self.history.bind(minimum_height=self.history.setter('height'))
        layout.add_widget(self.history)
        
        scroll.add_widget(layout)
        self.add_widget(scroll)
        Clock.schedule_once(lambda dt: self.charger_historique(), 0.5)

    def enregistrer(self, instance):
        app = MDApp.get_running_app()
        try:
            data = {"ferme_id": app.ferme_id, "date": datetime.now().strftime("%d/%m %H:%M"), "oeufs": int(self.oeufs.text or 0), "mortes": 0, "total_poules": 100}
            app.supabase.table("production").insert(data).execute()
            self.msg.text = "✅ Sauvegardé !"
            self.oeufs.text = ""
            self.charger_historique()
        except Exception:
            self.msg.text = "Erreur"

    def charger_historique(self):
        app = MDApp.get_running_app()
        if not app.ferme_id: return
        self.history.clear_widgets()
        try:
            res = app.supabase.table("production").select("date, oeufs").eq("ferme_id", app.ferme_id).order("id", desc=True).limit(5).execute()
            for row in res.data:
                self.history.add_widget(MDLabel(text=f"{row['date']} : {row['oeufs']} œufs", font_style="Caption"))
        except: pass

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
        self.prix = MDTextField(hint_text="Prix d'un sac (FCFA)", input_filter='int', mode="rectangle")
        layout.add_widget(self.prix)
        btn = MDRaisedButton(text="ENREGISTRER", pos_hint={"center_x": 0.5})
        btn.bind(on_press=self.enregistrer)
        layout.add_widget(btn)
        self.msg = MDLabel(text="", theme_text_color="Custom", text_color=(0, 0.7, 0, 1), halign="center")
        layout.add_widget(self.msg)
        
        layout.add_widget(MDLabel(text="--- Derniers enregistrements ---", font_style="Subtitle1", size_hint_y=None, height="40dp"))
        self.history = MDBoxLayout(orientation='vertical', spacing="5dp", size_hint_y=None)
        self.history.bind(minimum_height=self.history.setter('height'))
        layout.add_widget(self.history)
        
        scroll.add_widget(layout)
        self.add_widget(scroll)
        Clock.schedule_once(lambda dt: self.charger_historique(), 0.5)

    def enregistrer(self, instance):
        app = MDApp.get_running_app()
        try:
            sacs = float(self.sacs.text or 0)
            prix = int(self.prix.text or 0)
            data = {"ferme_id": app.ferme_id, "date": datetime.now().strftime("%d/%m %H:%M"), "type_aliment": "Standard", "sacs": sacs, "prix_sac": prix, "cout_total": int(sacs * prix)}
            app.supabase.table("alimentation").insert(data).execute()
            self.msg.text = "✅ Dépense sauvegardée !"
            self.sacs.text = ""
            self.prix.text = ""
            self.charger_historique()
        except Exception:
            self.msg.text = "Erreur"

    def charger_historique(self):
        app = MDApp.get_running_app()
        if not app.ferme_id: return
        self.history.clear_widgets()
        try:
            res = app.supabase.table("alimentation").select("date, sacs, cout_total").eq("ferme_id", app.ferme_id).order("id", desc=True).limit(5).execute()
            for row in res.data:
                self.history.add_widget(MDLabel(text=f"{row['date']} : {row['sacs']} sacs ({row['cout_total']} F)", font_style="Caption"))
        except: pass

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
        self.type_int = MDTextField(hint_text="Type (Vaccin...)", mode="rectangle")
        layout.add_widget(self.type_int)
        self.produit = MDTextField(hint_text="Produit", mode="rectangle")
        layout.add_widget(self.produit)
        self.cout = MDTextField(hint_text="Coût (FCFA)", input_filter='int', mode="rectangle")
        layout.add_widget(self.cout)
        self.rappel = MDTextField(hint_text="Rappel (JJ/MM/AAAA)", mode="rectangle")
        layout.add_widget(self.rappel)
        btn = MDRaisedButton(text="ENREGISTRER", pos_hint={"center_x": 0.5})
        btn.bind(on_press=self.enregistrer)
        layout.add_widget(btn)
        self.msg = MDLabel(text="", theme_text_color="Custom", text_color=(0, 0.7, 0, 1), halign="center")
        layout.add_widget(self.msg)
        
        layout.add_widget(MDLabel(text="--- Derniers enregistrements ---", font_style="Subtitle1", size_hint_y=None, height="40dp"))
        self.history = MDBoxLayout(orientation='vertical', spacing="5dp", size_hint_y=None)
        self.history.bind(minimum_height=self.history.setter('height'))
        layout.add_widget(self.history)
        
        scroll.add_widget(layout)
        self.add_widget(scroll)
        Clock.schedule_once(lambda dt: self.charger_historique(), 0.5)

    def enregistrer(self, instance):
        app = MDApp.get_running_app()
        try:
            data = {"ferme_id": app.ferme_id, "date": datetime.now().strftime("%d/%m %H:%M"), "type_intervention": self.type_int.text or "N/A", "produit": self.produit.text or "-", "cout": int(self.cout.text or 0), "rappel_date": self.rappel.text or "-"}
            app.supabase.table("sante").insert(data).execute()
            self.msg.text = "✅ Intervention enregistrée !"
            self.type_int.text = ""
            self.produit.text = ""
            self.cout.text = ""
            self.rappel.text = ""
            self.charger_historique()
        except Exception:
            self.msg.text = "Erreur"

    def charger_historique(self):
        app = MDApp.get_running_app()
        if not app.ferme_id: return
        self.history.clear_widgets()
        try:
            res = app.supabase.table("sante").select("date, type_intervention, cout").eq("ferme_id", app.ferme_id).order("id", desc=True).limit(5).execute()
            for row in res.data:
                self.history.add_widget(MDLabel(text=f"{row['date']} : {row['type_intervention']} ({row['cout']} F)", font_style="Caption"))
        except: pass

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
        self.age = MDTextField(hint_text="Âge (semaines)", input_filter='int', mode="rectangle")
        layout.add_widget(self.age)
        self.poids = MDTextField(hint_text="Poids moyen (grammes)", input_filter='int', mode="rectangle")
        layout.add_widget(self.poids)
        btn = MDRaisedButton(text="ENREGISTRER", pos_hint={"center_x": 0.5})
        btn.bind(on_press=self.enregistrer)
        layout.add_widget(btn)
        self.msg = MDLabel(text="", theme_text_color="Custom", text_color=(0, 0.7, 0, 1), halign="center")
        layout.add_widget(self.msg)
        
        layout.add_widget(MDLabel(text="--- Derniers enregistrements ---", font_style="Subtitle1", size_hint_y=None, height="40dp"))
        self.history = MDBoxLayout(orientation='vertical', spacing="5dp", size_hint_y=None)
        self.history.bind(minimum_height=self.history.setter('height'))
        layout.add_widget(self.history)
        
        scroll.add_widget(layout)
        self.add_widget(scroll)
        Clock.schedule_once(lambda dt: self.charger_historique(), 0.5)

    def enregistrer(self, instance):
        app = MDApp.get_running_app()
        try:
            data = {"ferme_id": app.ferme_id, "date": datetime.now().strftime("%d/%m %H:%M"), "age_semaines": int(self.age.text or 0), "poids_moyen": int(self.poids.text or 0)}
            app.supabase.table("poids").insert(data).execute()
            self.msg.text = "✅ Poids enregistré !"
            self.age.text = ""
            self.poids.text = ""
            self.charger_historique()
        except Exception:
            self.msg.text = "Erreur"

    def charger_historique(self):
        app = MDApp.get_running_app()
        if not app.ferme_id: return
        self.history.clear_widgets()
        try:
            res = app.supabase.table("poids").select("date, age_semaines, poids_moyen").eq("ferme_id", app.ferme_id).order("id", desc=True).limit(5).execute()
            for row in res.data:
                self.history.add_widget(MDLabel(text=f"{row['date']} : {row['age_semaines']} sem. ({row['poids_moyen']} g)", font_style="Caption"))
        except: pass

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
        self.plateaux = MDTextField(hint_text="Plateaux vendus", input_filter='int', mode="rectangle")
        layout.add_widget(self.plateaux)
        self.prix = MDTextField(hint_text="Prix d'un plateau", input_filter='int', mode="rectangle")
        layout.add_widget(self.prix)
        btn = MDRaisedButton(text="ENREGISTRER", pos_hint={"center_x": 0.5})
        btn.bind(on_press=self.enregistrer)
        layout.add_widget(btn)
        self.msg = MDLabel(text="", theme_text_color="Custom", text_color=(0, 0.7, 0, 1), halign="center")
        layout.add_widget(self.msg)
        
        layout.add_widget(MDLabel(text="--- Derniers enregistrements ---", font_style="Subtitle1", size_hint_y=None, height="40dp"))
        self.history = MDBoxLayout(orientation='vertical', spacing="5dp", size_hint_y=None)
        self.history.bind(minimum_height=self.history.setter('height'))
        layout.add_widget(self.history)
        
        scroll.add_widget(layout)
        self.add_widget(scroll)
        Clock.schedule_once(lambda dt: self.charger_historique(), 0.5)

    def enregistrer(self, instance):
        app = MDApp.get_running_app()
        try:
            plat = int(self.plateaux.text or 0)
            prix = int(self.prix.text or 0)
            data = {"ferme_id": app.ferme_id, "date": datetime.now().strftime("%d/%m %H:%M"), "plateaux": plat, "prix_plateau": prix, "recette_totale": plat * prix}
            app.supabase.table("ventes").insert(data).execute()
            self.msg.text = "✅ Recette sauvegardée !"
            self.plateaux.text = ""
            self.prix.text = ""
            self.charger_historique()
        except Exception:
            self.msg.text = "Erreur"

    def charger_historique(self):
        app = MDApp.get_running_app()
        if not app.ferme_id: return
        self.history.clear_widgets()
        try:
            res = app.supabase.table("ventes").select("date, plateaux, recette_totale").eq("ferme_id", app.ferme_id).order("id", desc=True).limit(5).execute()
            for row in res.data:
                self.history.add_widget(MDLabel(text=f"{row['date']} : {row['plateaux']} plateaux ({row['recette_totale']} F)", font_style="Caption"))
        except: pass

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
            v = app.supabase.table("ventes").select("recette_totale").eq("ferme_id", app.ferme_id).execute()
            rec = sum([row['recette_totale'] for row in v.data]) if v.data else 0
            
            a = app.supabase.table("alimentation").select("cout_total").eq("ferme_id", app.ferme_id).execute()
            dep_a = sum([row['cout_total'] for row in a.data]) if a.data else 0
            
            s = app.supabase.table("sante").select("cout").eq("ferme_id", app.ferme_id).execute()
            dep_s = sum([row['cout'] for row in s.data]) if s.data else 0
            
            dep = dep_a + dep_s
            ben = rec - dep
            
            self.l_rec.text = f"Recettes : {rec:,} F"
            self.l_dep.text = f"Dépenses (Alim + Santé) : {dep:,} F"
            self.l_ben.text = f"Bénéfice : {ben:,} F"
            self.l_ben.text_color = (0, 0.6, 0, 1) if ben >= 0 else (0.8, 0, 0, 1)
        except Exception as e:
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
        
        btn = MDRaisedButton(text="GÉNÉRER LE RAPPORT", pos_hint={"center_x": 0.5})
        btn.bind(on_press=self.generer)
        layout.add_widget(btn)
        
        btn_copy = MDRaisedButton(text="COPIER POUR WHATSAPP", pos_hint={"center_x": 0.5}, md_bg_color=(0, 0.6, 0, 1))
        btn_copy.bind(on_press=self.copier)
        layout.add_widget(btn_copy)
        
        self.status = MDLabel(text="", halign="center")
        layout.add_widget(self.status)
        self.add_widget(layout)

    def generer(self, instance):
        app = MDApp.get_running_app()
        try:
            v = app.supabase.table("ventes").select("recette_totale, plateaux").eq("ferme_id", app.ferme_id).execute()
            rec = sum([row['recette_totale'] for row in v.data]) if v.data else 0
            plat = sum([row['plateaux'] for row in v.data]) if v.data else 0
            
            a = app.supabase.table("alimentation").select("cout_total, sacs").eq("ferme_id", app.ferme_id).execute()
            dep_a = sum([row['cout_total'] for row in a.data]) if a.data else 0
            sacs = sum([row['sacs'] for row in a.data]) if a.data else 0
            
            s = app.supabase.table("sante").select("cout").eq("ferme_id", app.ferme_id).execute()
            dep_s = sum([row['cout'] for row in s.data]) if s.data else 0
            
            p = app.supabase.table("production").select("oeufs").eq("ferme_id", app.ferme_id).execute()
            oeufs = sum([row['oeufs'] for row in p.data]) if p.data else 0

            dep = dep_a + dep_s
            ben = rec - dep
            date_jour = datetime.now().strftime("%d/%m/%Y")

            texte = f"🐔 *RAPPORT PONDEUSE PRO* 🐔\nFerme : {app.ferme_code}\nDate : {date_jour}\n"
            texte += f"-------------------------\n"
            texte += f"🥚 *PRODUCTION* : {oeufs} œufs\n"
            texte += f"🌾 *ALIM* : {sacs} sacs ({dep_a} FCFA)\n"
            texte += f"💉 *SANTE* : {dep_s} FCFA\n"
            texte += f"💰 *FINANCES* :\n"
            texte += f"- Plateaux vendus : {plat}\n"
            texte += f"- Recettes : {rec} FCFA\n"
            texte += f"- Dépenses : {dep} FCFA\n"
            texte += f"-------------------------\n"
            if ben >= 0:
                texte += f"✅ *BÉNÉFICE : +{ben} FCFA*\n"
            else:
                texte += f"❌ *PERTE : {ben} FCFA*\n"

            self.txt.text = texte
            self.status.text = "✅ Rapport généré !"
        except Exception:
            self.status.text = "Erreur"

    def copier(self, instance):
        if "Cliquez sur" in self.txt.text: return
        Clipboard.copy(self.txt.text)
        self.status.text = "✅ Copié !"

class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "main"
        self.root_layout = MDBoxLayout(orientation='vertical')
        
        self.toolbar = MDTopAppBar(
            title="Ferme", 
            right_action_items=[["logout", lambda x: self.deconnexion()]]
        )
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
        try:
            app.supabase.auth.sign_out()
        except: pass
        
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
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
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
            res = self.supabase.table("profiles").select("ferme_id, role").eq("id", self.user_id).execute()
            if res.data and res.data[0]['ferme_id']:
                self.ferme_id = res.data[0]['ferme_id']
                self.user_role = res.data[0]['role']
                
                f = self.supabase.table("fermes").select("code_ferme").eq("id", self.ferme_id).execute()
                self.ferme_code = f.data[0]['code_ferme']
                
                self.sm.current = "main"
                self.sm.get_screen("main").mettre_a_jour_interface()
            else:
                self.sm.current = "ferme_setup"
        except Exception:
            self.sm.current = "ferme_setup"

if __name__ == '__main__':
    PondeuseApp().run()