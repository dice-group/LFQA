FROM python:3.9
WORKDIR /neamt
COPY start.py .
COPY ./component .
COPY configuration.ini .
# install pytorch CPU
RUN pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
# install fairseq
    git clone --branch fixing_prefix_allowed_tokens_fn https://github.com/nicola-decao/fairseq
# change directory
WORKDIR /neamt/fairseq
RUN pip install --editable ./
WORKDIR /neamt
# install requirements.txt
RUN pip install -r requirements.txt
# install genre
    git clone https://github.com/facebookresearch/GENRE.git
WORKDIR /neamt/GENRE
RUN python setup.py build
    python setup.py install
# Run the application
CMD ["/neamt/start.py"]
ENTRYPOINT ["python"]