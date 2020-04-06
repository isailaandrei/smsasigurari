FROM python:3
ENV PYTHONUNBUFFERED 1
COPY requirements.txt /
RUN pip install -r /requirements.txt
RUN mkdir /code
WORKDIR /code
COPY . /code/
EXPOSE 8000