#!/bin/bash

# Run the Docker container in detached mode
docker run -d -p 8000:8000 jungle-quest

# Wait a few seconds for the container to start up
sleep 5

# Open the default browser (works on macOS, Linux, and Windows)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:8000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:8000
elif [[ "$OSTYPE" == "msys"* ]]; then
    start http://localhost:8000
else
    echo "Please open http://localhost:8000 in your browser"
fi
