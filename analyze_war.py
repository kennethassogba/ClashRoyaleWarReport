"""
Fetches Clash Royale war data, analyzes player performance, generates a banner
for the winner, and posts a summary to a Discord webhook.
"""

import json
import os
from io import BytesIO
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from huggingface_hub import InferenceClient

# --- Configuration ---
CLASH_API_TOKEN = os.environ.get("CLASH_API_TOKEN")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
HF_TOKEN = os.environ.get("HF_TOKEN")
CLAN_TAG = "#LLJ8LYRP"
CLAN_URL = "https://royaleapi.com/clan/LLJ8LYRP/war/analytics"
HUGGING_FACE_MODEL = "black-forest-labs/FLUX.1-dev"

# --- Validate Configuration ---
if not all([CLASH_API_TOKEN, DISCORD_WEBHOOK_URL, HF_TOKEN]):
    missing = [
        name
        for name, var in {
            "CLASH_API_TOKEN": CLASH_API_TOKEN,
            "DISCORD_WEBHOOK_URL": DISCORD_WEBHOOK_URL,
            "HF_TOKEN": HF_TOKEN,
        }.items()
        if not var
    ]
    raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

# --- API Clients ---
huggingface_client = InferenceClient(provider="auto", api_key=HF_TOKEN)


def _clash_royale_api_get(endpoint: str) -> Dict[str, Any]:
    """Helper to make GET requests to the Clash Royale API."""
    url = f"https://api.clashroyale.com/v1/{endpoint}"
    headers = {"Authorization": f"Bearer {CLASH_API_TOKEN}"}
    response = requests.get(url, headers=headers)
    if not response.ok:
        print(f"API Error: {response.status_code}")
        raise RuntimeError(f"API Response Body: {response.text}")
    return response.json()


def fetch_war_data() -> List[Dict[str, Any]]:
    """Fetches the river race log for the clan."""
    encoded_clan_tag = CLAN_TAG.replace("#", "%23")
    data = _clash_royale_api_get(f"clans/{encoded_clan_tag}/riverracelog")
    return data.get("items", [])


def get_player_deck(player_tag: str) -> List[str]:
    """Fetches the current deck for a given player."""
    encoded_player_tag = player_tag.replace("#", "%23")
    try:
        data = _clash_royale_api_get(f"players/{encoded_player_tag}")
        cards = data.get("currentDeck", [])
        return [c["name"] for c in cards]
    except RuntimeError:
        print(f"Could not fetch deck for player {player_tag}. Skipping banner.")
        return []


def generate_banner(player_name: str, deck: List[str]) -> Optional[bytes]:
    """Generates a banner image using Hugging Face Inference API."""
    deck_str = ", ".join(deck)
    prompt = (
        f"A cinematic epic fantasy banner celebrating the Clash Royale winner named \"{player_name}\". "
        f"Depict a dynamic battle arena scene featuring characters like {deck_str}, with cinematic lighting and photorealistic textures blended with subtle painterly brushwork. "
        "Do NOT look like an AI-generated image: avoid obvious digital artifacts, repetitive patterns, or synthetic textures. No watermarks or signatures. "
        "Render the player's name prominently \"{player_name}\" and legibly as an integrated element of the scene."
        "Render the clan's name prominently \"CCPOM\" and legibly as an integrated element of the scene."
        "High detail, natural anatomy, realistic lighting, shallow depth of field, slight film grain, victory atmosphere."
    )
    print(prompt)

    try:
        image = huggingface_client.text_to_image(prompt, model=HUGGING_FACE_MODEL)
        with BytesIO() as buffer:
            image.save(buffer, format="PNG")
            return buffer.getvalue()
    except Exception as e:
        print(f"Erreur generation image : {e}")
        return None


def send_to_discord(message: str, image_bytes: Optional[bytes] = None) -> None:
    """Sends a message and an optional image to the Discord webhook."""
    if image_bytes:
        files = {"file": ("banner.png", image_bytes, "image/png")}
        payload_json = json.dumps({"content": message})
        response = requests.post(
            DISCORD_WEBHOOK_URL, data={"payload_json": payload_json}, files=files
        )
    else:
        response = requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

    if not response.ok:
        print(f"API Error sending to Discord: {response.status_code}")
        raise RuntimeError(f"API Response Body: {response.text}")


def process_war_data(war_items: List[Dict[str, Any]]) -> pd.DataFrame:
    """Processes war data to calculate scores and averages for each player."""
    history: Dict[str, Dict[str, Any]] = {}
    recent_wars = war_items[:4]

    for i, war in enumerate(recent_wars):
        for standing in war.get("standings", []):
            clan = standing.get("clan", {})
            if clan.get("tag") == CLAN_TAG:
                for p in clan.get("participants", []):
                    if p["fame"] > 0:
                        tag = p["tag"]
                        if tag not in history:
                            history[tag] = {"name": p["name"], "scores": [0] * 4}
                        history[tag]["scores"][i] = p["fame"]

    if not history:
        return pd.DataFrame()

    data = [
        {
            "tag": tag,
            "name": info["name"],
            "last_war": info["scores"][0],
            "avg": sum(info["scores"]) / len(info["scores"]),
        }
        for tag, info in history.items()
    ]
    return pd.DataFrame(data)


def format_leaderboard_message(
    top_5_last: pd.DataFrame, top_5_avg: pd.DataFrame
) -> str:
    """Formats the leaderboard message for Discord."""
    message_lines = ["Bravo à tous pour vos efforts en guerre de clan !", ""]

    message_lines.append("**TOP 5 - DERNIÈRE GUERRE**")
    for i, (_, row) in enumerate(top_5_last.iterrows(), 1):
        message_lines.append(f"{i}. {row['name']} — {int(row['last_war'])} pts")

    message_lines.append("")
    message_lines.append("**TOP 5 - MOYENNE GLISSANTE (4 SEMAINES)**")
    for i, (_, row) in enumerate(top_5_avg.iterrows(), 1):
        message_lines.append(f"{i}. {row['name']} — {row['avg']:.0f} pts/semaine")

    message_lines.append("")
    message_lines.append(f"Retrouvez le classement complet ici : {CLAN_URL}")

    return "\n".join(message_lines)


def main() -> None:
    """Main function to run the analysis and post to Discord."""
    war_items = fetch_war_data()
    if not war_items:
        print("No war data found. Exiting.")
        return

    df = process_war_data(war_items)
    if df.empty:
        print("No participant data found. Exiting.")
        return

    top_5_last = df.sort_values(by="last_war", ascending=False).head(5)
    top_5_avg = df.sort_values(by="avg", ascending=False).head(5)

    winner = top_5_last.iloc[0]
    deck = get_player_deck(winner["tag"])
    image_bytes = generate_banner(winner["name"], deck) if deck else None

    message = format_leaderboard_message(top_5_last, top_5_avg)

    send_to_discord(message, image_bytes)
    print("Report sent to Discord successfully.")


if __name__ == "__main__":
    main()
