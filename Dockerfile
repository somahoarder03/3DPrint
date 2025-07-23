# syntax=docker/dockerfile:1.4
# (Optional) Specify Dockerfile syntax for BuildKit features like 'AS'

# Stage 1: Builder Stage
# This stage contains all the tools and dependencies needed to build your Python packages,
# especially those with C extensions (like NumPy, which needs a C compiler).
FROM python:3.11-slim-bookworm AS builder

# Set the working directory for this stage
WORKDIR /app

# Copy only the requirements file first to leverage Docker's build cache.
# If only the requirements.txt changes, this step and subsequent ones will be re-run.
COPY requirements.txt .

# Install system-level build dependencies. These are usually heavy and not needed at runtime.
# - build-essential: Provides GCC, g++, make, etc.
# - libgl1-mesa-glx, libglib2.0-0, libjpeg-dev, zlib1g-dev, libopenblas-dev: Common dev libraries for
#   scientific packages, image processing, and optimized linear algebra.
# - libpython3-dev: Essential for compiling Python packages with C extensions.
# - git: Needed if your requirements.txt refers to packages from Git repositories.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \ # Contains gcc, g++
    gfortran \        # <--- ADD THIS LINE! This is the Fortran compiler
    pkg-config \      # pkg-config was also not found, good to include
    libgl1-mesa-glx \
    libglib2.0-0 \
    libjpeg-dev \
    zlib1g-dev \
    libpython3-dev \
    libopenblas-dev \
    git && \
    # Clean up the apt cache to keep this intermediate stage's size down
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install your Python dependencies into a virtual environment.
# Installing into a venv is a best practice for Python applications in Docker.
# This ensures that all dependencies are isolated and can be easily copied to the final stage.
# We explicitly create the venv and then activate it to install packages.
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ---
# Stage 2: Runtime Stage
# This stage is for the final, slimmed-down image. It only contains what's needed to run the application,
# without any build tools or unnecessary dependencies from the 'builder' stage.
# Using the same base image (python:3.11-slim-bookworm) ensures compatibility of the Python interpreter.
FROM python:3.11-slim-bookworm AS runtime

# Set environment variables for the virtual environment.
# This makes sure Python uses the packages from the venv.
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Set the working directory for the runtime stage
WORKDIR /app

# Copy the created virtual environment from the 'builder' stage to the 'runtime' stage.
# This is the key step of multi-stage builds: only copy the necessary artifacts.
# This will include all installed Python packages.
COPY --from=builder /opt/venv /opt/venv

# Copy your application source code.
# This is done here, after copying the venv, so that changes to your code don't
# invalidate the venv layer in the build cache.
COPY . .

# Expose any ports your application listens on (e.g., for a web server)
# EXPOSE 8000 # Uncomment and adjust if your app listens on a port

# Define the command to run your application when the container starts.
# This command will automatically use the Python interpreter and packages from the virtual environment.
CMD ["python", "detect.py","--test"]