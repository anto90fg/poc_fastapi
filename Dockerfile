FROM python:3.9-bullseye

WORKDIR /app
ENV PYTHONPATH=/app
# Update the package manager's package index
RUN apt-get update && apt-get install -y tzdata software-properties-common openjdk-17-jdk
RUN apt-get -y upgrade
COPY pyproject.toml poetry.lock ./README.md .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir --upgrade poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --with test

RUN addgroup --system reply && adduser --system --shell /sbin/nologin --home /var/cache/reply --ingroup reply reply
RUN chown reply:reply /app
USER reply
SHELL ["/bin/bash", "-c"]
CMD poetry run pytest tests/ -vv --cov --cov-report term-missing
