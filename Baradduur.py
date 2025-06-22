import streamlit as st
from openai import OpenAI
import json
from dotenv import load_dotenv
import os

regles = """Tu es un maître du jeu de rôle médiéval-fantastique, dur et expérimenté. L'univers est sombre, cruel, inspiré du Moyen Âge, avec un ton narratif sérieux, synthétique et immersif.

Les dialogues utilisent un vocabulaire d’époque. Tu ne poses pas de questions, tu laisses le joueur libre. Tu ne parles jamais à sa place.

Tu analyses les choix du joueur : bonnes décisions récompensées, erreurs punies. Échecs fréquents, parfois fatals. Les conséquences sont durables.

La trahison, la violence, les PNJ imprévisibles et les événements imprévus sont fréquents, mais cohérents.

Le joueur débute avec une épée rouillée et 50 pièces. Il a un inventaire limité (surpoids interdit). Les prix sont réalistes : cheval 500, repas 2, nuit 5, bière 1...

Tu dois parfois proposer des dilemmes ou énigmes mais pas en permanence.

La magie existe, rare et mystérieuse, jamais omniprésente.

Les jours passent selon les actions. La faim et la fatigue existent.

L’univers évolue : les informations passées peuvent résoudre des situations futures.

Ne rends pas le jeu répétitif ni trop généreux.

Situation initiale :
Vous êtes un jeune chevalier à la recherche de gloire et de fortune. Vous arrivez dans la seigneurie d’un Monseigneur, armé de votre épée rouillée et de 50 pièces. On y trouve un château, des plaines agricoles, des habitations, un marché, une taverne et une forêt.
"""

load_dotenv()  # charge les variables du fichier .env

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

st.title("Baradduur")

# --- Charger une sauvegarde JSON si elle existe ---
uploaded_file = st.file_uploader("📂 Charger une sauvegarde", type="json")
if uploaded_file:
    sauvegarde = json.load(uploaded_file)
    st.session_state.messages = sauvegarde
    st.success("✅ Sauvegarde chargée ! Vous pouvez reprendre la partie.")

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system",
        "content": regles
    }]

# Afficher les anciens messages (sauf le system)
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Saisie utilisateur
user_input = st.chat_input("Entrez votre action...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=st.session_state.messages
    )

    assistant_reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

    # Afficher la réponse
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)

if len(st.session_state.messages) > 20:
    résumé = client.chat.completions.create(
        model="gpt-4o",
        messages=st.session_state.messages[:-10] + [{"role": "user", "content": "Résume les événements en actualisant ces éléments au résumé précedent : les pièces d'or, les objets, les actions éffectuées, les personnages, leurs caractères et les actions effectuées avec, les lieux visités, les détails important pour la suite"}]
    ).choices[0].message.content

    st.session_state.messages = [
        {"role": "system", "content": regles},
        {"role": "assistant", "content": f"Résumé de la situation : {résumé}"}
    ] + st.session_state.messages[-10:]


# --- BOUTON POUR TÉLÉCHARGER LA SAUVEGARDE EN JSON ---
json_data = json.dumps(st.session_state.messages, indent=2, ensure_ascii=False)
st.download_button(
    label="📥 Télécharger la sauvegarde",
    data=json_data,
    file_name="sauvegarde_jdr.json",
    mime="application/json"
)

