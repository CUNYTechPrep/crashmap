##!/usr/local/Cellar/bash/5.1.16/bin/bash

# Note: If you are running this script with bash, you will need bash version 5.
#   This is crucial especially for macOS user because macOS ships by default
#   bash version 3 at the time of writing this.
# Example shebang on line 1 if you installed bash 5.1.16 with brew. Uncomment 
#   and modify it to the path you installed bash 5.

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
