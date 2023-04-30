FROM virtualhold/ansible-vault AS ansible
ARG ROOT_LOGIN_ANSIBLE
ARG ROOT_PASSWORD_ANSIBLE

# Create file for encryption
RUN touch db.credentials && \
    echo $ROOT_LOGIN_ANSIBLE >> db.credentials && \
    echo $ROOT_PASSWORD_ANSIBLE >> db.credentials

# Encrypt credentials
ADD ansible.credentials .
RUN ansible-vault encrypt db.credentials --vault-password-file=ansible.credentials

FROM python:3.8-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY --from=ansible db.credentials .

ADD . /app

RUN pip install -r requirements.txt