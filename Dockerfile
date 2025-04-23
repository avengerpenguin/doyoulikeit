FROM --platform=linux/amd64 python:3.13-slim AS build

RUN apt-get update && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install build setuptools wheel

COPY . /app/
RUN python -m build --wheel

FROM --platform=linux/amd64 python:3.13-slim AS app
COPY ./requirements.txt /tmp/dist/
RUN pip install -r /tmp/dist/requirements.txt

COPY --from=build /app/dist /tmp/dist
RUN pip install /tmp/dist/*.whl && rm -rf /tmp/dist

CMD ["uvicorn", "doyoulikeit:app", "--host", "0.0.0.0", "--port", "8080"]
