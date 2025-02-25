import os
import yaml

from pathlib import Path

class Config:
    def __init__(self):
        # TODO: Use rinbot paths system
        base_dir = Path(__file__).resolve().parent
        config_path = base_dir / 'lavalink' / 'config' / 'rinbot.yml'
        
        self.config_path = config_path
        self.config = self._load_config()
        
        self._set_env_vars()
    
    def _load_config(self):
        try:
            # TODO: Use rinbot paths system
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        
        except Exception as e:
            # TODO: Use rinbot logger
            print(f"Error loading configuration: {e}")
            
            # Return default configuration
            return {
                'django': {
                    'secret_key': 'default-insecure-key',
                    'debug': True,
                    'allowed_hosts': [],
                    'superuser': {
                        'username': 'admin',
                        'email': 'admin@example.com',
                        'password': 'adminpassword'
                    }
                },
                'database': {
                    'name': 'rinbot',
                    'user': 'rinbot',
                    'password': 'rinbotpassword',
                    'host': 'rinbot-postgres',
                    'port': 5432
                },
                'lavalink': {
                    'password': 'youshallnotpass',
                    'port': 2333
                },
                'instance': {
                    'base_dir': '/var/lib/rinbot',
                    'subdirs': [
                        'django/db',
                        'logs/tracebacks',
                        'logs/lavalink',
                        'cache'
                    ]
                }
            }
    
    def _set_env_vars(self):
        os.environ['DB_NAME'] = str(self.database.get('name'))
        os.environ['DB_USER'] = str(self.database.get('user'))
        os.environ['DB_PASSWORD'] = str(self.database.get('password'))
        os.environ['DB_HOST'] = str(self.database.get('host'))
        os.environ['DB_PORT'] = str(self.database.get('port'))
    
        os.environ['DJANGO_SUPERUSER_USERNAME'] = str(self.django.get('superuser').get('username'))
        os.environ['DJANGO_SUPERUSER_EMAIL'] = str(self.django.get('superuser').get('email'))
        os.environ['DJANGO_SUPERUSER_PASSWORD'] = str(self.django.get('superuser').get('password'))
    
    @property
    def django(self):
        return self.config.get('django')
    
    @property
    def database(self):
        return self.config.get('database')
    
    @property
    def lavalink(self):
        return self.config.get('lavalink')
    
    @property
    def instance(self):
        return self.config.get('instance')


config = Config()

django_config = config.django
database_config = config.database
lavalink_config = config.lavalink
instance_config = config.instance 