FROM python:3.10-alpine
COPY resources/* /
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "/action.py"]
