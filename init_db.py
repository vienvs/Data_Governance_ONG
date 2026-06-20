"""Script utilitario para (re)criar o banco ong_adocao.db a partir do schema e seed.

Uso:  python _gerar_db.py
"""
import os
import sqlite3

DB = "ong_adocao.db"

# recria do zero para garantir consistencia
if os.path.exists(DB):
    os.remove(DB)

conn = sqlite3.connect(DB)
conn.execute("PRAGMA foreign_keys = ON")
conn.executescript(open("db/schema.sql", encoding="utf-8").read())
conn.executescript(open("db/seed.sql", encoding="utf-8").read())
conn.commit()

print("Usuarios:", conn.execute("SELECT COUNT(*) FROM usuario").fetchone()[0])
print("Animais:", conn.execute("SELECT COUNT(*) FROM animal").fetchone()[0])
print("Adotados:", conn.execute("SELECT COUNT(*) FROM animal WHERE status='adotado'").fetchone()[0])
print("Adocoes por status:", dict(conn.execute(
    "SELECT status, COUNT(*) FROM solicitacao_adocao GROUP BY status").fetchall()))
print("Castracoes:", conn.execute("SELECT COUNT(*) FROM solicitacao_castracao").fetchone()[0])

inconsistencias = conn.execute(
    "SELECT a.id FROM animal a "
    "LEFT JOIN solicitacao_adocao sa ON sa.animal_id=a.id AND sa.status='aprovado' "
    "WHERE a.status='adotado' GROUP BY a.id HAVING COUNT(sa.id) != 1"
).fetchall()
print("Inconsistencias adotado<->aprovado (deve ser []):", inconsistencias)

print("View vw_adocoes_aprovadas:",
      conn.execute("SELECT nome_animal, nome_adotante FROM vw_adocoes_aprovadas").fetchall())
conn.close()
print("OK - banco gerado:", DB)
