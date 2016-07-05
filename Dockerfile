FROM python:latest

VOLUME ["/antminer-autotune"]

WORKDIR /antminer-autotune

ADD requirements.txt .

RUN pip install -r requirements.txt

CMD ["python3", "-m", "antminer_autotune"]
