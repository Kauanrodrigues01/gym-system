# 🏋️ Sistema de Gestão de Academia

## Índice
- [Sobre](#sobre)
- [Funcionalidades Principais](#funcionalidades-principais)
- [Integrações Avançadas](#integrações-avançadas)
- [Relatórios e Dados](#relatórios-e-dados)
- [Benefícios](#benefícios)
- [Instalação](#instalação)

## <a id="sobre">Sobre o Projeto</a>
![Imagem do Sistema](https://i.imgur.com/HjT46fz.png)
Sistema de gestão de academia com automação inteligente, focado em eficiência administrativa e experiência do aluno.

## <a id="funcionalidades-principais">Funcionalidades Principais</a>
![Funcionalidade Principal](https://i.imgur.com/XUpvZzx.png)
- CRUD completo de alunos
- Automatização de tarefas com Celery
- Paginação e filtros otimizados

## Tecnologias

- Django
- Django Rest Framework
- Celery
- Redis
- Pandas
- Plotly

## <a id="integrações-avançadas">Integrações Avançadas 🚀</a>
### 📱 Integração WhatsApp (UltraMsg)
- Alertas automáticos de pagamento vencido
- Notificações personalizadas

### 💳 Integração de Pagamentos
- Geração de QR Code dinâmico
- Envio automático para WhatsApp
- Rastreamento em tempo real do status de pagamento

## <a id="relatórios-e-dados">📊 Relatórios e Visualização de Dados</a>
![Integração Avançada](https://i.imgur.com/kceu3KD.png)

### 📄 Relatórios em PDF
- Geração com xhtml2pdf e reportlab
- Design personalizado
- Exportação instantânea

### 📈 Análise de Dados
- Gráficos financeiros interativos
- Visualização de lucro mensal com Pandas e Plotly

## <a id="benefícios">Benefícios para a Academia</a>

- 🔹 Gestão centralizada de alunos e pagamentos
- 🔹 Automação de tarefas repetitivas
- 🔹 Tomada de decisão baseada em dados
- 🔹 Relatórios automáticos
- 🔹 Escalabilidade para academias de diversos portes

## **Exemplo de Fluxo**

1. Aluno realiza pagamento
2. Sistema atualiza status automaticamente
3. Verificação diária de pagamentos
4. Geração de gráficos e relatórios

## <a id="instalação">Instalação</a>

### Pré-requisitos
- Python 3.8+
- Redis
- Docker (opcional)

### Passos de Instalação

Clone o repositório do projeto para seu diretório local:

```bash
git clone https://link-do-repositorio.git
cd nome-do-repositorio
```

### 2. Criar e Ativar um Ambiente Virtual

Crie um ambiente virtual para isolar as dependências do projeto:

```bash
python -m venv venv
```

Ative o ambiente virtual:

- Windows:
```bash
venv\Scripts\activate
```

- Linux/macOS:
```bash
source venv/bin/activate
```

### 3. Instalar as Dependências

Instale as dependências do projeto com o comando:

```bash
pip install -r requirements.txt
```

### 4. Configurar as Variáveis de Ambiente

Crie um arquivo .env na raiz do projeto e preencha as variáveis de ambiente necessárias para a configuração do banco de dados e do superusuário. Tem um exemplo de .env no diretório chamado '.env.example':

### 5. Aplicar as Migrações

Rode as migrações para criar as tabelas do banco de dados. Isso também criará automaticamente o superusuário, se ele não existir, utilizando as variáveis de ambiente configuradas no .env:

```bash
python manage.py migrate
```

### 6. Rodar o Servidor Local e Celery

Agora você pode rodar o servidor de desenvolvimento do Django e iniciar as tarefas assíncronas com Celery:

#### Rodar o Servidor Django

Para rodar o servidor local do Django, use o comando:

```bash
python manage.py runserver
```

#### Redis Container

O Celery usa o Redis como o broker de mensagens. Portanto, é necessário ter um container Redis rodando para o Celery funcionar corretamente.

Caso você esteja utilizando Docker, você pode rodar um container Redis com o seguinte comando:

```bash
docker run --name redis -p 6379:6379 -d redis
```

#### Rodar a Celery

O Celery é responsável por rodar tarefas assíncronas em segundo plano, e o Celery Beat gerencia a execução periódica dessas tarefas.

Em um **terminal separado**, certifique-se de que esteja com o ambiente virtual(venv) ativo. Execute:

```bash
celery -A project worker --loglevel=info --pool=solo
```

#### Rodar a Celery Beat

**Em outro terminal separado**, certifique-se de que esteja com o ambiente virtual(venv) ativo. Execute:

```bash
celery -A project beat --loglevel=info
```

