FROM python:3.12-slim

RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Simulate a fresh user
RUN useradd -m testuser
USER testuser
WORKDIR /home/testuser
ENV PATH="/home/testuser/.local/bin:${PATH}"

# Clone the framework (will use build arg or default to public repo)
ARG REPO_URL=https://github.com/nealatnaidoo/claude-agent-framework.git
ARG BRANCH=main
RUN git clone --branch ${BRANCH} ${REPO_URL} claude-agent-framework

# Run the installer non-interactively
RUN cd claude-agent-framework && echo "y" | ./bin/install.sh

# Verify caf is available
RUN caf --help

# Default: drop into shell for manual inspection
CMD ["/bin/bash"]
