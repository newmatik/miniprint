#!/bin/bash

# Define the path to the .env file. This assumes that the .devcontainer directory
# is at the root of your project structure.
ENV_PATH="../.env"

# Create or clear the .env file
echo "Creating or clearing .env file..."
echo "" > $ENV_PATH

# Append environment variables to the .env file
echo "APIKEY=testapikey145" >> $ENV_PATH
echo "FLASK_APP=app.py" >> $ENV_PATH
echo "FLASK_ENV=development" >> $ENV_PATH
echo "FLASK_RUN_HOST=0.0.0.0" >> $ENV_PATH
echo "FLASK_RUN_PORT=5500" >> $ENV_PATH
echo ".env file created successfully."

# Optional: Inform the user to restart their terminal or source the .env
echo "Please run 'source $ENV_PATH' to load the environment variables, or restart your terminal."
