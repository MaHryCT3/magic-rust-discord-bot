FROM python:3.12

WORKDIR /app

COPY image_generator/requirements.txt ./

# Install dependencies
RUN pip install -r requirements.txt

COPY core/ ./core
COPY global_constants.py ./
COPY image_generator/ ./image_generator
