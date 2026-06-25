
TOKEN=$(curl -s \
  --request POST \
  --url "https://oauth2.pnip.com.br/realms/pnip-homologacao/protocol/openid-connect/token" \
  --header "Content-Type: application/x-www-form-urlencoded" \
  --data "grant_type=client_credentials" \
  --data "client_id=lupa_data" \
  --data "client_secret=CZb1RAqgcazMOMJYrCOQU5s5laRfO4l2" \
| jq -r .access_token)

UUID="987b90a2-b8e8-4311-96ce-d3a46ee285e2"

curl \
  -H "Authorization: Bearer $TOKEN" \
  "https://api.hmg.pnip.com.br/servico-terceiros/caol/find/by/uuid/$UUID"

# curl -i \
#   -H "Authorization: Bearer $TOKEN" \
#   "https://api.hmg.pnip.com.br/servico-terceiros/caol/find-all"

