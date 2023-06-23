FROM python:3.9-slim-buster

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
COPY ./Imaginepy /code/Imaginepy

RUN python3 -m pip install -i https://pypi.doubanio.com/simple/ --no-cache-dir --upgrade -r /code/requirements.txt
WORKDIR /code/Imaginepy
RUN python3 setup.py install


WORKDIR /code
COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
