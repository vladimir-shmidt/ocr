FROM ubuntu AS base
RUN apt update && apt upgrade -y

RUN apt-get install -y locales && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LC_ALL en_US.UTF-8

FROM base AS publish
RUN apt install -y build-essential cmake curl
WORKDIR /src
COPY . .
RUN mkdir build && cd build && cmake .. && make
RUN curl -L https://github.com/bakwc/JamSpell-models/raw/master/ru.tar.gz -o ru.tar.gz && tar -xvf ru.tar.gz && cp ./ru_small.bin ./build/

FROM base AS final
WORKDIR /app
EXPOSE 80
COPY --from=publish /src/build .
CMD ["./web_server/web_server", "ru_small.bin", "0.0.0.0", "80"]