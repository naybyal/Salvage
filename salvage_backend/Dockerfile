FROM python:3.11-bookworm

# Add user and group first to ensure proper permissions
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    clang-14 \
    libclang-14-dev \
    git \
    python3-clang-14 \
    llvm-14 \
    llvm-14-dev \
    && rm -rf /var/lib/apt/lists/*

ENV LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:/usr/lib/llvm-14/lib:$LD_LIBRARY_PATH"
# Copy requirements first for caching
COPY ./requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt


COPY /build/my-languages.so /usr/src/app/build/my-languages.so
# Copy app files
COPY . .

# Ensure 'output' directory exists and has correct permissions
RUN mkdir -p /usr/src/app/output && \
    chmod -R 777 /usr/src/app/output && \
    chown -R appuser:appgroup /usr/src/app/output

# Set ownership before switching user
RUN chown -R appuser:appgroup /usr/src/app

USER appuser

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]