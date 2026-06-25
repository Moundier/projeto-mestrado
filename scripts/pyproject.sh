#!/usr/bin/env python3

find ./ -type d -exec touch {}/__init__.py \;
# find ./ -type f -name "__init__.py" -delete

# python -m venv venv
# source venv/bin/activate
# sudo python3 main.py

# echo "Cleaning Python cache..."
# find . -type d -name "__pycache__" -prune -exec rm -rf {} +
# find . -type f -name "*.pyc" -delete
# echo "Done."