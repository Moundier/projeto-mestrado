import json
from pathlib import Path

import requests

TOKEN_URL = "https://oauth2.pnip.com.br/realms/pnip-homologacao/protocol/openid-connect/token"

CAOL_BY_UUID_URL = "https://api.hmg.pnip.com.br/servico-terceiros/caol/find/by/uuid/{uuid}"
CAOL_FIND_ALL_URL = "https://api.hmg.pnip.com.br/servico-terceiros/caol/find-all"

CLIENT_ID = "lupa_data"
CLIENT_SECRET = "CZb1RAqgcazMOMJYrCOQU5s5laRfO4l2"
UUID = "987b90a2-b8e8-4311-96ce-d3a46ee285e2"


def get_access_token() -> str:
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


def fetch_caol_request(uuid: str, token: str) -> dict:
    response = requests.get(
        CAOL_BY_UUID_URL.format(uuid=uuid),
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def fetch_all_caol_requests(token: str) -> list[dict]:
    response = requests.get(
        CAOL_FIND_ALL_URL,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def main():
    token = get_access_token()

    data = fetch_all_caol_requests(token)

    output_file = Path("./assets/caol_requests.json")

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    main()

# def main():
#     token = get_access_token()
#     data = fetch_caol_request(UUID, token)

#     output_file = Path(f"caol_certification_request_{UUID}.json")

#     with output_file.open("w", encoding="utf-8") as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)

#     print(f"Saved to: {output_file}")


# if __name__ == "__main__":
#     main()



