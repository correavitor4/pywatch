from datetime import datetime
import zoneinfo
from textual.app import ComposeResult
from textual.widgets import Label, Digits, Button, Select
from textual.containers import Vertical, Horizontal

class RelogioMundialWidget(Vertical):
    """Widget para exibir a hora atual e a data no Relógio Mundial."""
    
    def compose(self) -> ComposeResult:
        """Interface do relógio principal."""
        yield Digits("00:00:00", id="hora_atual")
        yield Label("Data de hoje", id="data_atual")
        
    def on_mount(self) -> None:
        """Atualiza o relógio assim que a tela carrega e inicia o loop de 1 segundo."""
        self.atualizar_relogio()
        self.set_interval(1.0, self.atualizar_relogio)
        
    def atualizar_relogio(self) -> None:
        agora = datetime.now()
        
        dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        
        data_formatada = f"{dias_semana[agora.weekday()]}, {agora.day} de {meses[agora.month - 1]} de {agora.year}"
        
        self.query_one("#hora_atual", Digits).update(agora.strftime("%H:%M:%S"))
        self.query_one("#data_atual", Label).update(data_formatada)

class FusoHorarioWidget(Vertical):
    """Widget para exibir fusos horários adicionais em forma de cartão."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fuso = None

    def compose(self) -> ComposeResult:
        # Pega todos os fusos do sistema, filtra os úteis e os coloca em ordem alfabética
        todos_fusos = sorted([tz for tz in zoneinfo.available_timezones() if "/" in tz or tz == "UTC"])
        
        if not todos_fusos:
            opcoes = [("⚠️ Banco vazio! Feche o app e rode: pip install tzdata", "")]
        else:
            opcoes = [(tz, tz) for tz in todos_fusos]
        
        with Horizontal(classes="fuso_header"):
            yield Select(opcoes, prompt="Escolha a Cidade/Fuso", classes="select_fuso")
            yield Button("X", classes="remover_fuso", variant="error")
        yield Label("--:--:--", classes="fuso_hora")
        yield Label("Aguardando...", classes="fuso_data")

    def on_mount(self) -> None:
        self.set_interval(1.0, self.atualizar_relogio)

    def atualizar_relogio(self) -> None:
        if not self.fuso or self.fuso == Select.BLANK or self.fuso == "":
            return
        try:
            agora = datetime.now(zoneinfo.ZoneInfo(str(self.fuso)))
            self.query_one(".fuso_hora", Label).update(agora.strftime("%H:%M:%S"))
            self.query_one(".fuso_data", Label).update(agora.strftime("%d/%m/%Y"))
        except Exception:
            pass

    def on_select_changed(self, event: Select.Changed) -> None:
        """É chamado sempre que o usuário escolhe um novo fuso no menu suspenso."""
        if event.select.has_class("select_fuso"):
            self.fuso = event.value
            if self.fuso and self.fuso != Select.BLANK:
                self.atualizar_relogio()
            else:
                self.query_one(".fuso_hora", Label).update("--:--:--")
                self.query_one(".fuso_data", Label).update("Aguardando...")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.has_class("remover_fuso"):
            self.remove()