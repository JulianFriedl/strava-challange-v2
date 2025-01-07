#!/bin/bash

API_URL="https://scsport.eu/api/webhook"

post_activity_update() {
    local object_id=$1
    local owner_id=$2
    local title=$3

    payload=$(cat <<EOF
{
    "object_type": "activity",
    "object_id": $object_id,
    "aspect_type": "create",
    "updates": {},
    "owner_id": $owner_id,
    "event_time": $(date +%s)
}
EOF
)

    # Send the POST request
    curl -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "$payload"
}

OBJECT_ID=13293349251
OWNER_ID=136722253

post_activity_update $OBJECT_ID $OWNER_ID
