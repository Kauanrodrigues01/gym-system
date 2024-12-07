# **Aplicação de Gerenciamento de Alunos de uma academia**

A aplicação foi desenvolvida para atender às necessidades de administração de academias, proporcionando controle eficiente sobre os dados dos alunos, pagamentos e relatórios. Sua arquitetura modular e escalável facilita a adição de novas funcionalidades e adaptações.

---

## **Funcionalidades Principais**

### **1. CRUD de Alunos**
- Criação, visualização, atualização e exclusão de alunos.
- Dados detalhados como informações de contato e status de pagamento.

### **2. Automatização de Tarefas**
- **Celery** é utilizado para:
  - Verificação diária de pagamentos atrasados (alunos com mais de um mês sem pagar).
  - Geração de relatórios diários ao final do dia.
- **Redis** atua como broker para filas de tarefas, garantindo alta performance.

### **3. Gerenciamento Financeiro**
- Geração de gráficos financeiros com **Pandas** e **Plotly**, detalhando:
  - Dinheiro recebido por mês.
  - Outras métricas importantes para a academia.

### **4. Relatórios em PDF**
- Utilização de **xhtml2pdf** e **reportlab** para criar relatórios estilizados.
- Relatórios gerais e diários podem ser baixados pelo administrador.

### **5. Paginação e Filtros**
- Gerenciamento eficiente de grandes volumes de dados com paginação e filtros otimizados.

---

## **Tecnologias e Bibliotecas Utilizadas**

### **Backend**
- **Django** e **Django Rest Framework**: Estruturação da aplicação e lógica de negócios.

### **Automação e Fila de Tarefas**
- **Celery**: Processamento assíncrono de tarefas.
- **Redis**: Armazenamento em cache e fila de mensagens.

### **Análise e Visualização**
- **Pandas**: Manipulação e análise de dados.
- **Plotly**: Geração de gráficos interativos.

### **Relatórios**
- **xhtml2pdf**, **reportlab** e **pydyf**: Criação de relatórios em PDF.

### **Segurança**
- **cryptography** e **pyhanko**: Criptografia e assinaturas digitais.

### **Testes e Cobertura**
- **pytest** e **pytest-django**: Automação de testes.
- **coverage**: Análise de cobertura de código.

---

## **Benefícios para a Academia**

### **Gestão Simplificada**
- Centraliza informações sobre alunos e pagamentos.
- Automatiza tarefas repetitivas, reduzindo erros manuais.

### **Tomada de Decisão Baseada em Dados**
- Relatórios detalhados e gráficos ajudam no planejamento financeiro e operacional.

### **Eficiência Administrativa**
- Geração de relatórios diários e mensais sem necessidade de intervenção manual.

### **Flexibilidade e Escalabilidade**
- Paginação e automação permitem atender academias de diferentes portes.

---

## **Exemplo de Fluxo**
1. Um aluno realiza um pagamento.
2. A aplicação atualiza automaticamente o status do aluno.
3. Diariamente, a aplicação verifica pagamentos atrasados e envia notificações.
4. No final do dia:
   - Gráficos financeiros são gerados.
   - Relatórios em PDF ficam disponíveis para download pelo administrador.


## Passos para Rodar o Projeto

### 1. Clonar o Repositório

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

Crie um arquivo .env na raiz do projeto e preencha as variáveis de ambiente necessárias para a configuração do banco de dados e do superusuário. Exemplo de como configurar o arquivo .env:

```bash
# Configuração do email, USE ESTE MESMO, pois é apenas um email de teste
EMAIL_HOST_PASSWORD = 'yzuy uyju jxpo faxf'

# Configurações do superusuário (serão usadas para criar o superusuário automaticamente após a migração)
DJANGO_SUPERUSER_CPF = 'seu cpf'
DJANGO_SUPERUSER_EMAIL = 'seu email'
DJANGO_SUPERUSER_PASSWORD = 'sua senha'

```

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

