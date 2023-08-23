FROM python:3.10-alpine
COPY resources/* /
RUN python -m venv .venv && \
    .venv/bin/pip install -r requirements.txt
ENTRYPOINT [".venv/bin/python", "/action.py"]
