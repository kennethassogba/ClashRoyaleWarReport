import requests
import pandas as pd
from dotenv import dotenv_values

# Configuration
# Load environment variables from .env file
env_vars = dotenv_values() 
API_TOKEN = env_vars.get('API_TOKEN')
WEBHOOK_URL = env_vars.get('WEBHOOK_URL')
CLAN_TAG = "%23LLJ8LYRP" # Le # doit être encodé en %23
CLAN_URL = "https://royaleapi.com/clan/LLJ8LYRP/war/analytics"

if not API_TOKEN:
    print("Error: API_TOKEN not found in .env file. Please create a .env file with API_TOKEN='YOUR_API_TOKEN_HERE'.")
    raise SystemExit()
    # exit or raise an exception here

if not WEBHOOK_URL:
    print("Error: WEBHOOK_URL not found in .env file. Please create a .env file with WEBHOOK_URL='DISCORD_SERVER_WEBHOOK_URL'.")
    raise SystemExit()
    # exit or raise an exception here

def send_to_discord(message):
    payload = {"content": message}
    requests.post(WEBHOOK_URL, json=payload)

def fetch_war_data():
    url = f"https://api.clashroyale.com/v1/clans/{CLAN_TAG}/riverracelog"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        print(f"Erreur API : {response.status_code}")
        print(f"API Response Body: {response.text}") # Added to show full response
        return None

def analyze_and_post():
    items = fetch_war_data()
    if not items:
        return

    # Extraction des données des 4 dernières guerres
    history = {}

    # On itère sur les 4 dernières entrées du log
    recent_wars = items[:4]

    for i, war in enumerate(recent_wars):
        for participant in war.get('standings', []):
            clan = participant.get('clan', {})
            if clan.get('tag') == "#LLJ8LYRP":
                for p in clan.get('participants', []):
                    tag = p['tag']
                    name = p['name']
                    fame = p['fame']

                    if tag not in history:
                        history[tag] = {'name': name, 'scores': [0, 0, 0, 0]}
                    history[tag]['scores'][i] = fame

    # Transformation en DataFrame pour calculs
    data = []
    for tag, info in history.items():
        data.append({
            'name': info['name'],
            'last_war': info['scores'][0],
            'avg': sum(info['scores']) / 4
        })

    df = pd.DataFrame(data)

    # 1. Top 5 Dernière Guerre
    top_5_last = df.sort_values(by='last_war', ascending=False).head(5)

    # 2. Top 5 Moyenne 4 semaines
    top_5_avg = df.sort_values(by='avg', ascending=False).head(5)

    # Message
    message = "Bravo à tous pour vos efforts en guerre de clan !\n\n"

    message += "**TOP 5 - DERNIÈRE GUERRE**\n"
    for i, (_, row) in enumerate(top_5_last.iterrows(), 1):
        message += f"{i}. {row['name']} — {int(row['last_war'])} pts\n"

    message += "\n**TOP 5 - MOYENNE GLISSANTE (4 SEMAINES)**\n"
    for i, (_, row) in enumerate(top_5_avg.iterrows(), 1):
        message += f"{i}. {row['name']} — {row['avg']:.0f} pts/semaine\n"

    message += f"\nRetrouvez le classement complet ici : {CLAN_URL}"

    send_to_discord(message)

if __name__ == "__main__":
    analyze_and_post()
