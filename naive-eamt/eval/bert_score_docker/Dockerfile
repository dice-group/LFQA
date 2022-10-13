FROM python:3.9
WORKDIR /bertscore
COPY requirements.txt .
# install requirements.txt
RUN pip install -r requirements.txt
# Download the model in advance
RUN python -c "from evaluate import load; load(\"bertscore\")"
COPY service.py .
# Run the application
CMD ["-m", "flask", "--app", "/bertscore/service", "run", "--host=0.0.0.0", "--port=80", "--with-threads"]
ENTRYPOINT ["python"]