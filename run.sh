#!/bin/bash

echo "Executing a bash statement"

python3 ./bitmex_ws.py &
python3 ./quotes_saver.py &
python3 ./app.py &

