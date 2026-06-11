from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app, origins=["*"])

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

ARTURIN_CONTEXT = """Tu es un assistant stratégique, analytique et commercial pour Artur'in.
Positionnement : partenaire communication des réseaux multi-points de vente. IA + expertise sectorielle. Mission : offrir à chaque entreprise locale la vitrine digitale qu'elle mérite. Piliers : on vous trouve / on vous choisit / on vous recommande.
Clients typiques : agents immobiliers, opticiens, pharmaciens, dentistes, assureurs, avocats, notaires, experts-comptables, CGP/CGPI, coaches sportifs, garagistes, concessionnaires.
BASE UPSELLS : Shoot'In 30€/mois (12 mois) | Site web 295€HT création + 70€HT/mois (12 mois, pas de préavis) | Boost'In dès 50€/mois (6 mois) | Multi-sites 59€/établissement | Contenu EFL 60€/mois (8 articles/mois) | Seeble 30-80€/mois (prospection LinkedIn) | LinkedIn supplémentaire 50€/mois | Self'in gratuit (10 publications IA personnalisées, formulaire : https://forms.fillout.com/t/hdEdvdk4wrus) | Renouvellement Essilor : UNIQUEMENT opticiens, 1200€/6 mois ou 2400€/12 mois + Shoot'in offert."""

def call_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0.3
    }
    response = requests.post(GROQ_URL, headers=headers, json=body, timeout=60)
    data = response.json()
    return data["choices"][0]["message"]["content"]

@app.route("/api/mission1", methods=["POST"])
def mission1():
    try:
        body = request.json
        client = body.get("client", "")
        context = body.get("context", "")
        transcription = body.get("transcription", "")

        prompt = f"""{ARTURIN_CONTEXT}

MISSION 1 — COMPTE-RENDU DE CALL
Client : {client}
{f"Contexte : {context}" if context else ""}
Transcription : {transcription}

Génère le CR en respectant STRICTEMENT ces règles :
- Chaque ➤ doit commencer sur une NOUVELLE ligne (jamais deux ➤ sur la même ligne horizontale)
- Titres en MAJUSCULES avec émoji, sans numéro
- Utilise "je" pour parler de l'agent CS
- Prêt à copier dans Salesforce (aucune balise, aucune citation numérotée)
- ZÉRO pitch produit dans les points discutés — données brutes client uniquement
- Ne pas suivre l'ordre chronologique — regrouper par thèmes

FORMAT OBLIGATOIRE :
────────────────────
{client} — Compte-rendu

🔜 A VOIR AU PROCHAIN CALL
[Ce que le CS devra creuser. Si rien : RAS. Optionnel : upsell possible max 100 caractères]

🔋 RÉSUMÉ EXPRESS
[Résumé rapide du CR pour relire avant le prochain call]

👤 PROFIL DU CLIENT
[STRICTEMENT 2 lignes max]
➤ [Prénom interlocuteur], [Métier/Rôle/Localisation], humeur : [3 mots]
➤ Niveau digital : [niveau constaté] | État du commerce : [infos business si mentionnées]

📝 POINTS DISCUTÉS
[2-3 dossiers thématiques MAX en MAJUSCULES, puces ➤ en dessous, max 2-3 puces par thème]
[❤️ Anecdote humaine UNIQUEMENT si mentionnée explicitement dans le call]

🤝 UPSELL ET SOLUTIONS PRÉSENTÉES
[Si upsell évoqué : description + réaction client. Sinon : RAS]

────────────────────
📍 ACTIONS A FAIRE
[Actions immédiates du CS. Sinon : RAS]

────────────────────
💬 FEEDBACK PRODUIT
[Retours sur produits Artur'in si pertinent. Sinon : omettre cette section]"""

        result = call_groq(prompt)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/mission2", methods=["POST"])
def mission2():
    try:
        body = request.json
        prenom = body.get("prenom", "")
        cs = body.get("cs", "")
        content = body.get("content", "")
        upsell = body.get("upsell", "")

        site_web_template = ""
        selfin_template = ""

        if "Site web" in upsell:
            site_web_template = """
TEMPLATE SITE WEB OBLIGATOIRE dans l'email :
"Comme convenu, voici la présentation de notre accompagnement site internet.
Notre engagement : un site web professionnel clé en main.
-> Un accompagnement dédié : chef de projet expert + votre CS coach
-> Un design à votre image, fidèle à votre marque
-> Un contenu co-construit avec vous
-> Gestion technique complète : domaine, hébergement, sécurisation
-> Site responsive : ordinateur et mobile
-> Site optimisé SEO + contenus réguliers
Politique Commerciale :
-> Frais de création : 295€HT (une seule fois)
-> Abonnement mensuel : 70€HT/mois
-> Engagement : 12 mois | Pas de préavis" """

        if "Self'in" in upsell:
            selfin_template = """
TEMPLATE SELF'IN OBLIGATOIRE dans l'email :
"Comme évoqué, voici le lien pour lancer votre test Self'in, fonctionnalité gratuite :
👉 Le concept : 10 publications ultra-personnalisées basées sur votre réalité de terrain
👉 Votre seule action : remplir ce questionnaire de 3 minutes et envoyer une photo : https://forms.fillout.com/t/hdEdvdk4wrus
👉 Le résultat : l'IA génère des visuels authentiques qui renforcent le lien avec vos clients
Rien ne sera publié sans votre validation." """

        prompt = f"""{ARTURIN_CONTEXT}

MISSION 2 — EMAIL DE SUIVI
Prénom client : {prenom}
CS : {cs or "[Ton prénom]"}
Contenu call/CR : {content}
{f"Upsell évoqué : {upsell}" if upsell else "Aucun upsell"}

Objet : "Artur'in - Suivi de notre appel"

Génère l'email avec :
1. Mini-résumé chaleureux avec détail humain/personnel du call
2. Récapitulatif des points importants + coaching mentionné
{f"3. Proposition naturelle pour {upsell}" if upsell else "3. Pas de proposition commerciale"}
{site_web_template}
{selfin_template}
4. Si pertinent : mention d'un sujet pour le prochain call
5. Bonne journée + signature {cs or "[Ton prénom]"}

TONALITÉ : clarté, simplicité, bienveillance, proximité. Humain et professionnel. Pas de jargon.
SORTIE : uniquement l'email final prêt à envoyer, rien d'autre."""

        result = call_groq(prompt)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/mission3", methods=["POST"])
def mission3():
    try:
        body = request.json
        transcription = body.get("transcription", "")
        context = body.get("context", "")

        prompt = f"""{ARTURIN_CONTEXT}

MISSION 3 — COACHING POST-CALL
{f"Contexte : {context}" if context else ""}
Transcription : {transcription}

Tu es un conseiller stratégique personnel : QI 180, direct, lucide, sans complaisance. Expert en psychologie, vente, stratégie. Zéro excuse, orientation résultat.

Fournis :

MÉTRIQUES (0 à 10) :
-> Découverte & qualification : [score/10]
-> Argumentaire & valeur : [score/10]
-> Closing & next step : [score/10]

VÉRITÉ BRUTE :
-> 2 à 3 erreurs critiques avec extraits/citations exactes du call
-> 1 à 2 points positifs factuels

UPSELL PRIORITAIRE :
-> Upsell identifié
-> Triggers observés (citations du call)
-> Pitch 20 secondes
-> 2 phrases à tester au prochain call"""

        result = call_groq(prompt)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "Artur'in Agent CS — Backend Groq"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
