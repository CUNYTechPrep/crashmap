loadEnv() {
  local envFile="${1}"
  if [ -f "$envFile" ]; then
    local environmentAsArray variableDeclaration
    mapfile environmentAsArray < <(
      grep --invert-match '^#' "${envFile}" | # Remove commented lines.
        grep --invert-match '^\s*$' # Remove blank lines.
    )
    for variableDeclaration in "${environmentAsArray[@]}"; do
      export "${variableDeclaration//[$'\r\n']/}" # Remove line breaks and export the variables.
    done
    echo "Loaded environment variables from $envFile."
  else
    echo "$envFile not found."
  fi
}

loadEnv .env
loadEnv ".env.$1"
loadEnv .env.local
loadEnv ".env.$1.local"

docker-compose -f "docker-compose.$1.yml" "$2"
