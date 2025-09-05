# Poetry Setup and Usage Guide

This guide provides instructions on how to set up and manage project dependencies using Poetry.

## 1. Install Poetry

If you don't have Poetry installed, follow the official installation instructions for your operating system:

*   **macOS / Linux / WSL:**
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```
*   **Windows (PowerShell):**
    ```powershell
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    ```
    After installation, you might need to add Poetry to your PATH. Follow the instructions provided by the installer.

## 2. Project Setup

This project is already configured with a `pyproject.toml` file.

### Install Dependencies

Navigate to the project root directory in your terminal and run:

```bash
poetry install
```

This command will:
*   Read the `pyproject.toml` file.
*   Resolve all dependencies and their sub-dependencies.
*   Create a `poetry.lock` file (if it doesn't exist or is outdated), which pins the exact versions of all dependencies.
*   Create a virtual environment for your project (if one doesn't exist).
*   Install all dependencies into the virtual environment.

### Activate Virtual Environment

To activate the virtual environment managed by Poetry, run:

```bash
poetry shell
```
You can then run Python commands directly (e.g., `python app/main.py`).

### Run Commands Without Activating Shell

You can also run commands within the Poetry-managed virtual environment without explicitly activating the shell:

```bash
poetry run <your_command_here>
# Example:
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
poetry run pytest
```

## 3. Managing Packages

### Add a New Package

To add a new package to your project, use `poetry add`:

```bash
poetry add <package-name>
# Example: poetry add httpx

# Add with a specific version constraint:
poetry add <package-name>@^1.2.3 # Adds version >=1.2.3 <2.0.0
poetry add <package-name>@==1.2.3 # Adds exact version 1.2.3
poetry add <package-name>@">=1.2.3,<1.3.0" # Adds a version range

# Add a development dependency (e.g., for testing or linting):
poetry add --group dev <package-name>
# Example: poetry add --group dev black
```
After adding a package, Poetry will automatically update `pyproject.toml` and `poetry.lock`.

### Remove a Package

To remove a package, use `poetry remove`:

```bash
poetry remove <package-name>
# Example: poetry remove httpx

# Remove a development dependency:
poetry remove --group dev <package-name>
```
Poetry will update `pyproject.toml` and `poetry.lock`.

### Update Packages

To update all packages to their latest compatible versions (based on `pyproject.toml` constraints):

```bash
poetry update
```

To update a specific package:

```bash
poetry update <package-name>
# Example: poetry update fastapi
```

### Exporting Dependencies (e.g., for Dockerfiles)

While Poetry manages dependencies internally, you might need a `requirements.txt` style file for environments that don't have Poetry installed (e.g., some CI/CD pipelines or Docker builds).

To export a `requirements.txt` file from your `poetry.lock`:

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```
**Note:** For Docker builds, it's often more efficient to install dependencies directly with Poetry inside the Dockerfile.

## 4. Dockerfile Integration (Future Step)

Once you are ready to update your Dockerfiles to use Poetry, you will modify `deployment/Dockerfile.app` and `deployment/Dockerfile.worker` as follows:

```dockerfile
# ... (previous Dockerfile content) ...

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry
# --no-dev: Do not install development dependencies
# --no-root: Do not install the project itself as an editable package
RUN poetry install --no-dev --no-root

# ... (rest of your Dockerfile content) ...
```
Remember to adjust the `COPY` commands based on where `pyproject.toml` and `poetry.lock` are relative to your Docker build context.
