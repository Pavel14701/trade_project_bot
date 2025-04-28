export $(grep -v '^#' .env | xargs) || { echo "Error setting environment variables"; exit 1; }
grep -v '^#' .env | awk -F= '{print $1}' | while read var; do echo "$var=$(printenv "$var")"; done
echo "Environment successfully updated"