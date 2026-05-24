# =============================================================================
# ESCUDO INTELIGENTE DE COMPATIBILIDADE HÍBRIDA (PC E ANDROID)
# =============================================================================
import os
import sys
from types import ModuleType

# Verifica se o sistema operacional NÃO é Windows (ou seja, está rodando no Android)
if os.name != "nt":
    # 1. Cria um módulo 'wsgiref.simple_server' falso em memória para o Android
    if 'wsgiref' not in sys.modules:
        wsgiref = ModuleType('wsgiref')
        wsgiref.simple_server = ModuleType('simple_server')
        sys.modules['wsgiref'] = wsgiref
        sys.modules['wsgiref.simple_server'] = wsgiref.simple_server

    # 2. Desativa o fluxo de navegador do Google apenas no ambiente móvel
    sys.modules['google_auth_oauthlib'] = ModuleType('google_auth_oauthlib')
    sys.modules['google_auth_oauthlib.flow'] = ModuleType('flow')

# Seus imports originais continuam abaixo e funcionam perfeitamente em ambos:
import datetime
import flet as ft
import gspread
import httpx

app = flet_fastapi.app(main)

CHAVE_API_GOOGLE = "AIzaSyDp5zXQ4uP6VWo83XiLNePpz4vUuEiOzxU"
ID_DA_PLANILHA = "1MDlkENxlslErQ6DwxtDQ-6ufHxIJtCZ5G1eUVTXiTGc"
url_formulario = "https://docs.google.com/forms/d/11CUoNGpviG5ebyGSIR5c60Au-nZdmp150UQbDUZKUxE/formResponse"

# Inicialização via API Key pública configurada como Editor
client = gspread.api_key(CHAVE_API_GOOGLE)
db = client.open_by_key(ID_DA_PLANILHA)

sheet_alunos = db.worksheet("Alunos")
sheet_treinos = db.worksheet("Grade_Treinos")

# --- CONFIGURAÇÕES DE TESTE ---
ID_ALUNO_LOGADO = "123" 
É_ADMINISTRADOR = False  # Altere para True para testar a visão de Administrador


def main(page: ft.Page):
    # -------------------------------------------------------------------------
    # CONFIGURAÇÕES DE IDENTIDADE VISUAL (PALETA DE CORES PREMIUM)
    # -------------------------------------------------------------------------
    COLOR_BG_DARK = "#121214"      # Fundo principal escuro do app
    COLOR_SURFACE = "#1F2024"      # Fundo dos Cards e Containers
    COLOR_GOLD = "#D4AF37"         # Botões de ação e destaques principais
    COLOR_BLUE_BELT = "#1A56DB"    # Elementos de navegação e títulos
    COLOR_TEXT_PRIMARY = "#FFFFFF" # Texto principal
    COLOR_TEXT_MUTED = "#9CA3AF"   # Texto secundário de apoio

    page.title = "GROUND ONE BJJ - Gestão"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = COLOR_BG_DARK
    page.padding = 0

    # -------------------------------------------------------------------------
    # FUNÇÃO DE VALIDAÇÃO (ATUALIZA ERROS VISUAIS NA INTERFACE)
    # -------------------------------------------------------------------------
    def validar_campos_formulario(e):
        email_string = txt_email.value.strip() if txt_email.value else ""
        formato_email_valido = "@" in email_string and "." in email_string.split("@")[-1]

        senha_string = txt_senha.value if txt_senha.value else ""
        tamanho_senha_valido = len(senha_string) >= 6

        if txt_email.value and not formato_email_valido:
            txt_email.error_text = "Formato de e-mail inválido"
        else:
            txt_email.error_text = None

        if txt_senha.value and not tamanho_senha_valido:
            txt_senha.error_text = "A senha deve conter pelo menos 6 caracteres"
        else:
            txt_senha.error_text = None
            
        page.update()

    # -------------------------------------------------------------------------
    # FUNÇÕES DE MÁSCARAS AUTOMÁTICAS E VALIDAÇÃO ONLINE
    # -------------------------------------------------------------------------
    def mascara_cpf(e):
        texto = "".join(filter(str.isdigit, e.control.value))[:11]
        if len(texto) > 9:
            e.control.value = f"{texto[:3]}.{texto[3:6]}.{texto[6:9]}-{texto[9:]}"
        elif len(texto) > 6:
            e.control.value = f"{texto[:3]}.{texto[3:6]}.{texto[6:]}"
        elif len(texto) > 3:
            e.control.value = f"{texto[:3]}.{texto[3:]}"
        else:
            e.control.value = texto
        validar_campos_formulario(e)

    def mascara_data(e):
        texto = "".join(filter(str.isdigit, e.control.value))[:8]
        if len(texto) > 4:
            e.control.value = f"{texto[:2]}/{texto[2:4]}/{texto[4:]}"
        elif len(texto) > 2:
            e.control.value = f"{texto[:2]}/{texto[2:]}"
        else:
            e.control.value = texto
        validar_campos_formulario(e)

    def mascara_telefone(e):
        texto = "".join(filter(str.isdigit, e.control.value))[:11]
        if len(texto) > 6:
            e.control.value = f"({texto[:2]}) {texto[2:7]}-{texto[7:]}"
        elif len(texto) > 2:
            e.control.value = f"({texto[:2]}) {texto[2:]}"
        else:
            e.control.value = texto
        validar_campos_formulario(e)

    def mascara_cep(e):
        texto = "".join(filter(str.isdigit, e.control.value))[:8]
        if len(texto) > 5:
            e.control.value = f"{texto[:5]}-{texto[5:]}"
        else:
            e.control.value = texto
        validar_campos_formulario(e)

    # Máscaras de conversão reativa instantânea de caracteres para o formulário
    def forcar_caixa_alta(e):
        if e.control.value:
            e.control.value = e.control.value.upper()
            e.control.update()
        validar_campos_formulario(e)

    def forcar_caixa_baixa(e):
        if e.control.value:
            e.control.value = e.control.value.lower()
            e.control.update()
        validar_campos_formulario(e)

    # Motor Síncrono com Threading para busca instantânea e compatível (PC/Android)
    def disparar_busca_cep(e):
        cep_limpo = "".join(filter(str.isdigit, txt_cep.value))
        
        if len(cep_limpo) != 8:
            txt_rua.disabled = False
            txt_rua.value = "Erro: CEP precisa conter 8 números."
            txt_rua.disabled = True
            txt_rua.update()
            return

        txt_rua.disabled = False
        txt_rua.value = "BUSCANDO ENDEREÇO ONLINE..."
        txt_rua.disabled = True
        txt_rua.update()

        def processo_busca_background():
            url_oficial = f"https://viacep.com.br/ws/{cep_limpo}/json/"
            headers_requisicao = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

            try:
                resposta = httpx.get(url_oficial, headers=headers_requisicao, timeout=5.0)
                if resposta.status_code == 200:
                    dados = resposta.json()
                    
                    if "erro" not in dados:
                        txt_rua.disabled = False
                        txt_bairro.disabled = False
                        txt_cidade.disabled = False
                        txt_uf.disabled = False
                        
                        txt_rua.value = str(dados.get("logradouro", "")).upper()
                        txt_bairro.value = str(dados.get("bairro", "")).upper()
                        txt_cidade.value = str(dados.get("localidade", "")).upper()
                        txt_uf.value = str(dados.get("uf", "")).upper()
                        
                        txt_rua.disabled = True
                        txt_bairro.disabled = True
                        txt_cidade.disabled = True
                        txt_uf.disabled = True
                        
                        txt_rua.update()
                        txt_bairro.update()
                        txt_cidade.update()
                        txt_uf.update()
                        
                        validar_campos_formulario(None)
                        return
                    else:
                        txt_rua.disabled = False
                        txt_rua.value = "ERRO: CEP NÃO ENCONTRADO."
                        txt_rua.disabled = True
                        txt_rua.update()
                        return
            except Exception as falha:
                txt_rua.disabled = False
                txt_rua.value = f"ERRO DE CONEXÃO: {str(falha)}"
                txt_rua.disabled = True
                txt_rua.update()

        import threading
        threading.Thread(target=processo_busca_background, daemon=True).start()

    # Inicialização estrita dos componentes (Campos de endereço congelados por padrão)
    txt_nome = ft.TextField(label="Nome Completo", width=300, border_color=COLOR_BLUE_BELT, on_change=forcar_caixa_alta)
    txt_cpf = ft.TextField(label="CPF", width=300, border_color=COLOR_BLUE_BELT, on_change=mascara_cpf, keyboard_type=ft.KeyboardType.NUMBER)
    txt_nasc = ft.TextField(label="Nascimento", width=300, border_color=COLOR_BLUE_BELT, on_change=mascara_data, keyboard_type=ft.KeyboardType.NUMBER)
    txt_profissao = ft.TextField(label="Profissão", width=300, border_color=COLOR_BLUE_BELT, on_change=forcar_caixa_alta)
    txt_tel = ft.TextField(label="Telefone com DDD", width=300, border_color=COLOR_BLUE_BELT, on_change=mascara_telefone, keyboard_type=ft.KeyboardType.PHONE)
    txt_rua = ft.TextField(label="Logradouro", width=300, border_color=COLOR_BLUE_BELT, on_change=forcar_caixa_alta, disabled=True)
    txt_num = ft.TextField(label="Nº", width=300, border_color=COLOR_BLUE_BELT, on_change=validar_campos_formulario)
    txt_comp = ft.TextField(label="Complemento", width=300, border_color=COLOR_BLUE_BELT, on_change=validar_campos_formulario)
    txt_bairro = ft.TextField(label="Bairro", width=300, border_color=COLOR_BLUE_BELT, on_change=forcar_caixa_alta, disabled=True)
    txt_cidade = ft.TextField(label="Cidade", width=300, border_color=COLOR_BLUE_BELT, on_change=forcar_caixa_alta, disabled=True)
    txt_uf = ft.TextField(label="UF", width=300, border_color=COLOR_BLUE_BELT, on_change=forcar_caixa_alta, disabled=True)
    txt_cep = ft.TextField(label="CEP", width=240, border_color=COLOR_BLUE_BELT, on_change=mascara_cep, keyboard_type=ft.KeyboardType.NUMBER)

    txt_graduacao = ft.Dropdown(
        label="Graduação",
        width=300,
        border_color=COLOR_BLUE_BELT,
        options=[
            ft.dropdown.Option("Nenhuma"),
            ft.dropdown.Option("Branca"),
            ft.dropdown.Option("Cinza"),
            ft.dropdown.Option("Amarela"),
            ft.dropdown.Option("Laranja"),
            ft.dropdown.Option("Verde"),
            ft.dropdown.Option("Azul"),
            ft.dropdown.Option("Roxa"),
            ft.dropdown.Option("Marrom"),
            ft.dropdown.Option("Preta"),
        ]
    )
    txt_graduacao.on_change = validar_campos_formulario

    txt_email = ft.TextField(label="E-mail", width=300, border_color=COLOR_BLUE_BELT, keyboard_type=ft.KeyboardType.EMAIL, on_change=forcar_caixa_baixa)
    txt_email_conf = ft.TextField(label="Confirmar E-mail", width=300, border_color=COLOR_BLUE_BELT, keyboard_type=ft.KeyboardType.EMAIL, on_change=forcar_caixa_baixa)
    txt_senha = ft.TextField(label="Senha", width=300, border_color=COLOR_BLUE_BELT, password=True, can_reveal_password=True, on_change=validar_campos_formulario)
    txt_senha_conf = ft.TextField(label="Confirmar Senha", width=300, border_color=COLOR_BLUE_BELT, password=True, can_reveal_password=True, on_change=validar_campos_formulario)

    lbl_lembrete_senha = ft.Text("Senha com 6 dígitos ou mais", color=COLOR_GOLD, size=12, weight="bold")

    txt_login_email = ft.TextField(label="Digite seu E-mail", border_color=COLOR_GOLD, width=300, keyboard_type=ft.KeyboardType.EMAIL)
    txt_login_senha = ft.TextField(label="Digite sua Senha", border_color=COLOR_GOLD, width=300, password=True, can_reveal_password=True)
    lbl_erro_login = ft.Text("", color=ft.Colors.RED_400, size=14, weight="bold", text_align=ft.TextAlign.CENTER, visible=False)

    btn_entrar = ft.Button(content=ft.Text("Entrar no Sistema", color="#000000", weight="bold"), bgcolor=COLOR_GOLD, width=300)
    btn_enviar = ft.Button(content=ft.Text("Enviar Cadastro", color="#000000", weight="bold"), bgcolor=COLOR_GOLD, width=300)

    def intermedio_cadastro(e):
        btn_enviar.disabled = True
        btn_enviar.content = ft.Row(
            [
                ft.ProgressRing(width=16, height=16, stroke_width=2, color="#000000"),
                ft.Text("Processando...", color="#000000", weight="bold")
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )
        btn_enviar.update()
        executar_cadastro_sync(e)

    btn_enviar.on_click = intermedio_cadastro

    # -------------------------------------------------------------------------
    # LÓGICA DE ALERTAS AUTOMÁTICOS PROTEGIDA CONTRA FALHAS
    # -------------------------------------------------------------------------
    def verificar_alertas_direto(alunos_dados, email_usuario):
        if É_ADMINISTRADOR:
            return ft.Container()
        try:
            aluno_atual = next((a for a in alunos_dados if str(a.get("E-mail", "")).strip().lower() == email_usuario.strip().lower()), None)
            if not aluno_atual or not aluno_atual.get("Data_Vencimento"):
                return ft.Container()

            data_vencimento = datetime.datetime.strptime(str(aluno_atual["Data_Vencimento"]), "%Y-%m-%d").date()
            hoje = datetime.date.today()
            status_pgto = str(aluno_atual.get("Status_Pagamento", "Pendente"))

            if hoje >= data_vencimento and status_pgto == "Pendente":
                return ft.Container(
                    content=ft.Text("Sua mensalidade está vencida, favor regularizar.", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    bgcolor=ft.Colors.RED_800, padding=14, border_radius=8, margin=ft.margin.only(bottom=10)
                )
            elif data_vencimento - datetime.timedelta(days=2) <= hoje <= data_vencimento and status_pgto == "Pendente":
                return ft.Container(
                    content=ft.Text("O vencimento da sua mensalidade está chegando, adiante-se.", color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    bgcolor=COLOR_GOLD, padding=14, border_radius=8, margin=ft.margin.only(bottom=10)
                )
        except Exception:
            pass
        return ft.Container()

    # -------------------------------------------------------------------------
    # FUNÇÃO DE CADASTRO COM VALIDAÇÃO INTEGRADA EM POP-UP (ALERTDIALOG)
    # -------------------------------------------------------------------------
    def executar_cadastro_sync(e):
        def fechar_popup(ev):
            popup_aviso.open = False
            btn_enviar.content = ft.Text("Enviar Cadastro", color="#000000", weight="bold")
            btn_enviar.disabled = False
            page.update()

        popup_aviso = ft.AlertDialog(
            title=ft.Text("Aviso do Sistema", weight="bold"),
            content=ft.Text(""),
            actions=[
                ft.TextButton("OK", on_click=fechar_popup)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(popup_aviso)

        # Complemento (txt_comp) removido da obrigatoriedade
        campos_obrigatorios = [
            txt_nome.value, txt_tel.value, txt_cpf.value, txt_nasc.value,
            txt_profissao.value, txt_rua.value, txt_num.value,
            txt_bairro.value, txt_cidade.value, txt_uf.value, txt_cep.value,
            txt_graduacao.value,
            txt_email.value, txt_email_conf.value, txt_senha.value, txt_senha_conf.value
        ]

        if not all(campos_obrigatorios):
            popup_aviso.content.value = "Todos os campos obrigatórios devem ser preenchidos!"
            popup_aviso.open = True
            page.update()
            return

        # Trava: Verificação cruzada de e-mails
        if txt_email.value.strip().lower() != txt_email_conf.value.strip().lower():
            popup_aviso.content.value = "Os e-mails informados não coincidem!"
            popup_aviso.open = True
            page.update()
            return

        # Trava: Verificação cruzada de senhas
        if txt_senha.value != txt_senha_conf.value:
            popup_aviso.content.value = "As senhas digitadas nos dois campos não coincidem!"
            popup_aviso.open = True
            page.update()
            return

        if len(txt_senha.value) < 6:
            popup_aviso.content.value = "A senha deve conter pelo menos 6 caracteres!"
            popup_aviso.open = True
            page.update()
            return

        if len(txt_cpf.value) != 14:
            popup_aviso.content.value = "O CPF informado está incompleto ou fora do padrão!"
            popup_aviso.open = True
            page.update()
            return

        if len(txt_nasc.value) != 10:
            popup_aviso.content.value = "A data de nascimento informada está incompleta ou inválida!"
            popup_aviso.open = True
            page.update()
            return

        if len(txt_cep.value) != 9:
            popup_aviso.content.value = "O CEP informado está incompleto ou inválido!"
            popup_aviso.open = True
            page.update()
            return

        email_string = txt_email.value.strip()
        formato_email_valido = "@" in email_string and "." in email_string.split("@")[-1]
        if not formato_email_valido:
            popup_aviso.content.value = "Formato de e-mail inválido!"
            popup_aviso.open = True
            page.update()
            return

        dados_envio = {
            "entry.426433085": txt_nome.value.strip(),
            "entry.1399144794": txt_tel.value.strip(),
            "entry.2031416784": txt_cpf.value.strip(),
            "entry.329555039": txt_nasc.value.strip(),
            "entry.1888052013": txt_profissao.value.strip(),
            "entry.424137188": txt_rua.value.strip(),
            "entry.646853904": txt_num.value.strip(),
            "entry.1737777194": txt_comp.value.strip(),
            "entry.311478297": txt_bairro.value.strip(),
            "entry.1970547624": txt_cidade.value.strip(),
            "entry.120744136": str(txt_uf.value).upper(),
            "entry.1502016964": txt_cep.value.strip(),
            "entry.1135504943": str(txt_graduacao.value),
            "entry.601928810": txt_email.value.strip(),
            "entry.1386054704": txt_senha.value
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            httpx.post(url_formulario, data=dados_envio, headers=headers)
            
            # Limpeza completa dos campos para evitar dados residuais
            txt_nome.value = ""
            txt_tel.value = ""
            txt_cpf.value = ""
            txt_nasc.value = ""
            txt_profissao.value = ""
            txt_rua.value = ""
            txt_num.value = ""
            txt_comp.value = ""
            txt_bairro.value = ""
            txt_cidade.value = ""
            txt_uf.value = ""
            txt_cep.value = ""
            txt_graduacao.value = "Nenhuma"
            txt_email.value = ""
            txt_email_conf.value = ""
            txt_senha.value = ""
            txt_senha_conf.value = ""
            
            page.controls.clear()
            
            layout_sucesso = ft.Container(
                content=ft.Column([
                    ft.Text("PARABÉNS!!!", size=32, weight="bold", color=COLOR_GOLD, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=10),
                    ft.Text(
                        "Cadastro realizado com sucesso, seja bem vindo a família G1-Bjj, "
                        "estamos felizes de ter você conosco e esperamos suprir suas expectativas, "
                        "Nossa diretriz principal é \"nunca perder o foco, a disciplina e o respeito\".",
                        size=16,
                        color=COLOR_TEXT_PRIMARY,
                        text_align=ft.TextAlign.CENTER,
                        width=450
                    ),
                    ft.Container(height=20),
                    ft.Text(
                        "\"tudo o que vier às suas mãos para fazer, faça com todo seu entendimento e com "
                        "toda a sua força, pois pra sepultura onde iremos não ha obras, nem projetos, "
                        "nem sabedoria e nem conhecimento.\" Eclesiastes 9:10",
                        size=14,
                        italic=True,
                        color=COLOR_TEXT_MUTED,
                        text_align=ft.TextAlign.CENTER,
                        width=450
                    ),
                    ft.Container(height=30),
                    ft.Button(
                        content=ft.Text("Ir para o Login", color=COLOR_TEXT_PRIMARY, weight="bold"),
                        on_click=lambda _: [carregar_tela_autenticacao(), mudar_modo_login()], 
                        bgcolor=COLOR_BLUE_BELT, 
                        width=200
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.Alignment(0, 0),
                padding=30,
                expand=True
            )
            
            page.add(
                ft.Stack(
                    controls=[
                        ft.Image(
                            src="fundo.jpeg", fit="cover", expand=True, opacity=0.15,
                            width=page.window_width if hasattr(page, "window_width") else None,
                            height=page.window_height if hasattr(page, "window_height") else None
                        ),
                        layout_sucesso
                    ], expand=True
                )
            )
            page.update()

        except Exception as erro:
            btn_enviar.content = ft.Text("Enviar Cadastro", color="#000000", weight="bold")
            btn_enviar.disabled = False
            page.overlay.append(ft.SnackBar(ft.Text(f"Falha no envio dos dados. Motivo: {erro}")))
            page.update()

    # -------------------------------------------------------------------------
    # LÓGICA DE LOGIN REAL
    # -------------------------------------------------------------------------
    def executar_login(e):
        nonlocal lbl_erro_login
        
        lbl_erro_login.visible = False
        lbl_erro_login.value = ""
        
        if not txt_login_email.value or not txt_login_senha.value:
            lbl_erro_login.value = "Preencha o e-mail e a senha!"
            lbl_erro_login.visible = True
            btn_entrar.content = ft.Text("Entrar no Sistema", color="#000000", weight="bold")
            btn_entrar.disabled = False
            page.update()
            return

        # Normalização imediata da caixa do e-mail digitado
        if txt_login_email.value:
            txt_login_email.value = txt_login_email.value.strip().lower()

        try:
            alunos_dados = sheet_alunos.get_all_records()
            email_existe = any(str(a.get("E-mail", "")).strip().lower() == txt_login_email.value for a in alunos_dados)
            
            if not email_existe:
                lbl_erro_login.value = "Login e/ou Senha invalidos"
                lbl_erro_login.visible = True
                btn_entrar.content = ft.Text("Entrar no Sistema", color="#000000", weight="bold")
                btn_entrar.disabled = False
                page.update()
                return

            usuario_valido = next((a for a in alunos_dados if str(a.get("E-mail", "")).strip().lower() == txt_login_email.value and str(a.get("Senha", "")) == txt_login_senha.value), None)

            if usuario_valido:
                global ID_ALUNO_LOGADO
                ID_ALUNO_LOGADO = str(usuario_valido.get("ID_Usuario", "123"))
                
                try:
                    treinos_dados = sheet_treinos.get_all_records()
                except Exception:
                    treinos_dados = []
                
                renderizar_interface_montada(alunos_dados, treinos_dados)
            else:
                lbl_erro_login.value = "Login e/ou Senha invalidos"
                lbl_erro_login.visible = True
                btn_entrar.content = ft.Text("Entrar no Sistema", color="#000000", weight="bold")
                btn_entrar.disabled = False
                page.update()
                
        except Exception as erro_login:
            btn_entrar.content = ft.Text("Entrar no Sistema", color="#000000", weight="bold")
            btn_entrar.disabled = False
            page.overlay.append(ft.SnackBar(ft.Text(f"Erro ao conectar com banco de dados: {erro_login}")))
            page.update()

    # -------------------------------------------------------------------------
    # MONTAGEM VISUAL DA INTERFACE DO PAINEL LOGADO DE ALUNOS
    # -------------------------------------------------------------------------
    def renderizar_interface_montada(alunos_dados, treinos_dados):
        page.controls.clear()
        
        alerta_topo = ft.Container()
        try:
            alerta_topo = verificar_alertas_direto(alunos_dados, txt_login_email.value)
        except Exception:
            pass

        aluno_atual = next((a for a in alunos_dados if str(a.get("E-mail", "")).strip().lower() == txt_login_email.value.strip().lower()), None)
        
        vencimento_texto = "Pendente"
        status_pagamento_texto = "Pendente"
        valor_numerico_planilha = 150.0

        if aluno_atual:
            vencimento_texto = str(aluno_atual.get("Data_Vencimento") or "Pendente")
            status_pagamento_texto = str(aluno_atual.get("Status_Pagamento") or "Pendente")
            try:
                valor_bruto = str(aluno_atual.get("Valor_Mensalidade", "150")).strip()
                valor_numerico_planilha = float(valor_bruto.replace("R$", "").replace(",", ".").strip())
            except Exception:
                valor_numerico_planilha = 150.0

        texto_exibicao_valor = f"R$ {valor_numerico_planilha:,.2f}".replace(".", ",")
        status_color = ft.Colors.GREEN_400 if status_pagamento_texto == "Pago" else ft.Colors.RED_400

        graduacao_aluno = "BRANCA"
        if aluno_atual:
            grad_banco = str(aluno_atual.get("Graduacao", "Nenhuma")).strip().upper()
            if grad_banco != "NENHUMA":
                graduacao_aluno = grad_banco

        mapa_cores_faixa = {
            "BRANCA": "#FFFFFF",
            "CINZA": "#808080",
            "AMARELA": "#FFEB3B",
            "LARANJA": "#FF9800",
            "VERDE": "#4CAF50",
            "AZUL": "#0000FF",
            "ROXA": "#9C27B0",
            "MARROM": "#5D4037",
            "PRETA": "#000000"
        }

        cor_principal = mapa_cores_faixa.get(graduacao_aluno, "#FFFFFF")

        if graduacao_aluno == "PRETA":
            cor_ponteira_centro = "#FF0000"
        else:
            cor_ponteira_centro = "#000000"

        faixa_graduacao_rodape = ft.Container(
            height=22,
            width=page.window_width if hasattr(page, "window_width") else None,
            margin=ft.Margin.only(top=5),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, COLOR_TEXT_MUTED)),
            content=ft.Row(
                spacing=0,
                controls=[
                    ft.Container(bgcolor=cor_principal, expand=80),
                    ft.Container(bgcolor=cor_ponteira_centro, expand=15),
                    ft.Container(bgcolor=cor_principal, expand=5),
                ]
            )
        )

        total_treinos_mes = 0
        try:
            sheet_presencas = db.worksheet("Presencas")
            presencas_dados = sheet_presencas.get_all_records()
            mes_atual = datetime.date.today().month
            ano_atual = datetime.date.today().year
            
            for p in presencas_dados:
                if str(p.get("ID_Usuario", "")).strip() == ID_ALUNO_LOGADO or str(p.get("E-mail", "")).strip().lower() == txt_login_email.value.strip().lower():
                    data_p_str = str(p.get("Data_Treino", "")).strip()
                    try:
                        if "-" in data_p_str:
                            data_p = datetime.datetime.strptime(data_p_str, "%Y-%m-%d").date()
                        else:
                            data_p = datetime.datetime.strptime(data_p_str, "%d/%m/%Y").date()
                        
                        if data_p.month == mes_atual and data_p.year == ano_atual:
                            total_treinos_mes += 1
                    except Exception:
                        pass
        except Exception:
            total_treinos_mes = 0

        if É_ADMINISTRADOR:
            lista_alunos = ft.Column([
                ft.Container(
                    content=ft.Text(f"• {str(a.get('Nome', 'Sem Nome'))} - Vence: {str(a.get('Data_Vencimento', 'Pendente'))} ({str(a.get('Status_Pagamento', 'Pendente'))})", color=COLOR_TEXT_PRIMARY),
                    padding=8
                ) for a in alunos_dados
            ])
            conteudo_cadastro = ft.Container(
                content=ft.Column([
                    ft.Text("Painel Admin: Alunos Cadastrados", size=20, color=COLOR_GOLD, weight="bold"),
                    ft.Divider(color=COLOR_BLUE_BELT),
                    lista_alunos
                ]), 
                padding=24, bgcolor=COLOR_SURFACE, border_radius=12
            )
        else:
            # Blindagem de busca reativa: Localiza a coluna do nome ignorando variações de espaços
            chave_nome_limpa = next((k for k in aluno_atual.keys() if str(k).strip() == "Nome"), "Nome")
            nome_aluno = str(aluno_atual.get(chave_nome_limpa, "ATLETA")).strip().upper() if aluno_atual else "ATLETA"
            
            conteudo_cadastro = ft.Container(
                content=ft.Column([
                    ft.Text("Meu Perfil Ground One", size=22, color=COLOR_GOLD, weight="bold"),
                    ft.Text("Dados de cadastro e rendimento no tatame", size=13, color=COLOR_TEXT_MUTED),
                    ft.Divider(color=ft.Colors.GREY_800, height=15),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.PERSON, color=COLOR_BLUE_BELT, size=20),
                                ft.Text("Nome:", color=COLOR_TEXT_MUTED, size=14),
                                ft.Text(nome_aluno, color=COLOR_TEXT_PRIMARY, size=16, weight="bold")
                            ], spacing=10),
                            ft.Row([
                                ft.Icon(ft.Icons.MILITARY_TECH, color=COLOR_BLUE_BELT, size=20),
                                ft.Text("Graduação:", color=COLOR_TEXT_MUTED, size=14),
                                ft.Text(graduacao_aluno, color=COLOR_TEXT_PRIMARY, size=16, weight="bold")
                            ], spacing=10),
                        ], spacing=12),
                        bgcolor=ft.Colors.with_opacity(0.3, COLOR_BG_DARK),
                        padding=16,
                        border_radius=10,
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.1, COLOR_TEXT_MUTED))
                    ),
                    
                    ft.Container(height=5),
                    
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("MENSALIDADE", size=11, color=COLOR_TEXT_MUTED, weight="bold"),
                                    ft.Row([
                                        ft.Icon(ft.Icons.PAYMENT, color=status_color, size=18),
                                        ft.Text(status_pagamento_texto.upper(), color=status_color, size=15, weight="bold")
                                    ], spacing=5)
                                ], spacing=5),
                                bgcolor=ft.Colors.with_opacity(0.3, COLOR_BG_DARK),
                                padding=14,
                                border_radius=10,
                                expand=True,
                                border=ft.Border.all(1, ft.Colors.with_opacity(0.1, COLOR_TEXT_MUTED))
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("TREINOS NO MÊS", size=11, color=COLOR_TEXT_MUTED, weight="bold"),
                                    ft.Row([
                                        ft.Icon(ft.Icons.FITNESS_CENTER, color=COLOR_GOLD, size=18),
                                        ft.Text(f"{total_treinos_mes} Check-ins", color=COLOR_TEXT_PRIMARY, size=15, weight="bold")
                                    ], spacing=5)
                                ], spacing=5),
                                bgcolor=ft.Colors.with_opacity(0.3, COLOR_BG_DARK),
                                padding=14,
                                border_radius=10,
                                expand=True,
                                border=ft.Border.all(1, ft.Colors.with_opacity(0.1, COLOR_TEXT_MUTED))
                            )
                        ],
                        spacing=10
                    ),
                ], spacing=15),
                padding=20, 
                bgcolor=ft.Colors.TRANSPARENT, # Fundo transparente para realçar papel de parede
                border_radius=12,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.15, COLOR_BLUE_BELT))
            )

        lista_treinos = ft.Column(spacing=14)
        for t in treinos_dados:
            lista_treinos.controls.append(
                ft.Container(
                    content=ft.ListTile(
                        title=ft.Text(f"{str(t.get('Modalidade', 'Sem Modalidade'))}", size=16, weight="bold", color=COLOR_TEXT_PRIMARY),
                        subtitle=ft.Text(f"Horário: {str(t.get('Horario', 'Sem Horário'))} | Dia: {str(t.get('Dia_Semana', '-'))}\nVagas Disponíveis: {str(t.get('Vagas_Disponiveis', '0'))}", color=COLOR_TEXT_MUTED),
                        trailing=ft.Button(content=ft.Text("Presença", color="#000000", weight="bold"), data=str(t.get('ID_Treino', '')), bgcolor=COLOR_GOLD)
                    ),
                    bgcolor=COLOR_SURFACE,
                    border_radius=10,
                    padding=4,
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.1, COLOR_TEXT_MUTED))
                )
            )
        conteudo_treinos = ft.Container(
            content=ft.Column([
                ft.Text("Escolha seu Treino de Hoje", size=20, color=COLOR_BLUE_BELT, weight="bold"),
                ft.Text("Confirme seu lugar na área de tatame", size=13, color=COLOR_TEXT_MUTED),
                ft.Divider(color=ft.Colors.GREY_800),
                lista_treinos
            ], scroll=ft.ScrollMode.ALWAYS), 
            padding=20
        )

        txt_copia_cola_pix = ft.TextField(label="Código Pix Copia e Cola", border_color=COLOR_GOLD, visible=False, read_only=True, width=320)
        txt_instrucao_pix = ft.Text("Copie este código e cole no seu banco para realizar o pagamento via PIX", size=13, color=COLOR_GOLD, weight=ft.FontWeight.BOLD, visible=False, text_align=ft.TextAlign.CENTER)

        def exibir_qrcode_pix_clique(e):
            chave_pix_admin = "11951441943"
            nome_recebedor = "GROUND ONE BJJ"
            cidade_recebedor = "SAO PAULO"
            
            valor_formatado = f"{valor_numerico_planilha:.2f}"
            tamanho_valor = f"{len(valor_formatado):02d}"
            
            payload_base = f"00020101021126330014BR.GOV.BCB.PIX0111{chave_pix_admin}52040000530398654{tamanho_valor}{valor_formatado}5802BR5915{nome_recebedor}6009{cidade_recebedor}62070503***6304"
            
            def calcular_crc16(data):
                crc = 0xFFFF
                for byte in data.encode('utf-8'):
                    crc ^= (byte << 8)
                    for _ in range(8):
                        if crc & 0x8000:
                            crc = (crc << 1) ^ 0x1021
                        else:
                            crc <<= 1
                        crc &= 0xFFFF
                return f"{crc:04X}"

            crc_final = calcular_crc16(payload_base)
            txt_copia_cola_pix.value = f"{payload_base}{crc_final}"
            txt_copia_cola_pix.visible = True
            txt_instrucao_pix.visible = True
            page.update()

        conteudo_pagamento = ft.Container(
            content=ft.Column([
                ft.Text("Fatura & Mensalidade", size=20, color=COLOR_BLUE_BELT, weight="bold"),
                ft.Divider(color=ft.Colors.GREY_800),
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text("Valor da Mensalidade:", color=COLOR_TEXT_MUTED), ft.Text(texto_exibicao_valor, size=16, weight="bold", color=COLOR_TEXT_PRIMARY)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("Data de Vencimento:", color=COLOR_TEXT_MUTED), ft.Text(vencimento_texto, size=16, color=COLOR_TEXT_PRIMARY)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("Situação Atual:", color=COLOR_TEXT_MUTED), ft.Text(status_pagamento_texto.upper(), size=16, weight="bold", color=status_color)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], spacing=10),
                    bgcolor=COLOR_SURFACE, padding=20, border_radius=12, border=ft.Border.all(1, ft.Colors.with_opacity(0.1, COLOR_TEXT_MUTED))
                ),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ft.Button(content=ft.Text("Gerar Código de Pagamento Pix", color="#000000", weight="bold"), on_click=exibir_qrcode_pix_clique, bgcolor=COLOR_GOLD, width=320),
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                txt_copia_cola_pix,
                ft.Container(content=txt_instrucao_pix, width=300, padding=10)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.ALWAYS),
            padding=20
        )

        # Quarta aba estruturada com contêineres transparentes e rolagem interna
        conteudo_ebook = ft.Container(
            content=ft.Column([
                ft.Text("eBook Ground One BJJ", size=22, color=COLOR_GOLD, weight="bold", text_align=ft.TextAlign.CENTER),
                ft.Divider(color=ft.Colors.with_opacity(0.2, COLOR_TEXT_MUTED)),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Da Graduação", size=20, color=COLOR_GOLD, weight="bold", text_align=ft.TextAlign.CENTER),
                        ft.Text("2026", size=14, color=COLOR_TEXT_MUTED, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=10),
                        ft.Text("Art. 1° - As graduações só se darão apos avaliação presencial física e técnica seguindo, concomitantemente, os seguintes requisitos:\n"
                                "I - participação activa em 45 (quarenta e cinco) treinos no semestre;\n"
                                "II - avaliação em teste físico coletivo; III - apresentação do cata técnico.\n"
                                "Parágrafo único - Importante também, que a critério e exclusivamente sobre análise e vontade do Mestre avaliador, alguns requisitos deste artigo podem sofrer alterações dependendo da condição subjetiva de cada caso (aluno), porém, jamais será produto de negociação.\n\n"
                                "Art. 2° - Devdue aos eventos de graduação serem semestrais, junho/julho e novembro/dezembro e não anuais, a contagem dos treinos de todos os alunos, graduandos ou não graduandos será zerada a cada graduação não se cumulando treinos de um semestre para outro semestre, visando assim a habitualidade de comparecimento nos treinos de forma a passar por todas as fases importantes para a graduação, pois a eventualidade gera a impossibilidade de acompanhamento didático satisfatório.\n\n"
                                "Art. 3° - a graduação se dará de grau em grau independentemente da cor da faixa.\n"
                                "Parágrafo único – O disposto neste artigo poderá sofrer alteração, a critério e exclusivamente sobre análise e vontade do Mestre avaliador, porém, jamais será produto de negociação.\n\n"
                                "Art. 4° - O valor a ser pago por cada graduação será divulgado quando da divulgação oficial da data de cada evento, devendo o pagamento ser efetuado até 10 (dez) dias antes da realização do evento, sendo condição essencial para a graduação.\n"
                                "Paragrafo Unico - Alunos menores de 10 (dez) anos pagarão metade do valor estipulado.\n\n"
                                "Art. 5° - A aquisição de faixa nova, in caso de troca de faixa, será por conta do aluno, não sendo incluído no valor da graduação.\n\n"
                                "Art. 6° - A graduação só será possível com uniforme especificamente confeccionado para Jiu-Jitsu da seguinte forma:\n"
                                "– kimono na cor branca;\n"
                                "II - devidamente personalizado com o patch da equipe;\n"
                                "III - faixa com a ponta preta.\n\n"
                                "Art. 7° - A graduação não se dará sem que se observe o tempo mínimo exigido pelas normas da CBJJ (Confederação Brasileira de Jiu Bitsu).\n"
                                "§ 1° - A permanência mínima de um aluno adulto em cada faixa (branca, azul, roxa ou marrom) é de 2 (dois) anos sem prazo máximo de permanência na faixa, dependendo a troca de faixa, da análise em cada critério anterior.\n"
                                "§ 2° - A permanência mínima de um aluno mirim, infantil. Infanto-juvenil e juvenil em cada faixa (branca, cinza e branco, cinza, cinza e preto, amarela e branco, amarela, amarela e preto, laranja e branco, laranja, laranja e preto, verde e branco, verde ou verde e preto) é de 6 (seis) meses, sem prazo máximo de permanência na faixa, dependendo a troca de faixa, da análise em cada critério anterior.\n\n"
                                "Art. 8° - Menores de 16 (dezesseis) anos só poderão participar do evento de graduação com a presença de um maior responsável.\n\n"
                                "Art. 9° - A lista com os nomes dos graduandos e suas respectivas graduações deverá ser disponibilizada 30 (trinta) dias antes da data agendada para a realização do evento e deverá ser entregue ao Mestre Fluído para a confecção dos certificados que deverão ser pagos até 10 dias antes de sua confecção.\n"
                                "Paragrafo Único - Em toda troca de faixa da branca para a azul, da azul para a roxa, da roxa para a marrom e da marrom para a preta é obrigatório a confecção e entrega de certificados, com um custo de R$ 20,00 cada certificado, porém, nas graduação de graus e para faixas infantis e infanto juvenis não é obrigatório a entrega de certificado, ficando a critério do professor, mas quando optar por entregar o certificado, o custo de cada um também é de R$ 20.00\n\n"
                                "Art. 10° - Após Cumprido todos os requisitos, regras é critérios para a graduação, a participação do aluno no evento não será obrigatória dependendo também de sua própria intenção em graduar (gradua se quiser).\n\n"
                                "Art. 11° - Somente um mestre/professor, no mínimo faixa preta 3 graus pode promover um aluno faixa marrom à faixa preta.\n\n"
                                "Art. 12° - Somente um professor, no mínimo faixa preta pode promover um aluno faixa roxa à faixa marrom.\n\n"
                                "Art. 13° - Instrutor faixa marrom só pode promover a graduação de seus alunos, até a faixa roxa e na presença de seu mestre/professor ou professor faixa preta.\n\n"
                                "Art. 14° - Auxiliar, abaixo da faixa marrom não pode graduar nenhum aluno, devendo, caso cumprido todas as condições para a graduação, submeter seus alunos à avaliação e decisão de seu mestre/professor ou professor faixa preta, ficando a critério também deste último graduar ou não os alunos.\n\n"
                                "Art. 15° - Um aluno só poderá ser graduado à faixa roxa, marrom ou preta, se estiver devidamente registrado na FPJJ como atleta da EQUIPE GROUND ONE BRASILIAN JIU JITSU.\n\n"
                                "Art. 16° - Para que um aluno seja graduado à faixa roxa, marrom ou preta, é obrigatório ter realizado o curso de primeiro socorros ministrado semestralmente pela EQUIPE.\n\n"
                                "Art. 17° - Para que um aluno seja graduado à faixa roxa, marrom ou preta, é obrigatório estar devidamente inscrito na FPJJ, Federação Paulista de Jiu Jiu, e com carteirinha activa.\n\n"
                                "Art. 18° - Um aluno só poderá ser graduado às faixas marrom ou preta se estiver matriculado e treinando comprovadamente a pelo menos 6 (seis) meses com um Professor ou Mestre/Professor conforme disposto nos artigos 11° e 12° deste Estatuto.\n\n"
                                "Art. 19° - Para que um aluno seja graduado às faixas marrom ou preta, é obrigatório ter realizado o curso de arbitragem ministrado semestralmente pela EQUIPE.",
                                color=COLOR_TEXT_PRIMARY, size=15
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.Colors.TRANSPARENT, 
                    padding=10, 
                    border_radius=12, 
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.15, COLOR_BLUE_BELT))
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.ALWAYS),
            padding=10,
            bgcolor=ft.Colors.TRANSPARENT,
            expand=True
        )

        area_conteudo_dinamico = ft.Container(content=conteudo_cadastro, expand=True, bgcolor=ft.Colors.TRANSPARENT)

        def alternar_painel_visual(e):
            opcao = str(e.control.data)
            area_conteudo_dinamico.content = None 
            
            if opcao == "perfil":
                area_conteudo_dinamico.content = conteudo_cadastro
            elif opcao == "treinos":
                area_conteudo_dinamico.content = conteudo_treinos
            elif opcao == "financeiro":
                area_conteudo_dinamico.content = conteudo_pagamento
            elif opcao == "ebook":
                area_conteudo_dinamico.content = conteudo_ebook
                
            area_conteudo_dinamico.update()
            page.update()

        # Barra superior reconfigurada de botões com rolagem horizontal adaptativa
        menu_botoes = ft.Row(
            controls=[
                ft.Button(content=ft.Text("Meu Perfil", color=COLOR_TEXT_PRIMARY, weight="bold"), data="perfil", on_click=alternar_painel_visual, bgcolor=COLOR_BLUE_BELT),
                ft.Button(content=ft.Text("Treinos", color=COLOR_TEXT_PRIMARY, weight="bold"), data="treinos", on_click=alternar_painel_visual, bgcolor=COLOR_BLUE_BELT),
                ft.Button(content=ft.Text("Mensalidade", color=COLOR_TEXT_PRIMARY, weight="bold"), data="financeiro", on_click=alternar_painel_visual, bgcolor=COLOR_BLUE_BELT),
                ft.Button(content=ft.Text("eBook", color=COLOR_TEXT_PRIMARY, weight="bold"), data="ebook", on_click=alternar_painel_visual, bgcolor=COLOR_BLUE_BELT),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
            scroll=ft.ScrollMode.ADAPTIVE
        )

        interface_principal = ft.Container(
            content=ft.Column([
                alerta_topo,
                menu_botoes,
                ft.Divider(color=ft.Colors.GREY_800),
                area_conteudo_dinamico,
                faixa_graduacao_rodape
            ], expand=True, spacing=10),
            padding=12, expand=True, bgcolor=ft.Colors.TRANSPARENT
        )

        page.controls.clear()
        page.add(
            ft.Stack(
                controls=[
                    ft.Image(
                        src="fundo.jpeg",
                        fit="cover",
                        expand=True,
                        opacity=0.15,
                        width=page.window_width if hasattr(page, "window_width") else None,
                        height=page.window_height if hasattr(page, "window_height") else None
                    ),
                    interface_principal
                ],
                expand=True
            )
        )
        page.update()

    # -------------------------------------------------------------------------
    # FLUXO DE ALTERNÂNCIA DE TELAS
    # -------------------------------------------------------------------------
    container_campos_login = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14)

    def mudar_modo_login():
        container_campos_login.controls.clear()
        
        def intermedio_login(e):
            btn_entrar.disabled = True
            btn_entrar.content = ft.Row(
                [
                    ft.ProgressRing(width=16, height=16, stroke_width=2, color="#000000"),
                    ft.Text("Acessando...", color="#000000", weight="bold")
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            )
            btn_entrar.update()
            executar_login(e)

        btn_entrar.on_click = intermedio_login

        container_campos_login.controls.extend([
            ft.Text("Acesse sua Conta", size=18, weight="bold", color=COLOR_TEXT_PRIMARY),
            txt_login_email,
            txt_login_senha,
            lbl_erro_login,
            btn_entrar
        ])
        page.update()

    def abrir_tela_cadastro(e):
        page.controls.clear()
        
        layout_cadastro = ft.Container(
            content=ft.Column([
                ft.Row([ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=COLOR_GOLD, on_click=lambda _: carregar_tela_autenticacao())]),
                ft.Text("Faça seu Cadastro", size=24, weight="bold", color=COLOR_GOLD),
                ft.Text("Preencha as informações para ingressar no tatame", size=13, color=COLOR_TEXT_MUTED),
                ft.Divider(color=ft.Colors.GREY_800),
                ft.Column([
                    txt_nome, txt_tel, txt_cpf, txt_nasc, txt_profissao,
                    ft.Row(
                        controls=[
                            txt_cep,
                            ft.IconButton(
                                icon=ft.Icons.SEARCH,
                                icon_color=COLOR_GOLD,
                                tooltip="Verificar CEP online",
                                on_click=disparar_busca_cep,
                                width=60
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=5,
                        width=300
                    ),
                    txt_rua, txt_num, txt_comp, txt_bairro, txt_cidade, txt_uf,
                    txt_graduacao,
                    txt_email, txt_email_conf, txt_senha, txt_senha_conf,
                    lbl_lembrete_senha,
                ], scroll=ft.ScrollMode.ALWAYS, height=380, spacing=12),

                ft.Divider(color=ft.Colors.GREY_800),
                btn_enviar
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.Alignment(0, 0),
            padding=20,
            expand=True
        )

        page.add(
            ft.Stack(
                controls=[
                    ft.Image(
                        src="fundo.jpeg", fit="cover", expand=True, opacity=0.15,
                        width=page.window_width if hasattr(page, "window_width") else None,
                        height=page.window_height if hasattr(page, "window_height") else None
                    ),
                    layout_cadastro
                ], expand=True
            )
        )
        page.update()

    def carregar_tela_autenticacao():
        page.controls.clear()
        container_campos_login.controls.clear()
        
        linha_botoes_selecao = ft.Row(
            controls=[
                ft.Button(content=ft.Text("Entrar", color=COLOR_TEXT_PRIMARY, weight="bold"), on_click=lambda _: mudar_modo_login(), bgcolor=COLOR_BLUE_BELT),
                ft.Button(content=ft.Text("Cadastrar-se", color=COLOR_GOLD, weight="bold"), on_click=abrir_tela_cadastro),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )

        caixa_autenticacao_transparente = ft.Container(
            content=ft.Column([
                ft.Container(height=20),
                ft.Text("GROUND ONE BJJ", size=26, weight="bold", color=COLOR_TEXT_PRIMARY),
                ft.Text("Gestão de Atletas & Treinos", size=13, color=COLOR_TEXT_MUTED),
                ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
                linha_botoes_selecao,
                ft.Divider(height=25, color=ft.Colors.TRANSPARENT),
                container_campos_login
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.TRANSPARENT,
            padding=30,
            border_radius=16,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.15, COLOR_TEXT_MUTED))
        )

        layout_login_centralizado = ft.Container(
            content=caixa_autenticacao_transparente,
            alignment=ft.alignment.Alignment(0, 0),
            expand=True
        )

        page.add(
            ft.Stack(
                controls=[
                    ft.Image(
                        src="fundo.jpeg",
                        fit="cover",
                        expand=True,
                        opacity=0.35,
                        width=page.window_width if hasattr(page, "window_width") else None,
                        height=page.window_height if hasattr(page, "window_height") else None
                    ),
                    layout_login_centralizado
                ],
                expand=True
            )
        )
        page.update()

    carregar_tela_autenticacao()

import flet_fastapi
