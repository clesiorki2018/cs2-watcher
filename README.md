<!--
Copyright 2026 Clesiorki
SPDX-License-Identifier: Apache-2.0
-->

# CS2 Watcher

Ferramenta de acessibilidade para Counter-Strike 2 que automatiza holds de teclado, alterna o movimento lateral e aplica `CTRL` temporario no clique.

O projeto separa a regra de negocio da integracao com teclado, mouse e hotkeys, mantendo a configuracao centralizada e a logica principal em `AccessibilityWatcher`.

## Recursos

- `F8`: ativa ou desativa o modo principal.
- `F7`: ativa ou desativa o movimento lateral automatico.
- `ESC`: encerra o watcher.
- Hold continuo de `W` enquanto o modo principal esta ativo.
- Hold lateral alternado automaticamente entre `D` e `A`.
- Alternancia lateral com intervalo variavel entre `0.5s` e `1.0s` por padrao.
- Ao clicar, solta `W/A/D`, pressiona `CTRL` por `0.8s` e restaura o movimento.
- Debounce para evitar acionamentos duplicados de hotkeys e cliques.
- Threads separadas para reaplicar `W` e alternar `A/D` sem conflito.

## Estrutura

```text
.
|-- watcher.py                 # ponto de entrada da aplicacao
|-- cs2_watcher.sh             # script local que carrega .env e executa com sudo
|-- .env.example               # modelo de configuracao local
|-- LICENSE                    # licenca Apache 2.0
|-- NOTICE                     # avisos de copyright e marca
|-- cs2watcher/
|   |-- config.py              # configuracao de teclas, hotkeys e tempos
|   |-- hotkeys.py             # listener de hotkeys fisicas
|   |-- io.py                  # integracao com teclado e feedback sonoro
|   `-- watcher.py             # orquestracao do comportamento principal
|-- docs/
|   |-- classes.puml
|   |-- componentes.puml
|   |-- estados.puml
|   |-- sequencia.puml
|   |-- classes.png
|   |-- componentes.png
|   |-- estados.png
|   `-- sequencia.png
`-- PROMPT_PLANTUML.md         # prompt usado para gerar os diagramas
```

## Requisitos

- Linux.
- Python 3.
- Permissao para capturar mouse/hotkeys e injetar teclas.
- Bibliotecas Python:
  - `keyboard`
  - `pynput`
- Para visualizar ou exportar diagramas:
  - Java
  - PlantUML
  - Graphviz (`dot`)

## Configuracao do Ambiente

Entre na pasta do projeto e crie um ambiente virtual:

```bash
cd /home/seu-usuario/projetos/cs2
python3 -m venv .venvcs2
```

Ative o ambiente e instale as dependencias:

```bash
. .venvcs2/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Copie o modelo de ambiente e ajuste os caminhos da sua maquina:

```bash
cp .env.example .env
```

Exemplo de `.env` local:

```dotenv
CS2_WATCHER_PROJECT_DIR=/home/seu-usuario/projetos/cs2
CS2_WATCHER_VENV_DIR=/home/seu-usuario/projetos/cs2/.venvcs2
CS2_WATCHER_PYTHON_BIN=/home/seu-usuario/projetos/cs2/.venvcs2/bin/python
CS2_WATCHER_USE_SUDO=1
CS2_WATCHER_SUDO_BIN=sudo
```

Garanta permissao de execucao no launcher:

```bash
chmod +x cs2_watcher.sh
```

Se quiser chamar de qualquer lugar do sistema, crie um link simbolico em um
diretorio do `PATH`, por exemplo:

```bash
mkdir -p ~/.local/bin
ln -s /home/seu-usuario/projetos/cs2/cs2_watcher.sh ~/.local/bin/cs2-watcher
```

Confirme que `~/.local/bin` esta no `PATH`:

```bash
echo "$PATH"
```

Se nao estiver, adicione ao arquivo de perfil do seu shell, como `~/.bashrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

As teclas e tempos tambem podem ser sobrescritos no `.env`.

## Execucao

O script local carrega `.env`, entra no diretorio configurado e executa o watcher:

```bash
./cs2_watcher.sh
```

Ele tambem pode ser chamado de outro diretorio ou por um link simbolico em um
diretorio do `PATH`:

```bash
ln -s /home/seu-usuario/projetos/cs2/cs2_watcher.sh ~/.local/bin/cs2-watcher
cs2-watcher
```

Execucao direta, usando as configuracoes padrao do codigo ou variaveis ja exportadas no shell:

```bash
sudo python watcher.py
```

O `sudo` pode ser necessario porque a biblioteca `keyboard` normalmente precisa de permissoes elevadas no Linux para injetar eventos de teclado.

## Configuracao

Os atalhos, teclas e tempos padrao ficam em `cs2watcher/config.py` e podem ser sobrescritos pelo `.env`:

```python
hotkey_main_mode = "f8"
hotkey_side_mode = "f7"
hotkey_exit = "esc"

hold_key_forward = "w"
hold_key_right = "d"
hold_key_left = "a"
effect_key = "ctrl"

action_duration = 0.80
click_debounce = 0.10
hold_refresh_interval = 0.10
hotkey_debounce = 0.30
side_switch_min_interval = 0.50
side_switch_max_interval = 1.00
```

## Diagramas

Os diagramas PlantUML ficam em `docs/`:

- [Componentes](docs/componentes.puml)
- [Classes](docs/classes.puml)
- [Sequencia](docs/sequencia.puml)
- [Estados](docs/estados.puml)

As versoes PNG tambem estao em `docs/`:

- [componentes.png](docs/componentes.png)
- [classes.png](docs/classes.png)
- [sequencia.png](docs/sequencia.png)
- [estados.png](docs/estados.png)

Para gerar os PNGs novamente:

```bash
plantuml -tpng docs/*.puml
```

## Fluxo principal

1. O usuario executa `watcher.py`.
2. A aplicacao cria o `AccessibilityWatcher`, o listener de mouse e o `HotkeyListener`.
3. Ao pressionar `F8`, o modo principal e ativado.
4. O watcher pressiona `W` e, se o movimento lateral estiver ativo, pressiona `D`.
5. Uma thread dedicada mantem `W` pressionado enquanto `CTRL` nao esta ativo.
6. Quando o intervalo lateral vence, o watcher alterna entre `A` e `D` e agenda o proximo intervalo.
7. Ao clicar, o watcher solta `W/A/D`, pressiona `CTRL` por `0.8s` e restaura `W` e a lateral.
8. Ao pressionar `ESC`, a aplicacao encerra e solta todas as teclas.

## Observacoes

Este projeto automatiza entrada de teclado/mouse. Use apenas em ambientes permitidos e respeite as regras do jogo, plataforma ou servidor onde for executar.

## Licenca e Marca

Este projeto e licenciado sob a Apache License, Version 2.0. Consulte
[LICENSE](LICENSE) para os termos completos.

Clesiorki e uma marca registrada de seu respectivo titular. Consulte
[NOTICE](NOTICE) para os avisos de copyright e marca.
