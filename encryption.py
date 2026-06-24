from cryptography.fernet import Fernet

KEY = b"xXXV2aTdwf54FtodDeZDK8gAWomH8deN_U-wJUuxxaE="

fernet = Fernet(KEY)


def encrypt_password(password):
    return fernet.encrypt(
        password.encode()
    ).decode()


def decrypt_password(encrypted):
    return fernet.decrypt(
        encrypted.encode()
    ).decode()
