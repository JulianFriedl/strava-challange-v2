#!/bin/bash
# chmod +x stress_test.sh
# ./stress_test.sh
# you need to disable flask sessions for map endpoint in order to run this

BASE_URL="http://localhost/api/map/"

YEARS=("2020,2021" "2022,2023" "2024,2025" "2021,2022" "2023,2025")

ATHLETES=("64384000,83693886,60746061" "129231074,65832043,64384000" "83693886,129231074,60746061" "65832043,64384000,83693886")

REQUEST_COUNT=100

DELAY=0

echo "Starting stress test with $REQUEST_COUNT requests..."

for ((i=1; i<=REQUEST_COUNT; i++))
do
  YEARS_IDX=$((i % ${#YEARS[@]}))
  ATHLETES_IDX=$((i % ${#ATHLETES[@]}))

  YEARS_PARAM="${YEARS[$YEARS_IDX]}"
  ATHLETES_PARAM="${ATHLETES[$ATHLETES_IDX]}"

  curl -s -o /dev/null -w "Request $i: HTTP Status: %{http_code}\n" \
    "${BASE_URL}?years=${YEARS_PARAM}&athletes=${ATHLETES_PARAM}"

  sleep $DELAY
done

echo "Stress test completed."
