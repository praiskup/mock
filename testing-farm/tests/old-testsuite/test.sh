#!/bin/bash -eux

cd ../../../mock

# Install the tested RPMs
install-mock-packages-built-by-packit mock-core-configs mock

# Download the tested SRPM
SRPM_DOWNLOAD_DIR=/tmp/mock-test-srpms install-mock-packages-built-by-packit mock

if (make check > >(tee the-log | grep -e FAILED: -e PASSED:) 2>&1) >&2; then
    echo "The 'make check' testsuite passed."
else
    cat the-log
    exit 1
fi
