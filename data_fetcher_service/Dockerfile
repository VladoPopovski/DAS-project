#Овој фајл креира слика за Python апликација, инсталира Google Chrome и потребни Python библиотеки
#и ја стартува апликацијата преку main.py.

FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget unzip curl xvfb libxi6 libgconf-2-4 \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" | tee -a /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install webdriver-manager

COPY . .

CMD ["python", "main.py"]
