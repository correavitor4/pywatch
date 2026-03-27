import platform
import subprocess
import threading
import os
from textual.app import ComposeResult
from textual.widgets import Label, Button, Input, Switch
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive

class PomodoroWidget(Vertical):
    """Widget para gerenciamento de tempo Pomodoro."""
    
    tempo_restante = reactive(25 * 60)
    sessoes_concluidas = reactive(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rodando = False
        self.atualizador = None
        self.modo = "Foco"
        self.tempos = {"Foco": 25 * 60, "Curta": 5 * 60} # Removido "Longa" daqui
        self.focos_concluidos = 0q

    def compose(self) -> ComposeResult:
        yield Input(placeholder="O que você vai focar agora?", classes="cronometro_nome")
        
        with Vertical(classes="pomodoro_config_container"):
            with Horizontal(classes="pomodoro_config_tempos"):
                yield Label("Foco:", classes="label_pomodoro")
                yield Input(value="25", classes="input_pomodoro_foco", max_length=2)
                yield Label("Short Break:", classes="label_pomodoro")
                yield Input(value="05", classes="input_pomodoro_curta", max_length=2)
            with Horizontal(classes="pomodoro_config_auto"):
                yield Label("Ciclos automáticos", classes="label_pomodoro")
                yield Switch(value=False, classes="switch_auto")
            
        yield Label("FOCO", classes="pomodoro_modo")
        yield Label("25:00", classes="tempo_display")
        yield Label("Sessões: 0", classes="pomodoro_sessoes")
        
        with Horizontal(classes="cronometro_botoes"):
            yield Button("Iniciar", classes="iniciar_pausar", variant="success")
            yield Button("Alternar", classes="alternar", variant="warning")
            yield Button("Zerar", classes="zerar", variant="default")
            yield Button("Resetar", classes="resetar", variant="error")
            yield Button("Remover", classes="remover", variant="error")

    def watch_tempo_restante(self, tempo: int) -> None:
        minutos, segundos = divmod(tempo, 60)
        display = f"{int(minutos):02}:{int(segundos):02}"
        
        label_display = self.query_one(".tempo_display", Label)
        label_display.update(display)
        
        if tempo <= 0 and self.rodando:
            self.disparar_alarme()
            auto = self.query_one(".switch_auto", Switch).value
            self.alternar_modo(auto_start=auto) # Decide se continua sozinho

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.has_class("iniciar_pausar"):
            if self.rodando:
                self.pausar()
            else:
                self.iniciar()
        elif event.button.has_class("alternar"):
            self.alternar_modo(auto_start=False)
        elif event.button.has_class("zerar"):
            self.zerar()
        elif event.button.has_class("resetar"):
            self.resetar()
        elif event.button.has_class("remover"):
            self.pausar()
            self.remove()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Aplica a máscara e atualiza os tempos simultaneamente."""
        if event.input.has_class("input_pomodoro_foco") or event.input.has_class("input_pomodoro_curta"):
            numeros = "".join(filter(str.isdigit, event.value))[:2]
            
            if event.value != numeros:
                event.input.value = numeros
                event.input.cursor_position = len(numeros)
            
            # Força a atualização dos valores internos assim que o usuário digita
            self.atualizar_tempos()
            
            # Se o cronômetro estiver parado, já atualiza o display visual
            if not self.rodando:
                self.tempo_restante = self.tempos[self.modo]

    def formatar_inputs(self) -> None:
        """Aplica o limite visual e o preenchimento de zeros apenas aos inputs existentes."""
        try:
            foco = self.query_one(".input_pomodoro_foco", Input)
            curta = self.query_one(".input_pomodoro_curta", Input)

            if not foco.has_focus:
                # Garante que o valor seja um número entre 0 e 60, formatado com 2 dígitos
                val = "".join(filter(str.isdigit, foco.value))
                foco.value = f"{min(int(val or '0'), 60):02}"
                
            if not curta.has_focus:
                val = "".join(filter(str.isdigit, curta.value))
                curta.value = f"{min(int(val or '0'), 60):02}"
        except Exception:
            # Silencia erros caso os widgets ainda não tenham sido montados
            pass

    def iniciar(self) -> None:
        self.formatar_inputs()
        self.atualizar_tempos()
        if self.tempo_restante <= 0:
            self.tempo_restante = self.tempos[self.modo]
        if self.tempo_restante > 0:
            self.rodando = True
            self.atualizador = self.set_interval(1, self.atualizar_tempo)
            botao = self.query_one(".iniciar_pausar", Button)
            botao.label = "Pausar"
            botao.variant = "warning"

    def pausar(self) -> None:
        self.rodando = False
        if self.atualizador: self.atualizador.pause()
        botao = self.query_one(".iniciar_pausar", Button)
        botao.label = "Retomar"
        botao.variant = "success"

    def zerar(self) -> None:
        self.pausar()
        self.formatar_inputs()
        self.atualizar_tempos()
        self.tempo_restante = self.tempos[self.modo]
        self.query_one(".iniciar_pausar", Button).label = "Iniciar"

    def resetar(self) -> None:
        self.pausar()
        self.focos_concluidos = 0
        self.sessoes_concluidas = 0
        self.modo = "Foco"
        self.query_one(".pomodoro_sessoes", Label).update("Sessões: 0")
        self.query_one(".pomodoro_modo", Label).update("FOCO")
        self.formatar_inputs()
        self.atualizar_tempos()
        self.tempo_restante = self.tempos["Foco"]
        self.query_one(".iniciar_pausar", Button).label = "Iniciar"
        self.query_one(".iniciar_pausar", Button).variant = "success"

    def alternar_modo(self, auto_start=False) -> None:
        """Muda o modo estritamente entre Foco e Curta (sem intervalo longo)."""
        self.pausar()

        # Lógica simplificada: Se era foco, vai para curta. Se era curta, volta para foco.
        if self.modo == "Foco":
            self.focos_concluidos += 1
            self.sessoes_concluidas = self.focos_concluidos
            self.modo = "Curta"
        else:
            self.modo = "Foco"

        # Atualiza a interface
        self.query_one(".pomodoro_sessoes", Label).update(f"Sessões: {self.sessoes_concluidas}")
        self.formatar_inputs()
        self.atualizar_tempos()
        self.tempo_restante = self.tempos[self.modo]
        self.query_one(".pomodoro_modo", Label).update(self.modo.upper())
        
        # Reseta o botão para o estado inicial
        botao = self.query_one(".iniciar_pausar", Button)
        botao.label = "Iniciar"
        botao.variant = "success"

        if auto_start:
            self.iniciar()

    def atualizar_tempos(self) -> None:
        """Lê apenas os valores de Foco e Curta e os guarda em segundos."""
        try:
            # Busca apenas os widgets que realmente existem no compose
            f_input = self.query_one(".input_pomodoro_foco", Input)
            c_input = self.query_one(".input_pomodoro_curta", Input)

            # Converte para inteiro, limitando a 60 minutos
            f_val = min(int(f_input.value or "0"), 60)
            c_val = min(int(c_input.value or "0"), 60)

            # Atualiza o dicionário de tempos
            self.tempos["Foco"] = f_val * 60
            self.tempos["Curta"] = c_val * 60

            # Sincroniza o label de sessões
            self.query_one(".pomodoro_sessoes", Label).update(f"Sessões: {self.sessoes_concluidas}")
        except Exception as e:
            # Se houver erro (ex: campo vazio durante a digitação), não faz nada
            pass

    def atualizar_tempo(self) -> None:
        self.tempo_restante -= 1

    def disparar_alarme(self) -> None:
        mensagem = f"O tempo de {self.modo} acabou! Prepare-se."
        def notificar():
            sistema = platform.system()
            if sistema == "Windows":
                cmd = f"""
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null;
                $xml = New-Object Windows.Data.Xml.Dom.XmlDocument;
                $xml.LoadXml('<toast scenario="reminder"><visual><binding template="ToastGeneric"><text hint-maxLines="1">🍅 Pomodoro App</text><text>{mensagem}</text></binding></visual></toast>');
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Relógio TUI').Show([Windows.UI.Notifications.ToastNotification]::new($xml))
                """
                subprocess.run(["powershell", "-Command", cmd], creationflags=0x08000000)
                try:
                    import winsound
                    for _ in range(5):
                        winsound.Beep(2000, 500) # 5 bipes altos e agudos (500ms cada)
                except Exception: pass
            elif sistema == "Linux":
                try:
                    subprocess.run(["notify-send", "--urgency=critical", "Pomodoro (TUI)", mensagem])
                    subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"])
                except Exception: pass
        threading.Thread(target=notificar, daemon=True).start()