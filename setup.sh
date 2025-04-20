#!/bin/bash

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# Install pre-commit hooks
pre-commit install

echo "Setup complete! Virtual environment activated."
echo "To deactivate the virtual environment, run: deactivate" 