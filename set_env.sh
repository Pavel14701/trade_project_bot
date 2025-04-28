while IFS='=' read -r key value || [[ -n "$key" ]]; do
  [[ -z "$key" || "$key" == \#* ]] && continue
  value="$(echo "$value" | sed 's/^["'\''"]//; s/["'\''"]$//')"
  export "$key=$value"
done < <(grep -v '^\s*#' .env | tr -d ' ') || { echo "Error setting environment variables"; exit 1; }

grep -v '^#' .env | awk -F= '{print $1}' | while read var; do echo "$var=\"$(printenv "$var")\""; done
echo "Environment successfully updated"