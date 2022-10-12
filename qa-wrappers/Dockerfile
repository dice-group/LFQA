FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
WORKDIR /app

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt; exit 0
RUN pip install uvicorn[standard]

COPY config.ini ./
COPY start.py ./
COPY systems systems