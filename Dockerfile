FROM python:3

# path inside the container in docker
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# output: uvicorn app.main:app --host 0.0.0.0 --port 8000 -> Means each comma is an empty space
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]