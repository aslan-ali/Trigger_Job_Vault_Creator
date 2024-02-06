import os
import requests
import json
import sys
import base64
import urllib3
import operator
from colorama import Fore, Style, init


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
SCREEN_WIDTH = 80
centered = operator.methodcaller('center', SCREEN_WIDTH)

GITLAB_USER_TOKEN = os.getenv("GITLAB_USER_TOKEN")
CI_PROJECT_ID = os.getenv("CI_PROJECT_ID")
VAULT_URL = os.getenv("VAULT_URL")
VAULT_TOKEN = os.getenv("VAULT_TOKEN_TRIGGER")
APP_NAMESPACE = os.getenv("APP_NAMESPACE")
APP_NAME = os.getenv("APP_NAME")
ENV = os.getenv("env")

print(centered(Fore.GREEN + f"============={APP_NAME}/{APP_NAMESPACE}/{ENV}=============" + Fore.RESET))

#authentication to VAULT
headers = {
    "X-Vault-Token": VAULT_TOKEN,
    "Content-Type": "application/json",
}

print(centered(Fore.GREEN + f"=============Creating Secret for {APP_NAMESPACE}/{APP_NAME}/{ENV}==================" + Fore.RESET))

#adding key value for the first time and convert to
secret_data = {"key1": "value1"}
data_json = json.dumps({"data": secret_data})

path_namespace = f"secret/data/{APP_NAMESPACE}/{APP_NAME}/{ENV}"
response_secret = requests.get(
    f"{VAULT_URL}/v1/{path_namespace}", headers=headers, verify=False
)


def response_secret_get():
    if response_secret.ok:
        print(centered(Fore.YELLOW + f"{APP_NAMESPACE}/{APP_NAME}/{ENV} - Secret Path already exist!" + Fore.RESET))
    else:
        response = requests.put(
            f"{VAULT_URL}/v1/{path_namespace}", data=data_json, headers=headers, verify=False
        )

        def response_print_secret():
            if response.ok:
                print(centered(Fore.GREEN + f"{APP_NAMESPACE}/{APP_NAME}/{ENV} - Secret Path successfully created!" + Fore.RESET))
            else:
                print(centered(Fore.RED + f"Error creating secret. Status code: {response.status_code}. Response content: {response.content}" + Fore.RESET))

        response_print_secret()
response_secret_get()


print(
    centered(Fore.GREEN + f"=============Creating Policy for {APP_NAMESPACE}/{APP_NAME}/*/{ENV}==================" + Fore.RESET)
)
response_policy= requests.get(
    f"{VAULT_URL}/v1/sys/policy/{APP_NAMESPACE}_{ENV}",
    headers=headers,
    verify=False,
)

def render_json_template(template_path, context):
    with open(template_path, "r") as f:
        template_content = f.read()
    template_content = template_content.replace('${APP_NAMESPACE}', context["APP_NAMESPACE"])
    return json.loads(template_content)


def response_policy_get():
    if response_policy.ok:
        print(centered(Fore.YELLOW + f"{APP_NAMESPACE}_{ENV} - Policy already exist!" + Fore.RESET))
    else:
        policy = render_json_template(f"templates/{ENV}.json", {"APP_NAMESPACE": APP_NAMESPACE})
        policy_single_line = json.dumps(policy, indent=2)
        payload = {"policy": policy_single_line}
        response = requests.put(
            f"{VAULT_URL}/v1/sys/policy/{APP_NAMESPACE}_{ENV}",
            headers=headers,
            json=payload,
            verify=False
        )
        def response_policy_create():
            if response.ok:
                print(
                    centered(Fore.GREEN + f"{APP_NAMESPACE}_{ENV} - Policy successfully created!" + Fore.RESET)
                )
            else:
                print(
                    centered(Fore.RED + f"Error creating policy. Status code: {response.status_code}. Response content: {response.content}" + Fore.RESET)
                )

        response_policy_create()
response_policy_get()

print(
    centered(Fore.GREEN + f"=============Apply Policy for AppRole {APP_NAMESPACE}_{ENV}==================" + Fore.RESET)
)

role_name = f"{APP_NAMESPACE}_{ENV}"
policy_name = f"{APP_NAMESPACE}_{ENV}"
data = {"token_policies": [policy_name], "bind_secret_id": "true"}

response_role = requests.get(
    f"{VAULT_URL}/v1/auth/approle/role/{role_name}",
    headers=headers,
    verify=False
)
def response_role_get():
    if response_role.ok:
        print(centered(Fore.YELLOW + f"{role_name}- Role already exist!" + Fore.RESET))
    else:
        response = requests.post(
            f"{VAULT_URL}/v1/auth/approle/role/{role_name}",
            headers=headers,
            json=data,
            verify=False
        )
        def response_role_assign():
            if response.ok:
                print(
                    centered(Fore.GREEN + f"Policy {policy_name} assigned to AppRole {role_name} successfully!" + Fore.RESET)
                )
            else:
                print(
                    centered(Fore.RED + f"Error assigning policy {policy_name} to AppRole {role_name}. Status code {response.status_code}" + Fore.RESET)
                )
                sys.exit(1)

        response_role_assign()
response_role_get()


print(centered(Fore.GREEN + "==============Retrieve a Role-ID && Secret-ID==================" + Fore.RESET))

response = requests.get(
    f"{VAULT_URL}/v1/auth/approle/role/{role_name}/role-id",
    headers=headers,
    verify=False,
)


def vault_roleid():
    role_id = None
    if response.ok:
        role_id = response.json()["data"]["role_id"]
        print(centered(Fore.GREEN + f"Role ID for Approle {role_name}:  {role_id}" + Fore.RESET))
    else:
        print(centered(Fore.RED + f"Error retrieving Role ID for AppRole {role_name}" + Fore.RESET))
        sys.exit(1)
    return role_id


role_id = vault_roleid()
role_id_encode = base64.b64encode(role_id.encode()).decode()


response = requests.post(
    f"{VAULT_URL}/v1/auth/approle/role/{role_name}/secret-id",
    headers=headers,
    verify=False,
)


def vault_secretid():
    secret_id = None
    if response.ok:
        secret_id = response.json()["data"]["secret_id"]
        print(centered(Fore.GREEN + f"Secret ID for AppRole {role_name}: {secret_id}" + Fore.RESET))
    else:
        print(centered(Fore.RED + f"Error retrieve Secret ID for AppRole {role_name}." + Fore.RESET))
        sys.exit(1)
    return secret_id


secret_id = vault_secretid()
secret_id_encode = base64.b64encode(secret_id.encode()).decode()


vault_secret = {"VAULT_ROLE_ID": role_id_encode, "VAULT_SECRET_ID": secret_id_encode}
vault_json = json.dumps({"data": vault_secret})

path_vault = f"secret/data/{APP_NAMESPACE}/secret-vault/{ENV}"
response_secret = requests.get(
    f"{VAULT_URL}/v1/{path_vault}", headers=headers, verify=False
)


def response_vault_get():
    if response_secret.ok:
        print(centered(Fore.YELLOW + f"{APP_NAMESPACE}/secret-vault/{ENV} - Secret Vault Path already exist!" + Fore.RESET))
    else:
        response = requests.put(
            f"{VAULT_URL}/v1/{path_vault}", data=vault_json, headers=headers, verify=False
        )

        def response_vault_secret():
            if response.ok:
                print(
                    centered(Fore.GREEN + f"{APP_NAMESPACE}/secret-vault/{ENV} - Vault Secret Path successfully created!" + Fore.RESET)
                )
            else:
                print(
                    centered(Fore.RED + f"Error creating secret. Status code: {response.status_code}. Response content: {response.content}" + Fore.RESET)
                )

        response_vault_secret()
response_vault_get()
