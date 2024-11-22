FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code

RUN apt-get update && apt-get install -y ffmpeg

CMD ["gunicorn", "--workers", "1", "--timeout", "600", "--bind", "0.0.0.0:7860", "wsgi:app"]
