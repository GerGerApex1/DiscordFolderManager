import keyring
def store_token(token):
    keyring.set_password('discord_server_manager', 'DISCORD_USER_TOKEN', token)
    print('Successfuly stored token')
def get_token():
    password =  keyring.get_password('discord_server_manager', 'DISCORD_USER_TOKEN')
    if password == "":
        return None
    else:
        return password
def is_available():
    token = get_token()
    if token is None:
        return False
    else:
        return True