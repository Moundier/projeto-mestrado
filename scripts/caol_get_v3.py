import json
import re
from pathlib import Path

import requests

# todos os caols de 02/06/2024 ate 02/06/2026

TOKEN_URL = "https://oauth2.pnip.com.br/realms/pnip-homologacao/protocol/openid-connect/token"
API_URL = "https://api.hmg.pnip.com.br/servico-terceiros/caol/find/by/uuid/{uuid}"

CLIENT_ID = "lupa_data"
CLIENT_SECRET = "CZb1RAqgcazMOMJYrCOQU5s5laRfO4l2"

UUID_FILE = "caol_requests_all_uuids.txt"
OUTPUT_DIR = "results"


def get_token() -> str:
    response = requests.post(
        TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def load_uuids(path: str) -> list[str]:
    uuids = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            uuids.append(re.sub(r'^"|"$', "", line))

    return uuids


def fetch_uuid(token: str, uuid: str) -> dict:
    response = requests.get(
        API_URL.format(uuid=uuid),
        headers={"Authorization": f"Bearer {token}"},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def main():
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    uuids = load_uuids(UUID_FILE)
    total = len(uuids)

    print(f"Loaded {total} UUIDs")

    for index, uuid in enumerate(uuids):
        if index < 285: 
            continue
        filename = f"{index:06d}_{uuid}.json"
        output_file = output_dir / filename

        if output_file.exists():
            print(f"[{index + 1}/{total}] Already exists: {filename}")
            continue

        try:
            print(f"[{index + 1}/{total}] Getting token...")
            token = get_token()

            print(f"[{index + 1}/{total}] Fetching {uuid}")
            data = fetch_uuid(token, uuid)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"[{index + 1}/{total}] Saved {filename}")

        except Exception as e:
            print(f"[{index + 1}/{total}] Failed {uuid}: {e}")

    print("Done.")


if __name__ == "__main__":
    main()