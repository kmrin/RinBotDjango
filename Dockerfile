FROM python:3.13.1

ENV DJANGO_SETTINGS_MODULE=settings
ENV PYTHONPATH=/app

RUN apt-get update && \
    apt-get install -y postgresql-client libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY rinbot /app

RUN pip install --upgrade pip
RUN pip install -r /app/python/requirements.txt

RUN mkdir -p /var/lib/rinbot/logs/tracebacks \
    /var/lib/rinbot/logs/lavalink \
    /var/lib/rinbot/cache

RUN chmod -R 777 /var/lib/rinbot
RUN chmod +x /app/scripts/init_instance.sh

ENTRYPOINT ["/app/scripts/init_instance.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
