# PostgreSQL 16 with pgvector and Apache AGE extensions
FROM postgres:16.1

# Install build dependencies and utilities
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-server-dev-16 \
    git \
    curl \
    ca-certificates \
    flex \
    bison \
    && rm -rf /var/lib/apt/lists/*

# Install pgvector 0.5.1
RUN cd /tmp && \
    git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git && \
    cd pgvector && \
    make && \
    make install && \
    cd / && rm -rf /tmp/pgvector

# Install Apache AGE 1.6.0-rc0 (latest for PG16)
RUN cd /tmp && \
    git clone --branch PG16/v1.6.0-rc0 https://github.com/apache/age.git && \
    cd age && \
    make install && \
    cd / && rm -rf /tmp/age

# Cleanup build dependencies (keep postgresql-server-dev for runtime)
RUN apt-get purge -y --auto-remove \
    build-essential \
    git \
    flex \
    bison

# Set shared_preload_libraries to include AGE
RUN echo "shared_preload_libraries = 'age'" >> /usr/share/postgresql/postgresql.conf.sample

EXPOSE 5432
