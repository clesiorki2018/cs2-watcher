# Prompt PlantUML do projeto CS2 Watcher

Use este prompt para gerar diagramas PlantUML fiéis ao projeto.

```text
Voce e um arquiteto de software senior. Analise o projeto Python "CS2 Watcher" e gere diagramas PlantUML claros, objetivos e consistentes com Clean Architecture, SOLID e Clean Code.

Contexto do projeto:
- O projeto automatiza acessibilidade de teclado/mouse para Counter-Strike 2.
- O ponto de entrada e `watcher.py`.
- `watcher.py` cria um `AccessibilityWatcher`, um listener de mouse do `pynput.mouse` e um `HotkeyListener`.
- `AccessibilityWatcher` coordena o modo principal, movimento lateral e efeito de clique.
- `WatcherConfig` centraliza hotkeys, teclas e tempos.
- `HotkeyListener` escuta teclas fisicas com `pynput.keyboard.Listener`.
- `KeyboardController` isola chamadas da biblioteca externa `keyboard`.
- `BeepService` fornece feedback sonoro via terminal bell.
- O script `cs2_watcher.sh` carrega `.env`, resolve caminhos locais e executa `watcher.py` com sudo.

Arquivos e responsabilidades:

1. `watcher.py`
- Funcao `main()`.
- Constroi `AccessibilityWatcher.build_default()`.
- Exibe as hotkeys configuradas.
- Cria `mouse.Listener(on_click=watcher.handle_click)`.
- Cria `HotkeyListener(config, watcher.toggle_main_mode, watcher.toggle_side_movement)`.
- Inicia listeners.
- Aguarda `hotkey_listener.wait()`.
- No `finally`, chama `watcher.shutdown()`, para o listener de mouse e para o listener de hotkeys.

2. `cs2watcher/config.py`
- Classe `WatcherConfig`, dataclass congelada.
- Campos:
  - `hotkey_main_mode = "f8"`
  - `hotkey_side_mode = "f7"`
  - `hotkey_exit = "esc"`
  - `hold_key_forward = "w"`
  - `hold_key_right = "d"`
  - `hold_key_left = "a"`
  - `effect_key = "ctrl"`
  - `action_duration = 0.70`
  - `click_debounce = 0.10`
  - `hold_refresh_interval = 0.10`
  - `hotkey_debounce = 0.30`
- Propriedade `initial_side_hold_key`, que retorna `hold_key_right`.

3. `cs2watcher/io.py`
- Classe `BeepService`.
  - `activated()` imprime um terminal bell.
  - `deactivated()` imprime dois terminal bells.
- Classe `KeyboardController`.
  - Recebe `WatcherConfig`.
  - `press_forward()` pressiona `hold_key_forward`.
  - `release_forward()` solta `hold_key_forward`.
  - `press_effect()` pressiona `effect_key`.
  - `release_effect()` solta `effect_key`.
  - `press_key(key)` pressiona uma tecla generica.
  - `release_side_keys()` solta `hold_key_right` e `hold_key_left`.
  - `release_all()` solta efeito, frente e laterais.

4. `cs2watcher/hotkeys.py`
- Classe `HotkeyListener`.
- Recebe `WatcherConfig`, callback `on_main_mode` e callback `on_side_movement`.
- Usa `pynput.keyboard.Listener(on_press=self._handle_press)`.
- Mantem `stop_event` e `last_trigger_time`.
- `start()` inicia o listener.
- `wait()` aguarda `stop_event`.
- `stop()` sinaliza parada e interrompe o listener.
- `_handle_press(key)`:
  - se a tecla for `exit_key`, sinaliza parada e retorna `False`.
  - se for `main_mode_key` e passar debounce, chama `on_main_mode()`.
  - se for `side_movement_key` e passar debounce, chama `on_side_movement()`.
- `_can_trigger(action)` aplica debounce por acao usando `time.monotonic()`.
- `_key_from_name(name)` converte nome para `pynput_keyboard.Key`.

5. `cs2watcher/watcher.py`
- Classe `AccessibilityWatcher`.
- Dependencias injetadas:
  - `WatcherConfig`
  - `KeyboardController`
  - `BeepService`
- Estado:
  - `main_mode`
  - `side_movement_enabled`
  - `current_side_hold_key`
  - `release_timer`
  - `last_click_time`
  - `action_running`
  - `stop_event`
  - `lock`
  - `hold_refresh_thread`
- `build_default()` cria configuracao, controlador de teclado e beep service.
- `toggle_main_mode()` alterna o modo principal.
- `toggle_side_movement()` alterna o movimento lateral.
- `handle_click(_x, _y, _button, pressed)` executa o efeito de CTRL em cliques aceitos.
- `shutdown()` para tarefas de fundo e solta todas as teclas.
- `_activate_main_mode()`:
  - pressiona W.
  - se o movimento lateral estiver ativo, pressiona a tecla lateral inicial.
  - emite beep de ativacao.
- `_deactivate_main_mode()`:
  - cancela timer.
  - solta todas as teclas.
  - limpa estado.
  - emite beep de desativacao.
- `_enable_side_movement()`:
  - se o modo principal estiver ativo e nao houver acao em andamento, pressiona a tecla lateral atual ou inicial.
  - emite beep de ativacao.
- `_disable_side_movement()`:
  - solta teclas laterais.
  - emite beep de desativacao.
- `_start_click_effect()`:
  - marca `action_running`.
  - cancela timer anterior.
  - guarda tecla lateral anterior.
  - solta W.
  - solta laterais.
  - pressiona CTRL.
  - agenda `threading.Timer(action_duration, _finish_click_effect, previous_side_key)`.
- `_finish_click_effect(previous_side_key)`:
  - solta CTRL.
  - se modo principal ainda estiver ativo, pressiona W e restaura movimento lateral.
  - limpa `action_running` e `release_timer`.
- `_restore_side_movement(previous_side_key)`:
  - se movimento lateral estiver desativado, solta laterais.
  - senao alterna A/D com `_get_next_side_key`.
- `_hold_refresh_loop()`:
  - enquanto `stop_event` nao estiver ativo, se modo principal estiver ativo e sem acao em andamento, reaplica W e tecla lateral atual.
  - dorme `hold_refresh_interval`.
- `_get_next_side_key(previous_key)` alterna entre D e A; se desconhecida, retorna tecla inicial.
- `_should_ignore_click(now)` aplica debounce de clique.

Gere obrigatoriamente:

1. Um diagrama de componentes PlantUML mostrando:
- `watcher.py` como entrada da aplicacao.
- Pacote `cs2watcher`.
- `AccessibilityWatcher`.
- `WatcherConfig`.
- `HotkeyListener`.
- `KeyboardController`.
- `BeepService`.
- Bibliotecas externas `pynput.mouse`, `pynput.keyboard`, `keyboard`, `threading` e `time`.
- Dependencias direcionais entre componentes.

2. Um diagrama de classes PlantUML mostrando:
- Atributos principais das classes.
- Metodos publicos principais.
- Relacoes de composicao/dependencia.
- Callbacks do `HotkeyListener` para `AccessibilityWatcher`.

3. Um diagrama de sequencia PlantUML para o fluxo:
- Usuario pressiona F8.
- `HotkeyListener` chama `AccessibilityWatcher.toggle_main_mode()`.
- O watcher ativa modo principal, pressiona W, pressiona D se movimento lateral estiver ativo e emite beep.
- Usuario clica com mouse.
- `mouse.Listener` chama `AccessibilityWatcher.handle_click(...)`.
- O watcher aplica debounce, solta W/A/D, pressiona CTRL, agenda timer.
- Timer chama `_finish_click_effect`, solta CTRL, restaura W e alterna A/D.

4. Um diagrama de estados PlantUML para `AccessibilityWatcher` contendo:
- `Desativado`.
- `ModoPrincipalAtivo`.
- `MovimentoLateralAtivo`.
- `MovimentoLateralDesativado`.
- `EfeitoCliqueEmExecucao`.
- Transicoes por F8, F7, clique aceito, timer finalizado e shutdown.

Regras de saida:
- Responda apenas com codigo PlantUML em blocos separados.
- Cada bloco deve iniciar com `@startuml` e terminar com `@enduml`.
- Use nomes em portugues, mas preserve nomes reais de classes e metodos.
- Evite inventar classes que nao existem.
- Quando representar bibliotecas externas, use estereotipo `<<external>>`.
- Use notas curtas somente onde ajudarem a explicar concorrencia, debounce ou timers.
```
