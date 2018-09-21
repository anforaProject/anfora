import yaml
import os
import binascii
import bcrypt

def create_settings(filen):
    settings = yaml.load(open(filen))

    template=(
        f'NODENAME = "{settings.get("application_name")}"\n'
        f'SUMMARY = "{settings.get("server_description")}"\n'
        f'SCHEME = "{settings.get("scheme")}"\n'
        f'DOMAIN ="{settings.get("domain")}"\n'
        f'BASE_URL ="{settings.get("scheme")}://{settings.get("domain")}"\n'
        'ID=BASE_URL\n'
        f'MEDIA_FOLDER = "{settings.get("media_folder")}"\n'
        f'thumb_folder="{settings.get("thumb_folder")}"\n'
        f'pic_folder="{settings.get("image_folder")}"\n'
        f'icon="{settings.get("icons_folder")}"\n'
        f'salt_code="{str(bcrypt.gensalt())}"\n'
        f'SECRET = "{binascii.hexlify(os.urandom(64)).decode()}"\n'
        f'ROOT_PATH = "{settings.get("root_path")}"\n'
        f'DB_USER = "{settings.get("db_user")}"\n'
        f'DB_PORT = "{settings.get("db_port")}"\n'
        f'DB_HOST = "{settings.get("db_host")}"\n'
        f'DB_NAME = "{settings.get("db_name")}"\n'
        f'EMAIL_ENABLED = {settings.get("email_enabled")}\n'
    )

    if settings.get("email_enabled"):
        smtp_config = (
            f'SMTP_SERVER = "{settings.get("smtp_server")}"\n'
            f'SMTP_PORT = {settings.get("smtp_port")}\n'
            f'SMTP_LOGIN = "{settings.get("smtp_login")}"\n'
            f'SMTP_PASSWORD = "{settings.get("smtp_password")}"\n'
            f'SMTP_FROM_ADDRESS = "{settings.get("smtp_adress")}"\n'
        )

        template += smtp_config

    return template 

def create_settings_file(filen='config/docker.yaml', settings_path='settings.py'):

    settings = create_settings(filen)
    with open(settings_path, 'w') as f:
        f.write(settings)

#create_settings_file('/home/yabir/killMe/anfora/src/config/dev.yaml')

def travis_setup():
    fileb = open("config/tests.yaml")
    settings = yaml.load(fileb)
    fileb.close()
    
    path = os.environ.get('VENV_HOME_DIR', '/home/circleci/anfora/')
    settings["root_path"] = path
    settings["media_folder"] = os.path.join(path, 'uploads')
    fileb = open("config/tests.yaml", "w")
    yaml.dump(settings, fileb)
    fileb.close()