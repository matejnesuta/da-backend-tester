FROM debian:bookworm-slim

# Install base dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Java 21 from Eclipse Temurin
RUN mkdir -p /etc/apt/keyrings \
    && wget -O - https://packages.adoptium.net/artifactory/api/gpg/key/public | tee /etc/apt/keyrings/adoptium.asc \
    && echo "deb [signed-by=/etc/apt/keyrings/adoptium.asc] https://packages.adoptium.net/artifactory/deb bookworm main" | tee /etc/apt/sources.list.d/adoptium.list \
    && apt-get update \
    && apt-get install -y temurin-21-jdk \
    && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/temurin-21-jdk-amd64

# Install Node.js 20.x
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Upgrade npm (JS client requires >= 11.5.1)
RUN npm install -g npm@11.5.1

# Install pnpm
RUN npm install -g pnpm@10.33.0

# Install Yarn Classic and enable Yarn Berry (via corepack)
# Note: corepack is enabled but pnpm version is explicitly pinned to avoid auto-upgrading
RUN npm install -g yarn@1.22.22 \
    && corepack enable \
    && corepack prepare pnpm@10.33.0 --activate

# Install Python 3 and pip (Bookworm has Python 3.11 which is compatible)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*
ENV TRUSTIFY_DA_PIP_PATH=/usr/bin/pip3

# Install uv (Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv

# Install Poetry (Python package manager)
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && mv /root/.local/bin/poetry /usr/local/bin/poetry

# Install Go
ENV GO_VERSION=1.22.1
RUN wget https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz \
    && rm go${GO_VERSION}.linux-amd64.tar.gz
ENV PATH="/usr/local/go/bin:${PATH}"

# Install Maven
ENV MAVEN_VERSION=3.9.6
RUN wget https://archive.apache.org/dist/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz \
    && tar -xzf apache-maven-${MAVEN_VERSION}-bin.tar.gz -C /opt \
    && ln -s /opt/apache-maven-${MAVEN_VERSION} /opt/maven \
    && rm apache-maven-${MAVEN_VERSION}-bin.tar.gz
ENV PATH="/opt/maven/bin:${PATH}"

# Install Gradle
ENV GRADLE_VERSION=8.6
RUN wget https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip \
    && unzip gradle-${GRADLE_VERSION}-bin.zip -d /opt \
    && ln -s /opt/gradle-${GRADLE_VERSION} /opt/gradle \
    && rm gradle-${GRADLE_VERSION}-bin.zip
ENV PATH="/opt/gradle/bin:${PATH}"

# Install Rust and Cargo
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Build Trustify DA Clients from source
WORKDIR /build

# Build arguments for client versions (can override at build time)
ARG JAVA_CLIENT_REPO=https://github.com/guacsec/trustify-da-java-client.git
ARG JAVA_CLIENT_BRANCH=main
ARG JS_CLIENT_REPO=https://github.com/guacsec/trustify-da-javascript-client.git
ARG JS_CLIENT_BRANCH=main

# Optional: GitHub token for accessing GitHub Packages (Java client dependencies)
ARG GITHUB_TOKEN=""

# Build Java client
RUN echo "Building Java client from source..." && \
    git clone --depth 1 --branch ${JAVA_CLIENT_BRANCH} ${JAVA_CLIENT_REPO} java-client && \
    cd java-client && \
    if [ -n "$GITHUB_TOKEN" ]; then \
        mkdir -p ~/.m2 && \
        echo "<settings><servers><server><id>github</id><username>token</username><password>${GITHUB_TOKEN}</password></server></servers></settings>" > ~/.m2/settings.xml; \
    fi && \
    mvn clean package -DskipTests && \
    mkdir -p /opt/clients && \
    find target -name '*-cli.jar' -exec cp {} /opt/clients/java-client.jar \; && \
    if [ ! -f /opt/clients/java-client.jar ]; then \
        echo "ERROR: CLI JAR not found in target directory. Contents:"; \
        ls -la target/*.jar || echo "No JAR files found"; \
        exit 1; \
    fi && \
    cd /build && rm -rf java-client

# Build JavaScript client
# Note: We keep the source directory because npm install -g creates a symlink to it
RUN echo "Building JavaScript client from source..." && \
    git clone --depth 1 --branch ${JS_CLIENT_BRANCH} ${JS_CLIENT_REPO} /opt/js-client && \
    cd /opt/js-client && \
    npm install && \
    npm run compile && \
    npm install -g . && \
    echo "Checking for installed JS client binary..." && \
    which trustify-da-javascript-client

# Set environment variables for client paths
ENV TRUSTIFY_DA_JAVA_CLIENT=/opt/clients/java-client.jar
ENV TRUSTIFY_DA_JS_CLIENT=/usr/bin/trustify-da-javascript-client

# Create app directory
WORKDIR /app

# Copy Python dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages

# Copy application code (new structure)
COPY tests/ ./tests/
COPY conftest.py .
COPY pytest.ini .
COPY deploy/entrypoint.sh .
COPY deploy/generate-lockfiles.sh .
COPY deploy/generate-python-venvs.sh .
COPY deploy/generate-all.sh .

# Create mount point for testfiles (will be mounted from host)
RUN mkdir -p /testfiles

# Create __init__.py files for Python module structure
RUN touch tests/__init__.py tests/client-testing/__init__.py tests/license-testing/__init__.py

# Entrypoint runs pytest
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["-n", "1"]
