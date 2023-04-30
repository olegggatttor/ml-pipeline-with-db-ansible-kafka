FROM virtualhold/ansible-vault AS ansible
ARG ROOT_LOGIN_ANSIBLE
ARG ROOT_PASSWORD_ANSIBLE
ARG ANSIBLE_PASSWORD

WORKDIR /ansible
# Create file for encryption
RUN touch db.credentials && \
    echo $ROOT_LOGIN_ANSIBLE >> db.credentials && \
    echo $ROOT_PASSWORD_ANSIBLE >> db.credentials

# Encrypt credentials
RUN touch ansible.credentials && \
    echo $ANSIBLE_PASSWORD >> ansible.credentials

RUN ansible-vault encrypt db.credentials --vault-password-file=ansible.credentials

FROM python:3.8-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY --from=ansible /ansible/db.credentials .

ADD . /app

RUN pip install -r requirements.txt