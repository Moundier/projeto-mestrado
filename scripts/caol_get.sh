
TOKEN=$(curl -s \
  --request POST \
  --url "https://oauth2.pnip.com.br/realms/pnip-homologacao/protocol/openid-connect/token" \
  --header "Content-Type: application/x-www-form-urlencoded" \
  --data "grant_type=client_credentials" \
  --data "client_id=lupa_data" \
  --data "client_secret=CZb1RAqgcazMOMJYrCOQU5s5laRfO4l2" \
| jq -r .access_token)

curl \
  -H "Authorization: Bearer $TOKEN" \
  "https://api.hmg.pnip.com.br/servico-terceiros/caol/find/by/uuid/$UUID"

curl -i \
  -H "Authorization: Bearer $TOKEN" \
  "https://api.hmg.pnip.com.br/servico-terceiros/caol/find-all"

# 1. Lista uma solicitação de certificação CAOL por UUID GET 
# https://api.hmg.pnip.com.br/servico-terceiros/caol/find/by/uuid/{uuid} 
# 2. Lista todas as certificações de CAOL GET 
# https://api.hmg.pnip.com.br/servico-terceiros/caol/find-all