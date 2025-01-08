#!/bin/bash

API_URL="https://scsport.eu/api/webhook"

post_deauthorization_event() {
    local owner_id=$1

    payload=$(cat <<EOF
{
    "object_type": "athlete",
    "object_id": $owner_id,
    "aspect_type": "update",
    "updates": { "authorized": "false" },
    "owner_id": $owner_id,
    "event_time": $(date +%s)
}
EOF
)

    curl -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "$payload"
}

OWNER_ID=29119306

post_deauthorization_event $OWNER_ID
