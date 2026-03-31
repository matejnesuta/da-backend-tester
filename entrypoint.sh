#!/bin/bash
#
# Container entrypoint: run pytest with any arguments passed to the container.
# Lock file generation is handled separately by generate-lockfiles.sh,
# which is invoked by run-in-container.sh after the image is built.
#

set -e

cd /app
exec python3 -m pytest "$@"
