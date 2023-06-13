from getpass import getpass
import warnings, readline
warnings.filterwarnings(action='ignore',message='Python 3.6 is no longer supported')
from cryptography.fernet import Fernet

password = getpass()
key = Fernet.generate_key()
fernet = Fernet(key)
encMessage = fernet.encrypt(password.encode())

with open('.env', 'w') as file:
    file.write(str(encMessage))
    file.write(str(key))

with open('.env', 'r') as file:
    password = file.readline().split("'")[1]
decMessage = fernet.decrypt(password).decode()
print("Your password is saved, encrypted and hidden!")