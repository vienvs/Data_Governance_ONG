-- Sistema de Gestao para ONG de Adocao de Animais
-- Esquema do banco de dados (SQLite)
--
-- O SQLite nao aplica chaves estrangeiras por padrao. A aplicacao executa
-- "PRAGMA foreign_keys = ON;" a cada conexao (ver db/connection.py). Para
-- inspecionar no DB Browser, ative Edit > Preferences > "Enable foreign keys".

-- Tabela usuario: conta de acesso. Email unico; senha sempre como hash.
CREATE TABLE IF NOT EXISTS usuario (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nome            TEXT    NOT NULL,
    email           TEXT    NOT NULL UNIQUE,
    senha_hash      TEXT    NOT NULL,
    data_nascimento TEXT    NOT NULL,
    tipo            TEXT    NOT NULL DEFAULT 'comum'
                            CHECK (tipo IN ('comum','admin')),
    criado_em       TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Tabela dono: extensao 1:1 do usuario (perfil de adotante).
-- usuario_id UNIQUE garante no maximo um perfil por usuario.
-- CPF com 11 digitos numericos e unico.
CREATE TABLE IF NOT EXISTS dono (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id          INTEGER NOT NULL UNIQUE REFERENCES usuario(id),
    cpf                 TEXT    NOT NULL UNIQUE
                                CHECK (length(cpf) = 11 AND
                                       cpf GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
    telefone            TEXT    NOT NULL,
    endereco            TEXT    NOT NULL,
    tipo_residencia     TEXT    NOT NULL
                                CHECK (tipo_residencia IN ('casa','apartamento')),
    tem_tela            INTEGER NOT NULL DEFAULT 0 CHECK (tem_tela IN (0,1)),
    caminho_doc         TEXT    NOT NULL,
    caminho_comprovante TEXT    NOT NULL,
    caminho_tela        TEXT    NOT NULL,
    status_aprovacao    TEXT    NOT NULL DEFAULT 'em_analise'
                                CHECK (status_aprovacao IN ('em_analise','aprovado','reprovado')),
    criado_em           TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Tabela animal: cao ou gato sob gestao da ONG. Idade nao-negativa.
CREATE TABLE IF NOT EXISTS animal (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nome         TEXT    NOT NULL,
    especie      TEXT    NOT NULL CHECK (especie IN ('cao','gato')),
    sexo         TEXT    NOT NULL CHECK (sexo IN ('macho','femea')),
    idade        INTEGER NOT NULL CHECK (idade >= 0),
    raca         TEXT,
    descricao    TEXT,
    status       TEXT    NOT NULL DEFAULT 'disponivel'
                         CHECK (status IN ('disponivel','adotado')),
    caminho_foto TEXT,
    criado_em    TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Tabela solicitacao_adocao: pedido de um dono por um animal.
CREATE TABLE IF NOT EXISTS solicitacao_adocao (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    dono_id                INTEGER NOT NULL REFERENCES dono(id),
    animal_id              INTEGER NOT NULL REFERENCES animal(id),
    data_solicitacao       TEXT    NOT NULL DEFAULT (datetime('now')),
    status                 TEXT    NOT NULL DEFAULT 'em_analise'
                                   CHECK (status IN ('em_analise','aprovado','reprovado')),
    observacoes_admin      TEXT,
    respostas_questionario TEXT    NOT NULL,
    aceite_termo           INTEGER NOT NULL DEFAULT 0 CHECK (aceite_termo IN (0,1)),
    decidido_por           INTEGER REFERENCES usuario(id),
    decidido_em            TEXT
);

-- Tabela solicitacao_castracao: associada ao usuario que registrou.
-- data_agendada guarda a data do procedimento definida pelo admin (agenda).
CREATE TABLE IF NOT EXISTS solicitacao_castracao (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id       INTEGER NOT NULL REFERENCES usuario(id),
    nome_pet         TEXT    NOT NULL,
    especie          TEXT    NOT NULL CHECK (especie IN ('cao','gato')),
    sexo             TEXT    NOT NULL CHECK (sexo IN ('macho','femea')),
    idade_pet        INTEGER NOT NULL CHECK (idade_pet >= 0),
    nome_tutor       TEXT    NOT NULL,
    telefone         TEXT    NOT NULL,
    endereco         TEXT    NOT NULL,
    data_solicitacao TEXT    NOT NULL DEFAULT (datetime('now')),
    data_agendada    TEXT,
    status           TEXT    NOT NULL DEFAULT 'em_analise'
                             CHECK (status IN ('em_analise','aprovado','reprovado')),
    decidido_por     INTEGER REFERENCES usuario(id),
    decidido_em      TEXT
);

-- Tabela log_auditoria: trilha de operacoes sensiveis.
CREATE TABLE IF NOT EXISTS log_auditoria (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id  INTEGER REFERENCES usuario(id),
    acao        TEXT    NOT NULL,
    entidade    TEXT    NOT NULL,
    registro_id INTEGER,
    detalhe     TEXT,
    data_hora   TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Indice unico parcial: impede duas solicitacoes em analise do mesmo par
-- (dono, animal), evitando solicitacoes duplicadas.
CREATE UNIQUE INDEX IF NOT EXISTS uq_adocao_ativa_por_dono_animal
    ON solicitacao_adocao (dono_id, animal_id)
    WHERE status = 'em_analise';

-- Regra critica: no maximo uma adocao aprovada por animal. A segunda aprovacao
-- para o mesmo animal viola o indice e levanta IntegrityError, convertida em
-- AnimalJaAdotadoError pela aplicacao.
CREATE UNIQUE INDEX IF NOT EXISTS uq_uma_adocao_aprovada_por_animal
    ON solicitacao_adocao (animal_id)
    WHERE status = 'aprovado';

-- Indices sobre chaves estrangeiras e campos de status usados em filtros.
CREATE INDEX IF NOT EXISTS idx_dono_usuario_id      ON dono (usuario_id);
CREATE INDEX IF NOT EXISTS idx_dono_status          ON dono (status_aprovacao);
CREATE INDEX IF NOT EXISTS idx_animal_status        ON animal (status);
CREATE INDEX IF NOT EXISTS idx_adocao_dono_id       ON solicitacao_adocao (dono_id);
CREATE INDEX IF NOT EXISTS idx_adocao_animal_id     ON solicitacao_adocao (animal_id);
CREATE INDEX IF NOT EXISTS idx_adocao_status        ON solicitacao_adocao (status);
CREATE INDEX IF NOT EXISTS idx_castracao_usuario_id ON solicitacao_castracao (usuario_id);
CREATE INDEX IF NOT EXISTS idx_castracao_status     ON solicitacao_castracao (status);
CREATE INDEX IF NOT EXISTS idx_auditoria_usuario_id ON log_auditoria (usuario_id);
CREATE INDEX IF NOT EXISTS idx_auditoria_data_hora  ON log_auditoria (data_hora);

-- View consolidada das adocoes aprovadas (relaciona dono e animal).
CREATE VIEW IF NOT EXISTS vw_adocoes_aprovadas AS
SELECT  sa.id                AS solicitacao_id,
        sa.data_solicitacao,
        sa.decidido_em,
        u.id                 AS usuario_id,
        u.nome               AS nome_adotante,
        u.email              AS email_adotante,
        d.cpf,
        d.telefone,
        d.endereco,
        a.id                 AS animal_id,
        a.nome               AS nome_animal,
        a.especie,
        a.sexo,
        a.status             AS status_animal
FROM    solicitacao_adocao sa
JOIN    dono d    ON d.id = sa.dono_id
JOIN    usuario u ON u.id = d.usuario_id
JOIN    animal a  ON a.id = sa.animal_id
WHERE   sa.status = 'aprovado';
