FROM ghcr.io/gridai/base-images:v1.9-cpu
RUN curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list && \
    sudo apt update && \
    sudo apt install redis

RUN git clone https://github.com/RediSearch/RediSearch.git && \
    cd RediSearch &&  \
    make &&  \
    sudo mkdir /redismodules && sudo chown -R 1000 /redismodules && \
    mv bin/linux-x64-release/search/redisearch.so /redismodules/

CMD ["redis-server", "--port", "6379", "--protected-mode", "no", "--loadmodule", "/redismodules/redisearch.so"]
