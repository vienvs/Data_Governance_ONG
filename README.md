# Sistema de Gestão para ONG de Adoção de Animais

Aplicação acadêmica (PUC-SP, Banco de Dados SQL e NoSQL) que centraliza o cadastro de usuários, animais, adoções e castrações de uma ONG, substituindo o processo manual baseado em Google Forms e Excel.

**Stack:** Python 3.11+, SQLite (módulo `sqlite3` nativo), Streamlit, bcrypt

## Sumário

- [Como tudo se integra](#como-tudo-se-integra)
- [Passo a passo para rodar](#passo-a-passo-para-rodar)
- [Contas de teste](#contas-de-teste)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Diagrama ER](#diagrama-er)
- [Documentação e relatório](#documentação-e-relatório)

## Como tudo se integra

A aplicação segue uma arquitetura em camadas. O fluxo de uma ação (por exemplo, aprovar uma adoção) atravessa as camadas de cima para baixo:

```
Interface Streamlit    views/*.py         o que o usuario ve e clica
        |
        v
Sessao / RBAC          app/session.py     quem esta logado e o que pode acessar
        |
        v
Servicos               services/*.py      regras de negocio (validacoes, decisoes)
        |
        v
Repositorios           repositories/*.py  SQL parametrizado (CRUD)
        |
        v
Conexao                db/connection.py   abre o SQLite, ativa FKs, transacoes
        |
        v
Banco SQLite           ong_adocao.db      tabelas, indices, view (db/schema.sql)
```

Pontos-chave da integração:

1. **`app/main.py` é o ponto de entrada.** Ele inicializa o banco (cria as tabelas se não existirem), lê quem está logado pela sessão e monta o menu lateral conforme o perfil (RBAC). Cada item do menu chama a função `render()` de uma página em `views/`.
2. **As páginas (`views/`) nunca falam com o banco diretamente.** Elas chamam funções dos serviços (`services/`), passando uma conexão obtida em `db/connection.py`.
3. **Os serviços aplicam as regras** e usam os repositórios (`repositories/`) para executar o SQL. Toda query é parametrizada (placeholders `?`), prevenindo injeção de SQL.
4. **O banco é a última linha de defesa.** Restrições `CHECK`, chaves estrangeiras e o índice único parcial garantem a integridade mesmo que a aplicação falhe.
5. **`app/config.py` lê o arquivo `.env`**, então nenhuma senha ou caminho fica fixo no código.

## Passo a passo para rodar

### 1. Pré-requisitos
- Python 3.11 ou superior (com "Add to PATH" marcado na instalação).
- Não é preciso instalar servidor de banco: o SQLite vem embutido no Python.

### 2. Configurar o ambiente

Na pasta do projeto, abra o terminal:

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Abra o `.env` e defina o `CODIGO_ACESSO_ONG` (qualquer valor; é o que cria contas de administrador). Os demais campos podem ficar como estão.

### 3. Criar o banco com dados de teste

```cmd
python init_db.py
```

Esse script recria o `ong_adocao.db`, carrega o schema (`db/schema.sql`) e os dados de teste (`db/seed.sql`), e imprime uma verificação de consistência. Você pode abrir o arquivo `ong_adocao.db` no DB Browser for SQLite para inspecionar os dados.

### 4. Rodar a aplicação

```cmd
streamlit run app/main.py
```

A aplicação abre em `http://localhost:8501`.

## Contas de teste

Todas as contas do seed usam a senha `senha123`.

| Perfil | E-mail | Observação |
|--------|--------|------------|
| Administrador | `admin@ong.org` | Acessa o painel administrativo completo |
| Usuário comum | `maria@email.com` | Perfil de adotante aprovado, com adoção concluída |
| Usuário comum | `joao@email.com` | Perfil de adotante em análise |
| Usuário comum | `ana@email.com` | Perfil aprovado, com solicitação reprovada e castração |

Para criar um novo administrador, cadastre-se informando o `CODIGO_ACESSO_ONG` definido no seu `.env`.

## Estrutura do projeto

```
app/
  main.py            ponto de entrada Streamlit (roteamento e RBAC)
  config.py          le o .env
  session.py         sessao e controle de acesso
views/               paginas da interface (uma render() por tela)
  auth.py            login e cadastro
  catalogo.py        catalogo de animais (clientes)
  perfil_dono.py     complemento do perfil de adotante
  adocao.py          solicitar adocao e minhas solicitacoes
  castracao.py       solicitar castracao e minhas solicitacoes
  painel_admin.py    painel do admin (documentos, CRUD, adocoes, agenda, auditoria)
services/            regras de negocio
repositories/        acesso a dados (SQL parametrizado)
db/
  connection.py      conexao sqlite3 (PRAGMA foreign_keys=ON, transacoes)
  schema.sql         tabelas, indices, view
  seed.sql           dados de teste
models/entities.py   dataclasses e enums
docs/
  diagrama_er.dbml   fonte do diagrama ER (dbdiagram.io)
  RELATORIO.md       rascunho do relatorio academico
init_db.py           cria e popula o banco
requirements.txt
.env.example
```

## Diagrama ER

O arquivo `docs/diagrama_er.dbml` contém a definição do diagrama em DBML. Para gerar a imagem, acesse https://dbdiagram.io, cole o conteúdo do arquivo e exporte como PNG ou PDF.

## Documentação e relatório

O rascunho do relatório acadêmico está em `docs/RELATORIO.md`, com as seções Introdução, Fundamentação Teórica, Metodologia, Resultados e Discussão, Aplicação no Streamlit, Conclusões e Referências. Os marcadores `[Figura N - ...]` indicam onde inserir as capturas de tela antes da entrega final.

## Observações técnicas

- Chaves estrangeiras no SQLite não são aplicadas por padrão; a aplicação executa `PRAGMA foreign_keys = ON` em toda conexão (`db/connection.py`).
- Segurança: senhas com hash bcrypt e salt; SQL sempre parametrizado; código de acesso de admin lido de variável de ambiente.
- Integridade crítica: o índice único parcial `uq_uma_adocao_aprovada_por_animal` garante, no nível do banco, no máximo uma adoção aprovada por animal.
- IA generativa foi usada como apoio na construção da aplicação; a modelagem e as decisões técnicas são de autoria do aluno, com base nos conteúdos da disciplina.
