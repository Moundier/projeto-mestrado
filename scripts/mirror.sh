USER="casanova"
HOST="192.168.0.18"

rsync -avz \
  "/home/$USER/Public/projeto-mestrado/" \
  "$USER@$HOST:/home/$USER/Public/projeto-mestrado/"