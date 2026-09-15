FROM python:3.12-slim
COPY server.py /opt/api/server.py
COPY error_description.txt /opt/api/error_description.txt
RUN mkdir -p /var/log/api
CMD ["python3", "/opt/api/server.py"]
