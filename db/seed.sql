-- Dados de teste (seed) do Sistema de Gestao ONG de Adocao.
-- Senha de todos os usuarios de teste: "senha123".
-- Os hashes bcrypt abaixo foram pre-computados (cada um com salt distinto).
--
-- Nota de consistencia: os 2 animais adotados possuem, cada um, exatamente
-- uma adocao 'aprovado' (total de 2 aprovadas), mais 2 'em_analise' e 1
-- 'reprovado'. Isso difere do enunciado original (que citava 1 aprovada),
-- mas e necessario para manter a integridade entre animal adotado e adocao
-- aprovada.

-- Limpeza para permitir recarregar o seed sem duplicar dados.
DELETE FROM log_auditoria;
DELETE FROM solicitacao_castracao;
DELETE FROM solicitacao_adocao;
DELETE FROM animal;
DELETE FROM dono;
DELETE FROM usuario;

-- Usuarios: 1 administrador e 3 usuarios comuns em etapas diferentes.
INSERT INTO usuario (id, nome, email, senha_hash, data_nascimento, tipo) VALUES
 (1, 'Administrador ONG', 'admin@ong.org',  '$2b$12$yJgKsFhfhTzHrswxzM/aG.GsKOzXudY7eQbMfCcJ6R3G8mYI1y5ri', '1985-03-10', 'admin'),
 (2, 'Maria Silva',       'maria@email.com', '$2b$12$hWTiG1ny12lIONroiatAEeFFaZU6TtP9Fp.lIzp9pZaywbrYC6yKK', '1995-07-22', 'comum'),
 (3, 'Joao Pereira',      'joao@email.com',  '$2b$12$Vww3/tq8NaN17sou6IlUP.nYIRyOi4qB2oFMIk7I5WPzBY9j/eNwe', '1990-11-05', 'comum'),
 (4, 'Ana Souza',         'ana@email.com',   '$2b$12$bKXn/wZV93EmQXwRfUbqPOMOQxXXtcp9SXNp8rdPC9CN8VIEDZ5ny', '2000-01-30', 'comum');

-- Donos: perfis de adotante em etapas diferentes. Os caminhos de imagem sao
-- ficticios de proposito: o painel exibe "imagem indisponivel" sem quebrar.
INSERT INTO dono (id, usuario_id, cpf, telefone, endereco, tipo_residencia, tem_tela,
                  caminho_doc, caminho_comprovante, caminho_tela, status_aprovacao) VALUES
 (1, 2, '12345678901', '(12) 90000-0001', 'Rua das Flores, 100 - Sao Jose dos Campos/SP', 'casa', 1,
     'images/Identidade Maria.webp', 'images/Comprovante de Residencia.jpg', 'images/Com tela.jpg', 'aprovado'),
 (2, 3, '23456789012', '(12) 90000-0002', 'Av. Brasil, 250 - Sao Jose dos Campos/SP', 'apartamento', 1,
     'images/Identidade Joao.webp', 'images/Comprovante de Residencia.jpg', 'images/Com tela 2.webp', 'em_analise'),
 (3, 4, '34567890123', '(12) 90000-0003', 'Rua Verde, 75 - Sao Jose dos Campos/SP', 'casa', 1,
     'images/Identidade Maria.webp', 'images/Comprovante de Residencia.jpg', 'images/Com tela.jpg', 'aprovado');

-- Animais: 3 caes disponiveis, 3 gatos disponiveis, 2 adotados.
INSERT INTO animal (id, nome, especie, sexo, idade, raca, descricao, status, caminho_foto) VALUES
 (1, 'Rex',     'cao',  'macho', 3, 'SRD',      'Docil e brincalhao.',        'disponivel', 'images/Cachorro 1.jpg'),
 (2, 'Thor',    'cao',  'macho', 5, 'Labrador', 'Calmo, bom com criancas.',   'disponivel', 'images/Cachorro 2.jpg'),
 (3, 'Bidu',    'cao',  'femea', 1, 'SRD',      'Filhote cheia de energia.',  'disponivel', 'images/Cachorro 3.jpg'),
 (4, 'Mimi',    'gato', 'femea', 2, 'SRD',      'Independente e carinhosa.',  'disponivel', 'images/Gato 1.jpg'),
 (5, 'Frajola', 'gato', 'macho', 4, 'Siames',   'Gosta de colo.',             'disponivel', 'images/Gato 2.jpg'),
 (6, 'Nina',    'gato', 'femea', 1, 'SRD',      'Curiosa e ativa.',           'disponivel', 'images/Gato 3.jpg'),
 (7, 'Bob',     'cao',  'macho', 6, 'Poodle',   'Adotado, companheiro fiel.', 'adotado',    'images/Cachorro 4.jpg'),
 (8, 'Lola',    'gato', 'femea', 3, 'SRD',      'Adotada, muito tranquila.',  'adotado',    'images/Gato 4.jpg');

-- Adocoes: 2 aprovadas (uma por animal adotado), 2 em analise, 1 reprovada.
INSERT INTO solicitacao_adocao
 (id, dono_id, animal_id, status, respostas_questionario, aceite_termo, observacoes_admin, decidido_por, decidido_em) VALUES
 (1, 1, 7, 'aprovado',
     '{"Todos de acordo?": "Sim", "Por que adotar?": "Quero um companheiro."}', 1,
     'Documentacao conferida e aprovada.', 1, datetime('now')),
 (2, 3, 8, 'aprovado',
     '{"Todos de acordo?": "Sim", "Por que adotar?": "Amo gatos."}', 1,
     'Tudo certo com a adotante.', 1, datetime('now')),
 (3, 2, 1, 'em_analise',
     '{"Todos de acordo?": "Sim", "Por que adotar?": "Quero adotar o Rex."}', 0,
     NULL, NULL, NULL),
 (4, 1, 2, 'em_analise',
     '{"Todos de acordo?": "Sim", "Por que adotar?": "Tenho espaco para o Thor."}', 0,
     NULL, NULL, NULL),
 (5, 3, 4, 'reprovado',
     '{"Todos de acordo?": "Nao", "Por que adotar?": "Indeciso."}', 0,
     'Familia nao esta totalmente de acordo.', 1, datetime('now'));

-- Castracoes: 1 em analise e 1 aprovada com data agendada.
INSERT INTO solicitacao_castracao
 (id, usuario_id, nome_pet, especie, sexo, idade_pet, nome_tutor, telefone, endereco, status, data_agendada, decidido_por, decidido_em) VALUES
 (1, 2, 'Pingo',  'cao',  'macho', 2, 'Maria Silva', '(11) 90000-0001', 'Rua das Flores, 100', 'em_analise', NULL, NULL, NULL),
 (2, 4, 'Mel',    'gato', 'femea', 3, 'Ana Souza',   '(11) 90000-0003', 'Rua Verde, 75',       'aprovado', date('now','+7 day'), 1, datetime('now'));

-- Auditoria: exemplos de eventos.
INSERT INTO log_auditoria (usuario_id, acao, entidade, registro_id, detalhe) VALUES
 (1, 'adocao_aprovada',  'solicitacao_adocao',    1, 'Animal 7 adotado'),
 (1, 'adocao_aprovada',  'solicitacao_adocao',    2, 'Animal 8 adotado'),
 (1, 'castracao_aprovado','solicitacao_castracao', 2, 'Agendada');

-- Verificacao de consistencia (deve retornar 0 linhas):
-- SELECT a.id FROM animal a
-- LEFT JOIN solicitacao_adocao sa ON sa.animal_id = a.id AND sa.status='aprovado'
-- WHERE a.status='adotado' GROUP BY a.id HAVING COUNT(sa.id) != 1;
