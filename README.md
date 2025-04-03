# Digital Wallet API

## Descrição
API completa para gerenciamento de carteiras digitais e transações financeiras, desenvolvida com Django REST Framework e PostgreSQL.

---

## 📝 Índice
- [Recursos](#recursos)
- [Tecnologias](#tecnologias)
- [Configuração](#configuracao)
  - [Pré-requisitos](#pre-requisitos)
  - [Desenvolvimento Local](#desenvolvimento-local)
  - [Sem Docker](#sem-docker)
- [Documentação da API](#documentacao-da-api)
- [Testes](#testes)
- [Endpoints](#endpoints)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Licença](#licenca)

---

## ✨ Recursos
- ✅ Autenticação segura com JWT
- ✅ Criação e gerenciamento de usuários
- ✅ Operações de carteira digital:
  - Consulta de saldo
  - Depósitos
- ✅ Transferências entre usuários
- ✅ Histórico de transações com filtro por data
- ✅ Documentação interativa com Swagger
- ✅ Dados fictícios para demonstração
- ✅ Testes automatizados

---

## 🧪 Tecnologias
### Backend:
- Python 3.13
- Django 5.2
- Django REST Framework 3.16

### Banco de Dados:
- PostgreSQL 17

### Autenticação:
- JWT (JSON Web Tokens)

### Infraestrutura:
- Docker
- Docker Compose

### Ferramentas:
- Swagger/Redoc para documentação
- Faker para dados de teste

---

## 🚀 Configuração
### Pré-requisitos
- Docker e Docker Compose **ou**
- Python 3.10+ e PostgreSQL

### Desenvolvimento Local com Docker
1. Clone o repositório:
   ```bash
   git clone https://github.com/brunodealmeida17/digital-wallet-api
   cd digital-wallet-api
   ```
2. Crie o arquivo de ambiente:
   ```bash
   cp .env.example .env
   ```
3. Inicie os containers:
   ```bash
   docker-compose up -d
   ```
4. Execute as migrações:
   ```bash
   docker-compose exec web python manage.py migrate
   ```
5. Popule o banco de dados com dados fictícios:
   ```bash
   docker-compose exec web python manage.py populate_db
   ```
6. A API estará disponível em: [http://localhost:8000](http://localhost:8000)

### Sem Docker
1. Configure um banco PostgreSQL e atualize as variáveis no `.env`
2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate    # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Execute as migrações:
   ```bash
   python manage.py migrate
   ```
5. Popule o banco de dados:
   ```bash
   python manage.py populate_db
   ```
6. Inicie o servidor:
   ```bash
   python manage.py runserver
   ```

---

## 📚 Documentação da API
Acesse a documentação interativa:
- **Swagger UI**: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- **ReDoc**: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

---

## 🧬 Testes
Para executar a suite de testes:
```bash
docker-compose exec web python manage.py test
```
Ou sem Docker:
```bash
python manage.py test
```

---

## 🔌 Endpoints Principais
### Autenticação
| Método | Endpoint | Descrição |
|---------|----------|-------------|
| POST | `/api/auth/register/` | Registrar novo usuário |
| POST | `/api/auth/login/` | Login (obter tokens JWT) |
| POST | `/api/auth/token/refresh/` | Refresh token |

### Carteira
| Método | Endpoint | Descrição |
|---------|----------|-------------|
| GET | `/api/wallet/` | Consultar saldo |
| POST | `/api/wallet/deposit/` | Adicionar saldo |

### Transferências
| Método | Endpoint | Descrição |
|---------|----------|-------------|
| POST | `/api/transfer/` | Criar transferência |
| GET | `/api/transfer/history/` | Histórico de transações |

**Filtros opcionais para histórico:**
- `start_date`: Data inicial (YYYY-MM-DD)
- `end_date`: Data final (YYYY-MM-DD)

---

## 💾 Estrutura do Projeto
```
digital_wallet_api/
├── app/                   # Aplicação principal
│   ├── migrations/        # Migrações do banco de dados
│   ├── management/        # Comandos customizados
│   ├── __init__.py
│   ├── admin.py           # Configuração do admin
│   ├── models.py          # Modelos de dados
│   ├── serializers.py     # Serializadores DRF
│   ├── views.py           # Views da API
│   ├── urls/              # Rotas organizadas
│   ├── tests.py           # Testes automatizados
├── digital_wallet_api/    # Configurações do projeto
│   ├── settings.py        # Configurações Django
│   ├── urls.py            # URLs principais
│   ├── wsgi.py
├── .env.example           # Variáveis de ambiente exemplo
├── Dockerfile             # Configuração Docker
├── docker-compose.yml     # Orquestração de containers
├── requirements.txt       # Dependências Python
└── README.md              # Este arquivo
```

---

## 📚 Licença
Este projeto está licenciado sob a licença BSD - veja o arquivo LICENSE para detalhes.

