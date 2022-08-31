FROM python:3.9
WORKDIR /neamt
COPY requirements.txt .
# install pytorch CPU
RUN pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
# install fairseq
RUN git clone --branch fixing_prefix_allowed_tokens_fn https://github.com/nicola-decao/fairseq
# change directory
WORKDIR /neamt/fairseq
RUN pip install --editable ./
WORKDIR /neamt
# install requirements.txt
RUN pip install -r requirements.txt
# install genre
RUN git clone https://github.com/facebookresearch/GENRE.git
WORKDIR /neamt/GENRE
RUN python setup.py build
RUN python setup.py install
# Downloading spacy's multilingual entity recognition model
RUN python -m spacy download xx_ent_wiki_sm
# COPY SRC
WORKDIR /neamt
COPY start.py .
COPY ./component .
COPY ./util .
COPY configuration.ini .
# Run the application
CMD ["-m", "flask", "--app", "/neamt/start", "run", "--host=0.0.0.0", "--port=80"]
ENTRYPOINT ["python"]