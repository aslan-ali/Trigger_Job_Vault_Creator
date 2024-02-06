<h1 align="center">Hi 👋, I'm Aslan</h1>
<h3 align="center">DevOps Engineer</h3>

- 📫 How to reach me **aslanray1995@gmail.com**

<h3 align="left">Connect with me:</h3>
<p align="left">
</p>

<h3 align="left">Languages and Tools:</h3>
<p align="left"> <a href="https://www.python.org" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"/> </a> </p>

###### I trigger this Job from another project via ci.yml:
###### Example:
```bash
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
fi
```
###### I send variables to this Job. But i must predefined this variables on project or you can centralized Pipeline where you must set your variables automatically.

