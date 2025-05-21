FROM python:3.11.11-alpine3.21

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0"]
