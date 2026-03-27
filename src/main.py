import json
import os
import sys
import platform
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane, Label, Button, Input, Switch
from textual.containers import VerticalScroll

from cronometro import CronometroWidget
from temporizador import TemporizadorWidget
from relogio_mundial import RelogioMundialWidget, FusoHorarioWidget
from alarme import AlarmeWidget
from pomodoro import PomodoroWidget

class RelogioWindowsApp(App):
    """Clone do aplicativo de Relógio do Windows 11 em formato TUI."""

    # Título que aparecerá no cabeçalho
    TITLE = "Relógio do Sistema (TUI)"
    
    # CSS embutido básico para o layout
    CSS = """
    TabPane {
        align: center middle;
    }
    Label {
        color: $text-muted;
    }
    #aba_cronometro, #aba_relogio_mundial, #aba_alarmes, #aba_pomodoro {
        align: center top;
    }
    CronometroWidget, TemporizadorWidget, FusoHorarioWidget, AlarmeWidget, PomodoroWidget {
        align: center middle;
        height: auto;
        min-height: 10;
        width: 100%;
        margin: 0;
        border: round $primary-muted; /* Borda mais suave e elegante */
        padding: 1 2;
        background: $panel; /* Fundo que simula a elevação do Windows 11 */
    }
    .cronometro_nome {
        width: 100%;
        border: none;
        background: transparent;
        text-align: center;
    }
    .cronometro_nome:focus {
        border: none;
    }
    .tempo_display {
        text-align: center; /* Alinha os dígitos horizontalmente ao centro */
        text-style: bold;
        margin-bottom: 1;
    }
    .tempo_display.rodando {
        color: $success; /* Fica verde quando está em contagem */
    }
    .tempo_display.pausado {
        color: $warning; /* Fica amarelo quando pausado */
    }
    .input_tempo {
        width: 100%;
        text-align: center;
        text-style: bold;
        border: none;
        background: transparent;
        margin-bottom: 1;
    }
    .input_tempo:focus {
        border: none;
        background: $boost; /* Leve destaque quando estiver digitando */
    }
    .cronometro_botoes {
        align: center middle;
        height: auto;
        margin-top: 1;
    }
    .laps_container {
        height: auto;
        max-height: 5; /* Limita a altura da lista de voltas visíveis */
        width: 100%;
        margin-top: 1;
    }
    .lap_label {
        width: 100%;
        text-align: center;
        color: $text-muted;
    }
    RelogioMundialWidget {
        align: center middle;
        width: auto;
        height: auto;
        margin-bottom: 2; /* Espaço entre o relógio principal e os outros cartões */
    }
    #hora_atual {
        color: $primary;
    }
    #data_atual {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    .fuso_header {
        width: 100%;
        height: auto;
        align: center middle;
    }
    .select_fuso {
        width: 1fr;
    }
    .remover_fuso {
        min-width: 5;
        margin-left: 1;
    }
    .fuso_hora {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-top: 1;
    }
    .fuso_data {
        text-align: center;
        color: $text-muted;
    }
    .alarme_header {
        width: 100%;
        height: auto;
        align: center middle;
        margin-bottom: 1;
    }
    .input_alarme {
        width: 12;
        text-align: center;
        text-style: bold;
        border: none;
        background: transparent;
    }
    .input_alarme:focus {
        border: none;
        background: $boost;
    }
    .info_soneca {
        width: 100%;
        text-align: center;
        color: $warning;
        text-style: italic;
        margin-bottom: 1;
    }
    AlarmeWidget.tocando {
        border: round $error; /* Borda fica em destaque vermelho quando toca */
        background: $error 15%;
    }
    .pomodoro_config_container {
        width: 100%;
        height: auto;
        align: center middle;
        margin-bottom: 1;
    }
    .pomodoro_config_tempos, .pomodoro_config_auto {
        width: auto;
        height: auto;
        align: center middle;
    }
    .pomodoro_config_auto {
        margin-top: 1;
    }
    .label_pomodoro {
        content-align: center middle;
        color: $text-muted;
        margin: 0 1;
    }
    .input_pomodoro_foco, .input_pomodoro_pausa {
        width: 8;
        text-align: center;
        text-style: bold;
        border: none;
        background: transparent;
    }
    .input_pomodoro_foco:focus, .input_pomodoro_pausa:focus {
        border: none;
        background: $boost;
    }
    .pomodoro_modo {
        text-align: center;
        text-style: bold;
        color: $accent;
    }
    #container_cronometros, #container_temporizadores, #container_fusos, #container_alarmes, #container_pomodoros {
        width: 100%;
        height: auto;
        layout: vertical;
        padding: 0;
        margin: 0;
    }
    CronometroWidget, TemporizadorWidget, FusoHorarioWidget, AlarmeWidget, PomodoroWidget {
        width: 100%;
        margin-bottom: 1;
    }
    #btn_add_cronometro, #btn_add_temporizador, #btn_add_fuso, #btn_add_alarme, #btn_add_pomodoro {
        margin: 1;
    }
    Button {
        margin: 0 2;
    }
    """

    # Atalhos de teclado que aparecerão no rodapé
    BINDINGS = [
        ("q", "minimize_to_tray", "Ocultar"),
        ("d", "toggle_dark", "Tema"),
        ("1", "switch_tab('aba_relogio_mundial')", "Mundial"),
        ("2", "switch_tab('aba_alarmes')", "Alarmes"),
        ("3", "switch_tab('aba_cronometro')", "Cronômetro"),
        ("4", "switch_tab('aba_temporizador')", "Temporizador"),
        ("5", "switch_tab('aba_pomodoro')", "Pomodoro"),
        ("left", "previous_tab", "Aba Anterior"),
        ("right", "next_tab", "Próxima Aba"),
        ("n", "add_item", "Novo"),
        ("r", "remove_item", "Remover Último"),
        ("b", "minimize_to_tray", "Esconder")
    ]

    def compose(self) -> ComposeResult:
        """Constrói a hierarquia da interface do usuário."""
        # Cabeçalho que já traz um relógio pequeno por padrão
        yield Header(show_clock=True)
        
        # Estrutura das 4 abas principais
        with TabbedContent(initial="aba_relogio_mundial"):
            with TabPane("Relógio Mundial", id="aba_relogio_mundial"):
                yield RelogioMundialWidget()
                yield Button("+ Adicionar Fuso Horário", id="btn_add_fuso", variant="primary")
                with VerticalScroll(id="container_fusos"):
                    pass
                
            with TabPane("Alarmes", id="aba_alarmes"):
                yield Button("+ Adicionar Alarme", id="btn_add_alarme", variant="primary")
                with VerticalScroll(id="container_alarmes"):
                    pass # Será preenchido dinamicamente pelo carregar_dados()
                
            with TabPane("Cronômetro", id="aba_cronometro"):
                yield Button("+ Adicionar Cronômetro", id="btn_add_cronometro", variant="primary")
                with VerticalScroll(id="container_cronometros"):
                    yield CronometroWidget()
                
            with TabPane("Temporizador", id="aba_temporizador"):
                yield Button("+ Adicionar Temporizador", id="btn_add_temporizador", variant="primary")
                with VerticalScroll(id="container_temporizadores"):
                    yield TemporizadorWidget()
                    
            with TabPane("Pomodoro", id="aba_pomodoro"):
                yield Button("+ Adicionar Pomodoro", id="btn_add_pomodoro", variant="primary")
                with VerticalScroll(id="container_pomodoros"):
                    yield PomodoroWidget()
        
        yield Footer()

    def on_mount(self) -> None:
        """Executa automaticamente assim que o app é montado na tela."""
        self.carregar_dados()
        
        # Desabilita o botão X no Windows para evitar fechamento acidental
        if platform.system() == "Windows":
            import ctypes
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                hMenu = ctypes.windll.user32.GetSystemMenu(hwnd, False)
                if hMenu:
                    ctypes.windll.user32.DeleteMenu(hMenu, 0xF060, 0)
                    
        if "--minimized" in sys.argv:
            self.action_minimize_to_tray()

    def carregar_dados(self) -> None:
        """Lê o JSON e recria os alarmes e fusos salvos na última sessão."""
        if os.path.exists("dados.json"):
            try:
                with open("dados.json", "r", encoding="utf-8") as f:
                    dados = json.load(f)
                
                container_alarmes = self.query_one("#container_alarmes", VerticalScroll)
                for al in dados.get("alarmes", []):
                    container_alarmes.mount(AlarmeWidget(nome_inicial=al.get("nome", ""), hora_inicial=al.get("hora", "07:00"), ativo_inicial=al.get("ativo", False)))
                
                container_fusos = self.query_one("#container_fusos", VerticalScroll)
                for fuso in dados.get("fusos", []):
                    container_fusos.mount(FusoHorarioWidget(fuso_inicial=fuso))
            except Exception:
                self.montar_padroes()
        else:
            self.montar_padroes()

    def montar_padroes(self) -> None:
        self.query_one("#container_alarmes", VerticalScroll).mount(AlarmeWidget())

    def salvar_dados(self) -> None:
        """Coleta os estados atuais e salva num arquivo JSON."""
        dados = {"alarmes": [], "fusos": []}
        try:
            for alarme in self.query(AlarmeWidget):
                try:
                    dados["alarmes"].append({"nome": alarme.query_one(".cronometro_nome", Input).value, "hora": alarme.query_one(".input_alarme", Input).value, "ativo": alarme.query_one(".switch_alarme", Switch).value})
                except Exception:
                    pass
            for fuso in self.query(FusoHorarioWidget):
                try:
                    if isinstance(fuso.fuso, str) and fuso.fuso != "Select.BLANK":
                        dados["fusos"].append(fuso.fuso)
                except Exception:
                    pass
                    
            with open("dados.json", "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
        except Exception:
            pass # Garante que falhas de salvamento não impeçam o app de fechar

    def action_quit(self) -> None:
        """Intercepta o ctrl+c para salvar os dados antes de sair totalmente."""
        self.salvar_dados()
        self.exit() # Força o encerramento seguro do Textual

    def action_minimize_to_tray(self) -> None:
        """Oculta o terminal e cria um ícone na bandeja do sistema (Windows)."""
        self.salvar_dados()
        if platform.system() != "Windows":
            self.notify("A Bandeja do Sistema é suportada nativamente apenas no Windows.")
            return

        import ctypes
        import threading
        try:
            import pystray
            from PIL import Image, ImageDraw
        except ImportError:
            self.notify("Instale as libs 'pystray' e 'pillow' para usar a bandeja.")
            return 
        
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0) # 0 = SW_HIDE
            
        def criar_icone():
            """ Carrega o ícone real do arquivo .png ou cria um de fallback. """
            try:
                # O script está em 'src', o ícone está na raiz.
                base_path = os.path.dirname(os.path.abspath(__file__))
                icon_path = os.path.join(base_path, "..", "icone.png")
                return Image.open(icon_path)
            except Exception:
                # Fallback para o ícone desenhado se o arquivo não for encontrado
                imagem = Image.new('RGB', (64, 64), color=(30, 30, 30))
                desenho = ImageDraw.Draw(imagem)
                desenho.ellipse((16, 16, 48, 48), fill=(0, 150, 255))
                return imagem
            
        def ao_abrir(icone, item):
            icone.stop()
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 5) # 5 = SW_SHOW
                
        def ao_sair(icone, item):
            icone.stop()
            if hwnd: ctypes.windll.user32.ShowWindow(hwnd, 5)
            self.call_from_thread(self.action_quit) 
            
        def iniciar_bandeja():
            menu = pystray.Menu(pystray.MenuItem("Abrir Relógio", ao_abrir, default=True), pystray.MenuItem("Sair Totalmente", ao_sair))
            icone = pystray.Icon("RelogioTUI", criar_icone(), "Relógio App", menu=menu)
            icone.run()
            
        threading.Thread(target=iniciar_bandeja, daemon=True).start()

    def action_switch_tab(self, tab_id: str) -> None:
        """Muda a aba ativa instantaneamente através do atalho numérico."""
        self.query_one(TabbedContent).active = tab_id

    def action_previous_tab(self) -> None:
        """Navega para a aba à esquerda."""
        abas = ["aba_relogio_mundial", "aba_alarmes", "aba_cronometro", "aba_temporizador", "aba_pomodoro"]
        tc = self.query_one(TabbedContent)
        if tc.active in abas:
            idx = abas.index(tc.active)
            tc.active = abas[(idx - 1) % len(abas)]

    def action_next_tab(self) -> None:
        """Navega para a aba à direita."""
        abas = ["aba_relogio_mundial", "aba_alarmes", "aba_cronometro", "aba_temporizador", "aba_pomodoro"]
        tc = self.query_one(TabbedContent)
        if tc.active in abas:
            idx = abas.index(tc.active)
            tc.active = abas[(idx + 1) % len(abas)]

    def action_add_item(self) -> None:
        """Aciona o botão de adicionar correspondente à aba atual."""
        aba_ativa = self.query_one(TabbedContent).active
        mapa_botoes = {
            "aba_relogio_mundial": "#btn_add_fuso",
            "aba_alarmes": "#btn_add_alarme",
            "aba_cronometro": "#btn_add_cronometro",
            "aba_temporizador": "#btn_add_temporizador",
            "aba_pomodoro": "#btn_add_pomodoro"
        }
        if aba_ativa in mapa_botoes:
            self.query_one(mapa_botoes[aba_ativa], Button).press()

    def action_remove_item(self) -> None:
        """Remove o último item adicionado na aba atual garantindo o encerramento correto."""
        aba_ativa = self.query_one(TabbedContent).active
        mapa_containers = {
            "aba_relogio_mundial": "#container_fusos",
            "aba_alarmes": "#container_alarmes",
            "aba_cronometro": "#container_cronometros",
            "aba_temporizador": "#container_temporizadores",
            "aba_pomodoro": "#container_pomodoros"
        }
        if aba_ativa in mapa_containers:
            container = self.query_one(mapa_containers[aba_ativa], VerticalScroll)
            if container.children:
                ultimo_item = container.children[-1]
                # Busca o botão de remover específico deste widget e simula o clique
                seletor = ".remover_fuso" if aba_ativa == "aba_relogio_mundial" else ".remover"
                ultimo_item.query_one(seletor, Button).press()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Detecta o botão de adicionar e anexa um novo widget de cronômetro."""
        if event.button.id == "btn_add_cronometro":
            container = self.query_one("#container_cronometros", VerticalScroll)
            container.mount(CronometroWidget())
            container.scroll_end(animate=False)
        elif event.button.id == "btn_add_temporizador":
            container = self.query_one("#container_temporizadores", VerticalScroll)
            container.mount(TemporizadorWidget())
            container.scroll_end(animate=False)
        elif event.button.id == "btn_add_fuso":
            container = self.query_one("#container_fusos", VerticalScroll)
            container.mount(FusoHorarioWidget())
            container.scroll_end(animate=False)
        elif event.button.id == "btn_add_alarme":
            container = self.query_one("#container_alarmes", VerticalScroll)
            container.mount(AlarmeWidget())
            container.scroll_end(animate=False)
        elif event.button.id == "btn_add_pomodoro":
            container = self.query_one("#container_pomodoros", VerticalScroll)
            container.mount(PomodoroWidget())
            container.scroll_end(animate=False)

def configurar_startup():
    """Adiciona o script na inicialização do sistema (Apenas Linux)."""
    if platform.system() != "Linux":
        print("A configuração de inicialização automática é suportada apenas no Linux para este script.")
        return

    caminho_python = sys.executable
    caminho_script = os.path.abspath(__file__)
    comando = f"{caminho_python} {caminho_script} --minimized"
    
    caminho_autostart = os.path.expanduser("~/.config/autostart/")
    os.makedirs(caminho_autostart, exist_ok=True)
    desktop_file = (
        f"[Desktop Entry]\n"
        f"Type=Application\n"
        f"Exec={comando}\n"
        f"Terminal=true\n"
        f"Name=Relógio TUI\n"
        f"Comment=Relógio em segundo plano\n"
    )
    with open(os.path.join(caminho_autostart, "relogiotui.desktop"), "w") as f:
        f.write(desktop_file)
    print("Configurado para iniciar no Linux com sucesso!")

def main() -> None:
    if "--setup-startup" in sys.argv:
        configurar_startup()
        sys.exit(0)

    app = RelogioWindowsApp()
    app.run()


if __name__ == "__main__":
    main()
