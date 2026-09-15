FROM python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea

# Grader-owned directory: expected values and the case inputs live here,
# readable only by root. The submitted parser never enters this tree; it is
# copied into /grade/run at grade time and executed as `nobody`.
RUN mkdir -p /grade /tests
COPY grader.py /grade/grader.py
COPY driver.py /grade/driver.py
COPY expected.json /grade/expected.json
COPY cases_public.json /grade/cases_public.json
RUN chmod 700 /grade && chmod 600 /grade/expected.json /grade/cases_public.json

COPY test.sh /tests/test.sh
RUN chmod 755 /tests/test.sh
