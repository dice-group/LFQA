FROM python:3.9
WORKDIR /bertsimilarity
COPY requirements.txt .
# install requirements.txt
RUN pip install -r requirements.txt
# Download the model in advance
COPY model_init.py .
RUN python model_init.py
COPY service.py .
# Run the application
CMD ["-m", "flask", "--app", "/bertsimilarity/service", "run", "--host=0.0.0.0", "--port=80", "--with-threads"]
ENTRYPOINT ["python"]