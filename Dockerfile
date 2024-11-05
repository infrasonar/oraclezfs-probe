FROM python:3.12
ADD . /code
WORKDIR /code
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update && apt install -y vim
CMD ["python", "main.py"]
