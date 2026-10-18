"""Atualiza a seção de repositórios recentes do README.

Busca os repositórios públicos na API do GitHub, pega os que tiveram
push mais recente e escreve a lista entre os marcadores REPOS:START/END.
"""

import json
import os
import re
import urllib.request
from datetime import datetime
from pathlib import Path

USUARIO = "kleberws"
QUANTIDADE = 5
README = Path(__file__).resolve().parent.parent / "README.md"


def buscar_repos():
    url = f"https://api.github.com/users/{USUARIO}/repos?per_page=100&sort=pushed"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})

    # No Actions o token evita o limite de 60 requisições/hora sem login
    token = os.getenv("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def montar_lista(repos):
    # Ignora forks e o próprio repositório do perfil
    proprios = [r for r in repos if not r["fork"] and r["name"].lower() != USUARIO]
    proprios.sort(key=lambda r: r["pushed_at"], reverse=True)

    linhas = []
    for repo in proprios[:QUANTIDADE]:
        data = datetime.strptime(repo["pushed_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y")
        descricao = repo["description"] or "sem descrição"
        linguagem = f" · {repo['language']}" if repo["language"] else ""
        linhas.append(f"- [{repo['name']}]({repo['html_url']}) — {descricao}{linguagem} · <sub>{data}</sub>")

    return "\n".join(linhas) or "_Nenhum repositório público ainda._"


def main():
    texto = README.read_text(encoding="utf-8")
    lista = montar_lista(buscar_repos())

    novo = re.sub(
        r"(<!-- REPOS:START -->).*?(<!-- REPOS:END -->)",
        lambda m: f"{m.group(1)}\n{lista}\n{m.group(2)}",
        texto,
        flags=re.DOTALL,
    )

    if novo != texto:
        README.write_text(novo, encoding="utf-8")
        print("README atualizado.")
    else:
        print("Nada mudou.")


if __name__ == "__main__":
    main()
