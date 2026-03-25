import platform
import subprocess
import threading
from datetime import datetime

from textual.app import ComposeResult
from textual.widgets import Label, Button, Input, Switch
from textual.containers import Horizontal, Vertical

class AlarmeWidget(Vertical):
    """Widget personalizado para o Alarme."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ativo = False
        self.ultimo_disparo = "" # Evita que o alarme dispare múltiplas vezes no mesmo minuto
        self.tocando = False

    def compose(self) -> ComposeResult:
        """Interface do alarme."""
        yield Input(placeholder="Nome do Alarme (Ex: Acordar)", classes="cronometro_nome")
        
        with Horizontal(classes="alarme_header"):
            # Input estilo microondas para HH:MM
            yield Input(value="07:00", classes="input_alarme")
            yield Switch(value=False, classes="switch_alarme")
            
        with Horizontal(classes="cronometro_botoes"):
            yield Button("Parar", classes="parar", variant="success")
            yield Button("+ 5m", classes="soneca_5", variant="primary")
            yield Button("+ 15m", classes="soneca_15", variant="primary")
            yield Button("Remover", classes="remover", variant="error")

    def on_mount(self) -> None:
        # Checa a hora atual do sistema a cada 1 segundo
        self.set_interval(1.0, self.checar_alarme)

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Atualiza o estado quando o usuário liga/desliga o interruptor."""
        if event.switch.has_class("switch_alarme"):
            self.ativo = event.value
            # Se desligar a chavinha enquanto a música toca, ele para o som
            if not self.ativo and self.tocando:
                self.parar()

    def checar_alarme(self) -> None:
        if not self.ativo:
            return
        
        agora = datetime.now().strftime("%H:%M")
        hora_alarme = self.query_one(".input_alarme", Input).value
        
        if agora == hora_alarme and self.ultimo_disparo != agora:
            self.ultimo_disparo = agora
            # O switch continua ativo nativamente para o dia seguinte!
            
            self.tocar()
            
            nome = self.query_one(".cronometro_nome", Input).value
            self.disparar_notificacao(nome)

    def tocar(self) -> None:
        """Inicia o som do alarme de forma contínua."""
        self.tocando = True
        self.add_class("tocando") # Feedback visual no cartão
        sistema = platform.system()
        if sistema == "Windows":
            try:
                import winsound
                # Toca música/som de notificação do Windows repetidamente em 2º plano
                winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_LOOP | winsound.SND_ASYNC)
            except Exception:
                pass
        elif sistema == "Linux":
            try:
                self.processo_audio = subprocess.Popen(["paplay", "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"])
            except Exception:
                pass

    def parar(self) -> None:
        """Interrompe o som e reseta o visual do alarme."""
        self.tocando = False
        self.remove_class("tocando")
        sistema = platform.system()
        if sistema == "Windows":
            try:
                import winsound
                # Comando para expurgar/parar sons tocando no momento
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
        elif sistema == "Linux":
            if hasattr(self, "processo_audio") and self.processo_audio:
                try: self.processo_audio.terminate()
                except Exception: pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.has_class("remover"):
            self.parar()
            self.remove()
        elif event.button.has_class("parar"):
            self.parar()
        elif event.button.has_class("soneca_5"):
            self.adicionar_soneca(5)
        elif event.button.has_class("soneca_15"):
            self.adicionar_soneca(15)

    def adicionar_soneca(self, minutos: int) -> None:
        """Adiciona minutos ao horário do alarme atual (Soneca)."""
        self.parar() # Para a música atual ao adicionar soneca
        hora_str = self.query_one(".input_alarme", Input).value
        try:
            h, m = map(int, hora_str.split(":"))
            m += minutos
            h = (h + m // 60) % 24
            m = m % 60
            novo_tempo = f"{h:02}:{m:02}"
            
            self.query_one(".input_alarme", Input).value = novo_tempo
            self.ultimo_disparo = "" # Permite disparar de novo no novo horário
            self.ativo = True
            self.query_one(".switch_alarme", Switch).value = True
        except Exception:
            pass

    def on_input_changed(self, event: Input.Changed) -> None:
        """Máscara estilo microondas para formatar em HH:MM."""
        if event.input.has_class("input_alarme"):
            numeros = "".join(filter(str.isdigit, event.value))
            numeros = numeros[-4:].zfill(4)
            formatado = f"{numeros[0:2]}:{numeros[2:4]}"
            
            if event.value != formatado:
                event.input.value = formatado
                event.input.cursor_position = len(formatado)

    def disparar_notificacao(self, nome: str) -> None:
        """Notificação silenciosa pelo SO (não rouba foco de jogos/tela cheia)."""
        sistema = platform.system()
        mensagem = f"Alarme '{nome}' está tocando!" if nome else "Há um alarme tocando!"
        
        def tarefa_notificacao():
            if sistema == "Windows":
                # Usa script PowerShell para invocar Notificação Toast nativa (no canto da tela)
                cmd = f"""
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null;
                \$xml = New-Object Windows.Data.Xml.Dom.XmlDocument;
                \$xml.LoadXml('<toast><visual><binding template="ToastGeneric"><text>Relógio App</text><text>{mensagem}</text></binding></visual></toast>');
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Relógio TUI').Show([Windows.UI.Notifications.ToastNotification]::new(\$xml))
                """
                subprocess.run(["powershell", "-Command", cmd], creationflags=0x08000000)
        threading.Thread(target=tarefa_notificacao, daemon=True).start()