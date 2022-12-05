FROM python:3.9.1

COPY ./ ./

RUN pip3 install -r requirements.txt

WORKDIR /

EXPOSE 8050

CMD ["python3", "./app.py"]