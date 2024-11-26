FROM python:3.11.7
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN apt-get update && apt-get install -y postgresql-client


RUN mkdir /code
WORKDIR /code

COPY . /code/

RUN pip install --upgrade pip &&  pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

COPY entrypoint.sh /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh
ENTRYPOINT ["/code/entrypoint.sh"]
