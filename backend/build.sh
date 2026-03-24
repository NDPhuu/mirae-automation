# Script to build on Render
set -o errexit

# Install poetry
pip install poetry

# Install dependencies using poetry
poetry install --no-dev

# Ensure we use CPU version of torch to save space/memory if needed
# (though pyproject.toml already specifies it)
