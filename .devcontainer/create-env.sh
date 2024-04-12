#!/bin/bash

# Ask the user for the API key
echo "Please enter your API key:"
read -s APIKEY

# Create the .env file with the API key
echo "Creating .env file..."
echo "APIKEY=$APIKEY" > .env
echo ".env file created successfully."

# Optional: Inform the user to restart their terminal or source the .env
echo "Please run 'source .env' to load the environment variables, or restart your terminal."
