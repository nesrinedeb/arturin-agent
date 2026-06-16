from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app, origins=["*"])

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-70b-versatile"

ARTURIN_CONTEXT = """Tu es un assistant interne pour l'équipe Customer Success d'Artur'in.
Artur'in est une plateforme de communication digitale pour les professionnels locaux (agents immobiliers, opticiens, assureurs, pharmaciens, dentistes, avocats, notaires, experts-comptables, coaches sportifs, garagistes...).
Produits Artur'in : publications réseaux sociaux automatisées, newsletter, Seeble (prospection LinkedIn automatisée), Shoot'in (photos pro 30€/mois), Boost'in (publicité Google/Meta dès 50€/mois), site web (295€HT + 70€HT/mois), Multi-sites (59€/établissement), Self'in (gratuit, 10 publications IA personnalisées).
Renouvellement Essilor : UNIQUEMENT pour les opticiens — 1200€/6 mois ou 2400€/12 mois + Shoot'in offert."""

def call_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Tu es un assistant Customer Success pour Artur'in. Tu génères des comptes-rendus de calls internes, structurés et prêts à copier dans Salesforce. Tu respectes EXACTEMENT les formats demandés sans jamais t'en écarter."
            },
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2000,
        "temperature": 0.2
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

MISSION : Génère un compte-rendu de call INTERNE, synthétique, prêt à copier dans Salesforce.

CLIENT : {client}
{f"CONTEXTE SUPPLÉMENTAIRE : {context}" if context else ""}
TRANSCRIPTION DU CALL : {transcription}

RÈGLES ABSOLUES — si tu ne les respectes pas, le CR est inutilisable :
1. Chaque puce ➤ doit être sur sa PROPRE ligne — JAMAIS deux ➤ sur la même ligne horizontale
2. Titres de section en MAJUSCULES avec émoji — sans numéro, sans point
3. Utilise "je" pour les actions du CS (ex: "j'ai proposé", "je vais envoyer")
4. ZÉRO description de produit — l'équipe connaît déjà tout
5. Données brutes uniquement : chiffres, citations, décisions concrètes
6. NE PAS suivre l'ordre chronologique — regroupe par thèmes logiques
7. Maximum 2-3 puces ➤ par thématique
8. IMPORTANT : le texte doit être propre, sans balises, sans numéros de source

GÉNÈRE CE FORMAT EXACT :

────────────────────
{client} — Compte-rendu

🔜 A VOIR AU PROCHAIN CALL
[Liste les points précis à creuser/vérifier au prochain call. Si rien de spécifique : RAS]
[Si pertinent, sur une ligne séparée : suggestion d'upsell en max 100 caractères]

🔋 RÉSUMÉ EXPRESS
[3-5 phrases : qui est le client + ce qu'on a fait ensemble + ce qui reste à faire + ton à garder pour le prochain call]

👤 PROFIL DU CLIENT
➤ [Prénom exact de l'interlocuteur trouvé dans la transcription], [Métier/Rôle/Localisation], humeur : [3 adjectifs précis qui reflètent vraiment le call]
➤ Niveau digital : [Faible/Moyen/Bon selon ce qu'on observe] | État du commerce : [situation business concrète mentionnée]

📝 POINTS DISCUTÉS

[NOM DU PREMIER THÈME EN MAJUSCULES]
➤ [donnée brute ou citation courte]
➤ [donnée brute ou citation courte]
➤ [donnée brute ou citation courte si nécessaire]

[NOM DU DEUXIÈME THÈME EN MAJUSCULES]
➤ [donnée brute ou citation courte]
➤ [donnée brute ou citation courte]

[NOM DU TROISIÈME THÈME EN MAJUSCULES si nécessaire]
➤ [donnée brute ou citation courte]

[❤️ suivi d'une anecdote humaine ou personnelle UNIQUEMENT si le client en a parlé explicitement]

🤝 UPSELL ET SOLUTIONS PRÉSENTÉES
[Si un upsell a été présenté ou discuté : décris-le en 2-3 phrases avec la réaction du client. Sinon : RAS]

────────────────────
📍 ACTIONS A FAIRE
➤ [Action précise et immédiate que le CS doit faire]
➤ [Autre action si nécessaire]

────────────────────
💬 FEEDBACK PRODUIT
[Si le client a donné des retours sur les produits Artur'in, liste-les ainsi :]
Insatisfaction : [nom du produit] — [ce qui ne va pas, max 100 caractères]
Suggestion : [nom du produit] — [ce qu'il propose, max 100 caractères]
Satisfaction : [nom du produit] — [ce qui plaît, max 100 caractères]
[Si aucun feedback produit : omettre cette section]"""

        result = call_groq(prompt)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"MISSION1 ERROR: {str(e)}")
        print(f"TRACEBACK: {error_details}")
        return jsonify({"success": False, "error": str(e), "trace": error_details}), 500

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
Intègre ce bloc OBLIGATOIREMENT dans l'email si site web proposé :
---
Comme convenu, voici la présentation de notre accompagnement site internet.
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
-> Engagement : 12 mois | Pas de préavis
---"""

        if "Self'in" in upsell:
            selfin_template = """
Intègre ce bloc OBLIGATOIREMENT dans l'email si Self'in proposé :
---
Comme évoqué, voici le lien pour lancer votre test Self'in, fonctionnalité gratuite :
👉 Le concept : 10 publications ultra-personnalisées basées sur votre réalité de terrain
👉 Votre seule action : remplir ce questionnaire de 3 minutes et envoyer une photo : https://forms.fillout.com/t/hdEdvdk4wrus
👉 Le résultat : l'IA génère des visuels authentiques qui renforcent le lien avec vos clients
Rien ne sera publié sans votre validation.
---"""

        prompt = f"""{ARTURIN_CONTEXT}

MISSION : Rédige un email de suivi professionnel suite à un call client Artur'in.

PRÉNOM DU CLIENT : {prenom}
CS QUI ENVOIE : {cs or "Nesrine"}
CONTENU DU CALL / CR : {content}
{f"UPSELL ÉVOQUÉ : {upsell}" if upsell else ""}

VOICI LE STYLE D'EMAIL ATTENDU CHEZ ARTUR'IN — respecte exactement ce ton et cette structure :

Exemple 1 (suivi + proposition) :
"Bonjour Nicole, bonjour David,
Merci pour votre temps lors de notre échange ce matin.
Comme évoqué, les publications réalisées sur vos réseaux sociaux permettent d'assurer une présence régulière et professionnelle de l'agence. En revanche, si l'objectif est d'augmenter davantage votre visibilité auprès de nouvelles personnes, les publications seules ont naturellement leurs limites puisqu'elles sont principalement vues par les personnes qui vous suivent déjà.
Pour toucher une audience plus large, il est possible de mettre en place des campagnes publicitaires sur Facebook et Instagram. Mon conseil serait de réaliser un premier test avec un budget modéré afin de mesurer concrètement les résultats.
N'hésitez pas à revenir vers moi après avoir fait le point ensemble. Je reste bien entendu disponible si vous avez la moindre question.
Je vous souhaite une excellente journée.
Bien cordialement,
[Prénom] — Customer Success Coach — Artur'In"

Exemple 2 (suivi simple) :
"Bonjour Quentin,
Suite à notre échange, je vous fais un récapitulatif des éléments abordés.
[Récapitulatif factuel et neutre des points discutés]
Je vous laisse revenir vers moi dès que vous aurez pu avancer de votre côté.
Bien entendu, nous restons à votre disposition pour toute question complémentaire.
Nesrine — Customer Success Coach — Artur'In"

RÈGLES ABSOLUES :
1. JAMAIS de citations ou mots exacts du client dans l'email
2. JAMAIS de mention des plaintes, insatisfactions ou erreurs passées
3. JAMAIS de formulations dramatiques ou d'empathie excessive
4. Rester factuel, neutre et orienté solutions/actions
5. Maximum 4-5 lignes par paragraphe
6. Terminer TOUJOURS par : [Prénom CS] — Customer Success Coach — Artur'In
7. Formule de politesse : "Bien cordialement" ou "À bientôt"

{site_web_template}
{selfin_template}

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

MISSION : Coaching post-call — analyse honnête et sans complaisance de la performance du CS.

{f"CONTEXTE : {context}" if context else ""}
TRANSCRIPTION : {transcription}

Tu es un conseiller stratégique d'élite : direct, lucide, sans complaisance. Expert en vente, psychologie client, gestion de churn. Zéro excuse, orientation résultat.

GÉNÈRE EXACTEMENT CE FORMAT :

MÉTRIQUES DE PERFORMANCE
-> Découverte & qualification : [X]/10 — [justification en 1 phrase]
-> Argumentaire & valeur : [X]/10 — [justification en 1 phrase]
-> Closing & next step : [X]/10 — [justification en 1 phrase]

ERREURS CRITIQUES
1. [Erreur critique avec citation exacte du call entre guillemets]
2. [Erreur critique avec citation exacte du call entre guillemets]
3. [Erreur critique si applicable]

POINTS POSITIFS
1. [Point positif factuel avec exemple du call]
2. [Point positif factuel si applicable]

UPSELL PRIORITAIRE
-> Upsell identifié : [nom du produit]
-> Pourquoi maintenant : [triggers observés avec citations du call]
-> Pitch 20 secondes : [pitch direct et percutant]
-> 2 phrases à tester : 
   • [Phrase 1]
   • [Phrase 2]"""

        result = call_groq(prompt)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/test", methods=["GET"])
def test():
    try:
        result = call_groq("Réponds uniquement : OK")
        return jsonify({"success": True, "result": result, "key_set": bool(GROQ_API_KEY)})
    except Exception as e:
        import traceback
        return jsonify({"success": False, "error": str(e), "trace": traceback.format_exc(), "key_set": bool(GROQ_API_KEY)}), 500

@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "Artur'in Agent CS — Backend Groq v2"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
