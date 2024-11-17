#!/bin/bash

echo "before: "$(date +"%T.%3N")

QUERY="SELECT * FROM initial_data;"

export PGPASSWORD=$POSTGRES_DB_PASSWORD
RESULTS=$(psql -U "$POSTGRES_DB_USER" -d "$POSTGRES_DB_NAME" -h "$POSTGRES_DB_HOST"  -c "$QUERY" -A -t)

while IFS= read -r line; do
    IFS='|' read -ra fields <<< "$line"
    formatted="${fields[0]}_${fields[1]}"
    redis-cli -u "redis://keydb" set "${formatted}" "${fields[2]}"
done <<< "$RESULTS"

echo "after: "$(date +"%T.%3N")
