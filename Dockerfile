FROM python:3.10-slim-buster
ENV PYTHONUNBUFFERED 1
RUN apt-get upgrade
RUN python -m pip install --upgrade pip
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app
WORKDIR /app
EXPOSE 80
EXPOSE 80
CMD ["mysql", "-h", "hostname", "-u", "root", "urls_db" ,"<", "/app/app/start.sql"]
LABEL maintainer="daniel.granuzzo@gmail.com"
ENTRYPOINT "python" "/app/app/main.py"


