#!/bin/bash

echo "Running all syncs..."
python -m connectors.elasticsearch.run_sync

echo "Done."
