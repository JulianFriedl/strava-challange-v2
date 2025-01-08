#!/bin/bash

DEAUTH_URL="https://www.strava.com/oauth/deauthorize"

deauthorize_athlete() {
    local access_token=$1

    response=$(curl -X POST "$DEAUTH_URL" \
        -H "Authorization: Bearer $access_token" \
        -H "Content-Type: application/json" \
        -d "{}")

    echo "Deauthorization response: $response"
}

ACCESS_TOKEN="0a93c790c48c5197cf6fe1a7e681000d68bb70f6"

deauthorize_athlete $ACCESS_TOKEN
