import sys
import os

# Adicione o diretório do seu projeto ao PATH do Python
project_home = u'/home/SEU_USUARIO/SEU_DIRETORIO_DO_PROJETO'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Defina a variável de ambiente FLASK_SECRET_KEY
os.environ['FLASK_SECRET_KEY'] = 'SUA_CHAVE_SECRETA_FORTE_AQUI'

# Importe a aplicação Flask
from app import app as application


