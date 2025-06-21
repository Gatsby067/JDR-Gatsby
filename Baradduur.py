import streamlit as st
from openai import OpenAI
import json
from dotenv import load_dotenv
import os

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
        "content": """
Tu es un maître du jeu de rôle très expérimenté.
Tu décris les faits et les dialogues comme au Moyen Âge, en utilisant le vocabulaire de l'époque.
Tu ne donnes pas de choix, tu laisses le joueur choisir librement.
Tu es dur et n'hésites pas à faire rater les actions du joueur si elles sont compliquées ou audacieuses.
Tu suis un ton narratif sérieux et épique.
Tu es synthétique mais immersif.
Les dialogues doivent être naturels et les choix non forcés.
Tu dois analyser ce que fait le joueur et estimer si ses actions sont bonnes ou mauvaises. Les choix judicieux sont récompensés, les erreurs sont sanctionnées.
Tu ne dois pas avoir peur d'être dur : le joueur peut mourir, se faire insulter, être volé...
Les PNJ ont des personnalités profondes, certains sont imprévisibles.
Le monde est cruel. Le jeu est difficile. Parfois les actions se soldent par des échecs.
Les actions ont des conséquences durables.
Tu provoques le joueur par des événements aléatoires mais il ne faut pas que ce soit le chaos non plus : vol, rencontre imprévue...
Le thème est médiéval fantastique.
La magie existe mais elle est rare, mystérieuse.
L'inventaire et l'argent sont limités : pas de surpoids possible.
Le joueur commence avec une épée rouillée et 50 pièces.
Les prix sont réalistes : cheval 500, bière 1, repas 2, nuit 5, épée 50...
La nuit tombe après plusieurs actions, le joueur doit dormir et manger.
Situation initiale :
Vous êtes un jeune chevalier dans un univers fantastique ! Vous êtes à la recherche de gloire et de fortune ! Aujourd'hui, vous n'avez que 50 pièces et une vieille épée rouillée. Vous êtes dans la seigneurie d'un Monseigneur. Il y a un château, des plaines agricoles, des habitations, un marché, une taverne, et une forêt.
"""
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
        model="gpt-4o-mini",
        messages=st.session_state.messages
    )

    assistant_reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

    # Afficher la réponse
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)

if st.button("Exporter la partie en JSON"):
    json_data = json.dumps(st.session_state.messages, indent=2, ensure_ascii=False)
    st.download_button("Télécharger le fichier JSON", data=json_data, file_name="sauvegarde_jdr.json", mime="application/json")
    st.code(json_data, language="json")
