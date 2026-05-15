# CS2 Watcher

Ferramenta de acessibilidade para Counter-Strike 2 que automatiza holds de teclado e aplica um efeito temporario de `CTRL` ao clicar com o mouse.

O projeto separa a regra de negocio da integracao com teclado, mouse e hotkeys, mantendo a configuracao centralizada e a logica principal em `AccessibilityWatcher`.

## Recursos

- `F8`: ativa ou desativa o modo principal.
- `F7`: ativa ou desativa o movimento lateral automatico.
- `ESC`: encerra o watcher.
- Hold continuo de `W` enquanto o modo principal esta ativo.
- Hold lateral alternado entre `D` e `A` apos cada clique aceito.
- Ao clicar, solta `W/A/D`, pressiona `CTRL` por um tempo configurado e restaura o movimento.
- Debounce para evitar acionamentos duplicados de hotkeys e cliques.
- Thread de refresh para reaplicar holds artificiais quando necessario.

## Estrutura

```text
.
|-- watcher.py                 # ponto de entrada da aplicacao
|-- cs2_watcher.sh             # script local que carrega .env e executa com sudo
|-- .env.example               # modelo de configuracao local
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
- Permissao para capturar mouse/teclado e injetar teclas.
- Bibliotecas Python:
  - `keyboard`
  - `pynput`
- Para visualizar ou exportar diagramas:
  - Java
  - PlantUML
  - Graphviz (`dot`)

Instalacao das dependencias Python:

```bash
python -m pip install -r requirements.txt
```

## Configuracao Local

Copie o modelo de ambiente e ajuste os caminhos da sua maquina:

```bash
cp .env.example .env
```

O `.env` real fica fora do Git e pode conter caminhos locais, como:

```dotenv
CS2_WATCHER_PROJECT_DIR=/home/seu-usuario/projetos/cs2
CS2_WATCHER_VENV_DIR=/home/seu-usuario/projetos/cs2/.venvcs2
CS2_WATCHER_PYTHON_BIN=/home/seu-usuario/projetos/cs2/.venvcs2/bin/python
CS2_WATCHER_USE_SUDO=1
CS2_WATCHER_SUDO_BIN=sudo
```

As teclas e tempos tambem podem ser sobrescritos no `.env`.

## Execucao

O script local carrega `.env`, entra no diretorio configurado e executa o watcher:

```bash
./cs2_watcher.sh
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

action_duration = 0.70
click_debounce = 0.10
hold_refresh_interval = 0.10
hotkey_debounce = 0.30
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
5. Ao clicar, o watcher aplica debounce, solta `W/A/D`, pressiona `CTRL` e agenda um timer.
6. Quando o timer termina, o watcher solta `CTRL`, restaura `W` e alterna a lateral entre `A` e `D`.
7. Ao pressionar `ESC`, a aplicacao encerra e solta todas as teclas.

## Observacoes

Este projeto automatiza entrada de teclado/mouse. Use apenas em ambientes permitidos e respeite as regras do jogo, plataforma ou servidor onde for executar.
