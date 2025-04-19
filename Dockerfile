FROM python:3.13-slim AS build
COPY --from=arigaio/atlas:latest /atlas /atlas

RUN apt-get update && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app/

COPY migrations /migrations

COPY ./requirements.txt /app/
RUN pip install -r requirements.txt
COPY doyoulikeit /app/


CMD ["uvicorn", "doyoulikeit:app", "--host", "0.0.0.0", "--port", "8080"]
