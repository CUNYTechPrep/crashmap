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

loadEnv ../.env
loadEnv ../.env.development
loadEnv ../.env.local
loadEnv ../.env.development.local
flask run
