#Овој фајл ги дефинира сите услуги и начинот заедно да работаат
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app
COPY main.py /app/
COPY api.py /app/

RUN pip install --no-cache-dir pandas openpyxl flask

EXPOSE 5000

VOLUME ["/app/data"]

CMD ["python", "/app/main.py"]
