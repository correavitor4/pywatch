from textual.app import ComposeResult
from textual.widgets import Label, Button, Input
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive

class TemporizadorWidget(Vertical):
    """Widget personalizado para o Temporizador."""
    
    tempo_restante = reactive(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rodando = False
        self.atualizador = None

    def compose(self) -> ComposeResult:
        """Interface do temporizador."""
        yield Input(placeholder="Nome do Temporizador", classes="cronometro_nome")
        
        # Input para digitar o tempo vs Label para mostrar a contagem
        yield Input(value="00:05:00", classes="input_tempo")
        yield Label("00:05:00", classes="tempo_display")
        
        # Reutilizamos a classe do cronômetro para manter o alinhamento já pronto!
        with Horizontal(classes="cronometro_botoes"):
            yield Button("Iniciar", classes="iniciar_pausar", variant="success")
            yield Button("Zerar", classes="zerar", variant="default")
            yield Button("Remover", classes="remover", variant="error")

    def on_mount(self) -> None:
        """Assim que o widget é criado, oculta o Label e deixa só o Input visível."""
        self.query_one(".tempo_display", Label).display = False

    def watch_tempo_restante(self, tempo: int) -> None:
        """Atualiza a tela a cada segundo ou dispara o alarme ao zerar."""
        minutos, segundos = divmod(tempo, 60)
        horas, minutos = divmod(minutos, 60)
        display = f"{int(horas):02}:{int(minutos):02}:{int(segundos):02}"
        
        label_display = self.query_one(".tempo_display", Label)
        label_display.update(display)
        
        # Quando a contagem acaba
        if tempo <= 0 and self.rodando:
            self.zerar()
            label_display.display = True
            self.query_one(".input_tempo", Input).display = False
            label_display.update("00:00:00 - FIM!")
            label_display.add_class("pausado") # Fica amarelo para chamar a atenção

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.has_class("iniciar_pausar"):
            if self.rodando:
                self.pausar()
            else:
                self.iniciar()
        elif event.button.has_class("zerar"):
            self.zerar()
        elif event.button.has_class("remover"):
            self.pausar()
            self.remove()

    def ler_tempo_input(self) -> int:
        """Lê o formato HH:MM:SS do input e converte para segundos no total."""
        texto = self.query_one(".input_tempo", Input).value
        try:
            partes = texto.split(":")
            return int(partes[0]) * 3600 + int(partes[1]) * 60 + int(partes[2])
        except Exception:
            return 0 # Se o usuário digitar algo inválido

    def iniciar(self) -> None:
        if self.tempo_restante <= 0:
            self.tempo_restante = self.ler_tempo_input()
            
        if self.tempo_restante > 0:
            self.rodando = True
            self.query_one(".input_tempo", Input).display = False
            self.query_one(".tempo_display", Label).display = True
            
            # Diferente do cronômetro, aqui o loop roda a cada 1 segundo redondo
            self.atualizador = self.set_interval(1, self.atualizar_tempo)
            
            botao = self.query_one(".iniciar_pausar", Button)
            botao.label = "Pausar"
            botao.variant = "warning"
            
            display_label = self.query_one(".tempo_display", Label)
            display_label.remove_class("pausado")
            display_label.add_class("rodando")

    def pausar(self) -> None:
        self.rodando = False
        if self.atualizador:
            self.atualizador.pause()
        
        botao = self.query_one(".iniciar_pausar", Button)
        botao.label = "Retomar"
        botao.variant = "primary"
        
        display_label = self.query_one(".tempo_display", Label)
        display_label.remove_class("rodando")
        display_label.add_class("pausado")

    def zerar(self) -> None:
        self.pausar()
        self.tempo_restante = 0
        
        self.query_one(".input_tempo", Input).display = True
        self.query_one(".tempo_display", Label).display = False
        
        botao = self.query_one(".iniciar_pausar", Button)
        botao.label = "Iniciar"
        botao.variant = "success"
        
        display_label = self.query_one(".tempo_display", Label)
        display_label.remove_class("rodando")
        display_label.remove_class("pausado")

    def atualizar_tempo(self) -> None:
        self.tempo_restante -= 1