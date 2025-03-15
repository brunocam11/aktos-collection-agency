#!/bin/bash

# Clean up any previous coverage data
coverage erase

# Run the tests with coverage
coverage run --source=accounts manage.py test accounts

# Generate a terminal report
echo -e "\n\nCoverage Report:"
coverage report -m