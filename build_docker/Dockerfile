FROM ubuntu:latest
RUN apt-get update &&\
    apt-get install -y pip &&\
    apt-get install -y curl
RUN curl -LO https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb &&\
    apt-get install -y ./google-chrome-stable_current_amd64.deb &&\
    rm google-chrome-stable_current_amd64.deb &&\
    curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin/:$PATH"
COPY ./ /usr/saroj_analytics
WORKDIR /usr/saroj_analytics
RUN uv sync --frozen
