FROM python:3.12

WORKDIR /app

COPY bot/requirements.txt ./

# Install dependencies
RUN pip install -r requirements.txt

COPY core/ ./core
COPY global_constants.py ./
COPY bot/ ./bot
