I trigger this Job from another project via ci.yml:
Example:

output=$(curl --silent --request POST \
            --form "ref=master" \
            --form "variables[TRIGGER_JOB]=Vault" \
            --form "variables[APP_NAMESPACE]=$NAMESPACE" \
            --form "variables[APP_NAME]=$APP_NAME" \
            --form "variables[env]=$env" \
            --form "token=$TRIGGER_VAULT_CREATOR" \
            "${CI_API_V4_URL}/projects/13/trigger/pipeline")
if [[ "$output" == *"created"* ]]; then
     echo "Vault-Creator Project triggered successfully!"


I send variables to this Job. But i must predefined this variables on project or you can centralized Pipeline where you must set your variables automatically.

