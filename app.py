# import streamlit as st
# import sqlite3
# import pandas as pd
# import hashlib
# import io
# from datetime import datetime

# # Importações da biblioteca ReportLab para geração de documentos formais em PDF
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib import colors

# # Importação para extração e leitura de ficheiros PDF submetidos
# import pypdf


# # -----------------------------------------------------------------------------
# # CONFIGURAÇÃO DA PÁGINA STREAMLIT
# # -----------------------------------------------------------------------------

# st.set_page_config(
#     page_title="CATS-SESP - Governança, Segurança e Ativos Tecnológicos",
#     page_icon="",
#     layout="wide"
# )


# # -----------------------------------------------------------------------------
# # INICIALIZAÇÃO E MODELAGEM DO BANCO DE DADOS (SQLite)
# # -----------------------------------------------------------------------------

# def init_db():
#     conn = sqlite3.connect("cats_sesp.db")
#     c = conn.cursor()
    
#     # Tabela: Projetos
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS projetos (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             nome TEXT NOT NULL,
#             processo TEXT,
#             institucion TEXT,
#             responsavel_tecnico TEXT,
#             data_inicio TEXT
#         )
#     ''')
    
#     # Tabela: Matriz de Titularidade 
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS matriz_titularidade (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             projeto_id INTEGER,
#             nome_ativo TEXT,
#             categoria TEXT,
#             titular_sesp BOOLEAN,
#             titular_instituicao BOOLEAN,
#             direito_exploracao BOOLEAN,
#             direito_transferencia BOOLEAN,
#             FOREIGN KEY (projeto_id) REFERENCES projetos (id)
#         )
#     ''')

#     # Tabela: Inventário de IA
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS inventario_ia (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             projeto_id INTEGER,
#             modelo_nome TEXT,
#             modelo_base TEXT,
#             licenca TEXT,
#             fine_tuning BOOLEAN,
#             metodo_ft TEXT,
#             acuracia REAL,
#             f1_score REAL,
#             FOREIGN KEY (projeto_id) REFERENCES projetos (id)
#         )
#     ''')

#     # Tabela: Checklists de Encerramento e Aceite
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS encerramento_aceite (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             projeto_id INTEGER,
#             codigo_fonte_entregue BOOLEAN,
#             repositorio_git BOOLEAN,
#             pesos_ia_entregues BOOLEAN,
#             dados_devolvidos_eliminados BOOLEAN,
#             vendor_lockin_identificado BOOLEAN,
#             status_encerramento TEXT,
#             data_registro TEXT,
#             FOREIGN KEY (projeto_id) REFERENCES projetos (id)
#         )
#     ''')

#     # Tabela: Auditoria de Conformidade PoSIC e CGD-SI (NSIC-05)
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS auditoria_posic (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             projeto_id INTEGER,
#             uso_ia_pessoal BOOLEAN,
#             prompts_sensiveis_externos BOOLEAN,
#             ripd_aprovado BOOLEAN,
#             mfa_ativo BOOLEAN,
#             retencao_logs_dias INTEGER,
#             camara_tecnica_designada TEXT,
#             status_conformidade TEXT,
#             data_auditoria TEXT,
#             FOREIGN KEY (projeto_id) REFERENCES projetos (id)
#         )
#     ''')
    
#     conn.commit()
#     conn.close()

# init_db()

# def run_query(query, params=()):
#     conn = sqlite3.connect("cats_sesp.db")
#     c = conn.cursor()
#     c.execute(query, params)
#     conn.commit()
#     conn.close()


# # -----------------------------------------------------------------------------
# # MOTOR DE GERAÇÃO DE PDFS FORMAIS COM HASH SHA-256
# # -----------------------------------------------------------------------------

# def gerar_pdf_parecer_tecnico(projeto_nome, processo, instituicao, status_audit, câmara, parecer_detalhes):
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
#     story = []
    
#     styles = getSampleStyleSheet()
#     title_style = ParagraphStyle(
#         'TitleStyle',
#         parent=styles['Heading1'],
#         fontSize=14,
#         textColor=colors.HexColor("#002B49"),
#         alignment=1,
#         spaceAfter=12
#     )
#     subtitle_style = ParagraphStyle(
#         'SubtitleStyle',
#         parent=styles['Normal'],
#         fontSize=10,
#         textColor=colors.HexColor("#555555"),
#         alignment=1,
#         spaceAfter=20
#     )
#     normal_style = styles['Normal']
#     bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontName='Helvetica-Bold')

#     # Cabeçalho Institucional
#     story.append(Paragraph("ESTADO DO PARANÁ - SECRETARIA DA SEGURANÇA PÚBLICA", title_style))
#     story.append(Paragraph("SISTEMA CATS-SESP | PARECER TÉCNICO DE GOVERNANÇA E AUDITORIA", subtitle_style))
#     story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#002B49"), spaceAfter=15))
    
#     # Dados do Projeto
#     data_emissao = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
#     story.append(Paragraph(f"<b>Projeto Auditado:</b> {projeto_nome}", normal_style))
#     story.append(Paragraph(f"<b>Processo Administrativo:</b> {processo}", normal_style))
#     story.append(Paragraph(f"<b>Instituição Executora:</b> {instituicao}", normal_style))
#     story.append(Paragraph(f"<b>Data da Auditoria:</b> {data_emissao}", normal_style))
#     story.append(Paragraph(f"<b>Câmara Técnica Designada:</b> {câmara}", normal_style))
#     story.append(Spacer(1, 15))
    
#     # Resultado da Avaliação
#     color_status = colors.green if "APROVADO" in status_audit else colors.red
#     story.append(Paragraph(f"<b>STATUS DA AUDITORIA:</b> <font color='{color_status.hexval()}'>{status_audit}</font>", normal_style))
#     story.append(Spacer(1, 10))

#     story.append(Paragraph("<b>Detalhamento da Análise de Compliance e Segurança:</b>", bold_style))
#     story.append(Spacer(1, 5))
    
#     for item in parecer_detalhes:
#         story.append(Paragraph(f"• {item}", normal_style))
#         story.append(Spacer(1, 3))
        
#     story.append(Spacer(1, 20))
#     story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=15))
    
#     # Cálculo de Assinatura e Integridade Hash SHA-256
#     conteudo_para_hash = f"{projeto_nome}-{processo}-{status_audit}-{data_emissao}".encode('utf-8')
#     hash_documento = hashlib.sha256(conteudo_para_hash).hexdigest().upper()
    
#     story.append(Paragraph("<b>Código de Validação e Autenticidade (SHA-256):</b>", bold_style))
#     story.append(Paragraph(f"<font fontName='Courier' size=8>{hash_documento}</font>", normal_style))
#     story.append(Spacer(1, 10))
#     story.append(Paragraph("<i>Documento gerado automaticamente pelo Sistema CATS-SESP conforme Resolução SESP/PR 2026, PoSIC v2.0 e Deliberação CGD-SI nº 5/2025.</i>", ParagraphStyle('Foot', parent=normal_style, fontSize=8, textColor=colors.gray)))

#     doc.build(story)
#     buffer.seek(0)
#     return buffer


# # -----------------------------------------------------------------------------
# # NAVEGAÇÃO DA APLICAÇÃO (SIDEBAR)
# # -----------------------------------------------------------------------------

# st.sidebar.title("CATS - SESP/PR")
# st.sidebar.caption("Cadastro de Ativos Tecnológicos e Governança")

# menu = st.sidebar.radio(
#     "Selecione o Módulo:",
#     [
#         "Gestão de Projetos",
#         "Matriz de Titularidade",
#         "Inventário de IA",
#         "Checklist de Aceite",
#         "Auditoria PoSIC & CGD-SI (NSIC-05)",
#         "Varredura de Sigilo em PDFs (RAG/IA)",
#         "Painel de Auditoria e Relatórios"
#     ]
# )

# st.sidebar.markdown("---")
# st.sidebar.info(
#     "Sistema em conformidade com:\n"
#     "- Resolução SESP/PR 2026\n"
#     "- PoSIC SESP-PR v2.0 (NSIC-01 a 11)\n"
#     "- Deliberação CGD-SI nº 5/2025\n"
#     "- Guia de PDTIC do SISP v2.1"
# )


# # -----------------------------------------------------------------------------
# # MÓDULO 1: GESTÃO DE PROJETOS
# # -----------------------------------------------------------------------------

# if menu == "Gestão de Projetos":
#     st.title("📁 Cadastro e Gestão de Projetos de Inovação / TI")
#     st.caption("Cadastre os projetos para vincular ativos tecnológicos, modelos de IA, auditorias e termos contratuais.")

#     with st.expander("➕ Cadastrar Novo Projeto", expanded=True):
#         with st.form("form_novo_projeto"):
#             col1, col2 = st.columns(2)
#             nome_p = col1.text_input("Nome do Projeto *")
#             proc_p = col2.text_input("Número do Processo Administrativo")
#             inst_p = col1.text_input("Instituição Executora (ex: UFPR, FAASP, ICT, Empresa)")
#             resp_p = col2.text_input("Responsável Técnico")
#             data_p = st.date_input("Data de Início", datetime.now())

#             btn_salvar_proj = st.form_submit_button("Cadastrar Projeto")
#             if btn_salvar_proj:
#                 if nome_p:
#                     run_query(
#                         "INSERT INTO projetos (nome, processo, institucion, responsavel_tecnico, data_inicio) VALUES (?, ?, ?, ?, ?)",
#                         (nome_p, proc_p, inst_p, resp_p, str(data_p))
#                     )
#                     st.success(f"Projeto '{nome_p}' cadastrado com sucesso!")
#                 else:
#                     st.error("O nome do projeto é obrigatório.")

#     st.subheader("Projetos Cadastrados no CATS-SESP")
#     conn = sqlite3.connect("cats_sesp.db")
#     df_proj = pd.read_sql_query("SELECT id AS ID, nome AS Projeto, processo AS Processo, institucion AS Instituicao, responsavel_tecnico AS Responsavel, data_inicio AS Inicio FROM projetos", conn)
#     conn.close()
#     st.dataframe(df_proj, use_container_width=True)


# # -----------------------------------------------------------------------------
# # MÓDULO 2: MATRIZ DE TITULARIDADE
# # -----------------------------------------------------------------------------

# elif menu == "Matriz de Titularidade":
#     st.title("Matriz de Titularidade, Direitos de Uso e Exploração")
#     st.caption("Classificação dos ativos do projeto conforme diretrizes da Resolução SESP/PR.")

#     conn = sqlite3.connect("cats_sesp.db")
#     df_proj = pd.read_sql_query("SELECT id, nome FROM projetos", conn)
#     conn.close()

#     if df_proj.empty:
#         st.warning("Nenhum projeto cadastrado. Cadastre um projeto primeiro no Módulo 'Gestão de Projetos'.")
#     else:
#         proj_dict = dict(zip(df_proj['nome'], df_proj['id']))
#         selected_proj_name = st.selectbox("Selecione o Projeto:", list(proj_dict.keys()))
#         selected_proj_id = proj_dict[selected_proj_name]

#         with st.form("form_matriz"):
#             st.subheader("1. Classificação do Ativo Tecnológico")
#             col1, col2 = st.columns(2)
#             nome_ativo = col1.text_input("Nome do Ativo (ex: Módulo de Visão, Algoritmo de Busca, Base Consolidada)")
#             categoria = col2.selectbox(
#                 "Categoria do Ativo:",
#                 [
#                     "A - Background IP SESP/PR (Preexistente da SESP)",
#                     "B - Background IP Executora (Preexistente da Universidade/Empresa)",
#                     "C - Tecnologia de Terceiros (Open Source ou Proprietária)",
#                     "D - Foreground IP (Criado especificamente no projeto)",
#                     "E - Resultado Derivado (Modificação, fine-tuning, combinação)"
#                 ]
#             )

#             st.subheader("2. Definição de Direitos Patrimoniais e Operacionais")
#             c1, c2, c3, c4 = st.columns(4)
#             tit_sesp = c1.checkbox("Titularidade SESP/PR")
#             tit_inst = c2.checkbox("Titularidade Instituição Executora")
#             dir_exp = c3.checkbox("Direito de Exploração Econômica")
#             dir_transf = c4.checkbox("Direito de Transferência a Terceiros")

#             st.subheader("3. Direitos Assegurados à SESP/PR")
#             m1, m2, m3, m4 = st.columns(4)
#             m1.checkbox("Licença Perpétua e Irrevogável", value=True)
#             m2.checkbox("Direito de Modificação/Adaptação", value=True)
#             m3.checkbox("Direito de Manutenção por Terceiros", value=True)
#             m4.checkbox("Direito de Auditoria", value=True)

#             btn_salvar_matriz = st.form_submit_button("Registrar Ativo na Matriz")
#             if btn_salvar_matriz:
#                 run_query(
#                     '''INSERT INTO matriz_titularidade 
#                        (projeto_id, nome_ativo, categoria, titular_sesp, titular_instituicao, direito_exploracao, direito_transferencia)
#                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
#                     (selected_proj_id, nome_ativo, categoria[0], tit_sesp, tit_inst, dir_exp, dir_transf)
#                 )
#                 st.success(f"Ativo '{nome_ativo}' vinculado ao projeto e gravado com sucesso!")

#         st.subheader(f"Matriz de Ativos do Projeto: {selected_proj_name}")
#         conn = sqlite3.connect("cats_sesp.db")
#         df_matriz = pd.read_sql_query(
#             f"SELECT nome_ativo AS Ativo, categoria AS Cat, titular_sesp AS 'SESP Titular', titular_instituicao AS 'Inst. Titular', direito_exploracao AS Exploracao, direito_transferencia AS Transferencia FROM matriz_titularidade WHERE projeto_id = {selected_proj_id}",
#             conn
#         )
#         conn.close()
#         st.dataframe(df_matriz, use_container_width=True)


# # -----------------------------------------------------------------------------
# # MÓDULO 3: INVENTÁRIO DE IA 
# # -----------------------------------------------------------------------------

# elif menu == "Inventário de IA":
#     st.title("Inventário de Inteligência Artificial e Modelos Derivados")
#     st.caption("Conforme diretrizes da Resolução SESP/PR e NSIC-05.")

#     conn = sqlite3.connect("cats_sesp.db")
#     df_proj = pd.read_sql_query("SELECT id, nome FROM projetos", conn)
#     conn.close()

#     if df_proj.empty:
#         st.warning("Cadastre um projeto antes de inventariar um modelo de IA.")
#     else:
#         proj_dict = dict(zip(df_proj['nome'], df_proj['id']))
#         selected_proj_name = st.selectbox("Selecione o Projeto:", list(proj_dict.keys()), key="ia_proj")
#         selected_proj_id = proj_dict[selected_proj_name]

#         with st.form("form_ia_detalhado"):
#             c1, c2, c3 = st.columns(3)
#             modelo_nome = c1.text_input("Nome Interno do Modelo Resultante")
#             modelo_base = c2.text_input("Modelo-Base Utilizado (ex: Llama-3-8B, YOLOv8)")
#             licenca = c3.text_input("Licença (ex: Apache 2.0, MIT, Llama License)")

#             fez_ft = st.radio("Foi realizado Fine-Tuning / Ajuste Fino?", ["Não", "Sim"])
#             metodo_ft = st.multiselect("Métodos Empregados:", ["Full Fine-Tuning", "LoRA", "QLoRA", "Adapter", "Transfer Learning"]) if fez_ft == "Sim" else []

#             st.write("**Métricas de Avaliação de Desempenho:**")
#             m1, m2 = st.columns(2)
#             acuracia = m1.number_input("Acurácia (0.0 a 1.0)", 0.0, 1.0, 0.90)
#             f1 = m2.number_input("F1-Score (0.0 a 1.0)", 0.0, 1.0, 0.88)

#             btn_ia = st.form_submit_button("Gravar Modelo no Inventário")
#             if btn_ia:
#                 run_query(
#                     '''INSERT INTO inventario_ia (projeto_id, modelo_nome, modelo_base, licenca, fine_tuning, metodo_ft, acuracia, f1_score)
#                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
#                     (selected_proj_id, modelo_nome, modelo_base, licenca, (fez_ft == "Sim"), ", ".join(metodo_ft), acuracia, f1)
#                 )
#                 st.success("Modelo registrado no inventário do CATS-SESP!")

#         st.subheader(f"Modelos Inventariados no Projeto: {selected_proj_name}")
#         conn = sqlite3.connect("cats_sesp.db")
#         df_ia = pd.read_sql_query(
#             f"SELECT modelo_nome AS Modelo, modelo_base AS 'Modelo Base', licenca AS Licenca, fine_tuning AS 'Fine-Tuning', metodo_ft AS Metodo, acuracia AS Acuracia, f1_score AS 'F1-Score' FROM inventario_ia WHERE projeto_id = {selected_proj_id}",
#             conn
#         )
#         conn.close()
#         st.dataframe(df_ia, use_container_width=True)


# # -----------------------------------------------------------------------------
# # MÓDULO 4: CHECKLIST DE ACEITE E ENCERRAMENTO 
# # -----------------------------------------------------------------------------

# elif menu == "Checklist de Aceite":
#     st.title("Checklist de Recebimento, Aceite e Desmobilização Tecnológica")
#     st.caption("Verificação técnica obrigatória para emissão de Termo de Aceite Definitivo e liberação financeira.")

#     conn = sqlite3.connect("cats_sesp.db")
#     df_proj = pd.read_sql_query("SELECT id, nome FROM projetos", conn)
#     conn.close()

#     if df_proj.empty:
#         st.warning("Nenhum projeto cadastrado.")
#     else:
#         proj_dict = dict(zip(df_proj['nome'], df_proj['id']))
#         selected_proj_name = st.selectbox("Selecione o Projeto para Encerramento:", list(proj_dict.keys()), key="enc_proj")
#         selected_proj_id = proj_dict[selected_proj_name]

#         with st.form("form_aceite"):
#             st.subheader("1. Entregáveis de Software e Código-Fonte")
#             c1, c2, c3 = st.columns(3)
#             cod_entregue = c1.checkbox("Código-fonte integral disponibilizado (sem ofuscação)")
#             repo_git = c2.checkbox("Repositório Git com histórico e branches entregue")
#             doc_api = c3.checkbox("APIs e Arquitetura documentadas")

#             st.subheader("2. Entregáveis de Inteligência Artificial e Dados")
#             i1, i2, i3 = st.columns(3)
#             pesos_entregues = i1.checkbox("Pesos/Checkpoints do Modelo entregues")
#             dados_tratados = i2.checkbox("Dados da SESP devolvidos/eliminados (com declaração)")
#             ambientes_limpos = i3.checkbox("Ambientes temporários de teste eliminados")

#             st.subheader("3. Prevenção ao Vendor Lock-In e Continuidade Operacional")
#             v1, v2 = st.columns(2)
#             vendor_lockin = v1.radio("Risco de Vendor Lock-in Identificado?", ["Não", "Sim"])
#             capacitacao = v2.checkbox("Treinamento e Capacitação da equipe SESP realizados")

#             st.subheader("4. Parecer Final do Encerramento")
#             status_final = st.selectbox(
#                 "Conclusão da Fiscalização Técnica:",
#                 [
#                     "ENCERRAMENTO APROVADO (Aceite Definitivo)",
#                     "ENCERRAMENTO APROVADO COM RESSALVAS (Pendências não críticas)",
#                     "ENCERRAMENTO NÃO APROVADO (Pendências críticas de código/dados/modelos)"
#                 ]
#             )

#             btn_encerramento = st.form_submit_button("Registrar Termo de Aceite / Encerramento")
#             if btn_encerramento:
#                 run_query(
#                     '''INSERT INTO encerramento_aceite 
#                        (projeto_id, codigo_fonte_entregue, repositorio_git, pesos_ia_entregues, dados_devolvidos_eliminados, vendor_lockin_identificado, status_encerramento, data_registro)
#                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
#                     (selected_proj_id, cod_entregue, repo_git, pesos_entregues, dados_tratados, (vendor_lockin == "Sim"), status_final, str(datetime.now().strftime("%Y-%m-%d %H:%M")))
#                 )
#                 if "NÃO APROVADO" in status_final:
#                     st.error("Encerramento NÃO APROVADO retido até sanar as pendências apontadas.")
#                 else:
#                     st.success("Termo de Aceite registrado com sucesso!")


# # -----------------------------------------------------------------------------
# # MÓDULO 5: AUDITORIA POSIC & CGD-SI (NSIC-05) + GERAÇÃO DE PDF
# # -----------------------------------------------------------------------------

# elif menu == "Auditoria PoSIC & CGD-SI (NSIC-05)":
#     st.title("Auditoria de Conformidade PoSIC SESP-PR & CGD-SI")
#     st.caption("Verificação automatizada de conformidade com a NSIC-05 (Uso de IA) e a Deliberação CGD-SI nº 5/2025.")

#     conn = sqlite3.connect("cats_sesp.db")
#     df_proj = pd.read_sql_query("SELECT id, nome, processo, institucion FROM projetos", conn)
#     conn.close()

#     if df_proj.empty:
#         st.warning("Cadastre um projeto no Módulo 'Gestão de Projetos' para realizar a auditoria.")
#     else:
#         proj_dict = {row['nome']: (row['id'], row['processo'], row['institucion']) for _, row in df_proj.iterrows()}
#         selected_proj_name = st.selectbox("Selecione o Projeto para Auditagem:", list(proj_dict.keys()), key="audit_posic")
#         selected_proj_id, proc_val, inst_val = proj_dict[selected_proj_name]

#         with st.form("form_auditoria_posic"):
#             st.subheader("1. Verificação de Regras para Inteligência Artificial (NSIC-05)")
#             ia_pessoal = st.checkbox("Utiliza ferramentas de IA através de contas pessoais/gratuitas (ex: ChatGPT/Gemini pessoal)?")
#             prompts_sensiveis = st.checkbox("Alimenta modelos externos de IA com dados pessoais, inquéritos ou detalhes operacionais?")
#             ripd_ok = st.checkbox("Possui Relatório de Impacto à Proteção de Dados (RIPD) aprovado pelo Controlador?")

#             st.subheader("2. Verificação de Segurança da Informação (NSIC-02 / NSIC-10)")
#             mfa_ok = st.checkbox("Autenticação Multifator (MFA/2FA) ativada para acessos externos e administrativos?")
#             retencao_logs = st.number_input("Prazo configurado de retenção de logs de acesso (em dias):", min_value=0, max_value=365, value=180)

#             st.subheader("3. Roteamento de Governança Estadual (CGD-SI nº 5/2025)")
#             camara = st.selectbox(
#                 "Câmara Técnica Responsável para Parecer:",
#                 [
#                     "CT-IA (Inteligência Artificial)",
#                     "CT-SID (Segurança da Informação e Dados)",
#                     "CT-GOA (Gestão Orçamentária e Aquisições)",
#                     "CT-GSTIC (Gestão de Serviços de TIC)",
#                     "CT-NDGD (Normas de Governança Digital)",
#                     "CT-IPE (Integração e Planejamento Estratégico)"
#                 ]
#             )

#             btn_auditar = st.form_submit_button("Executar Diagnóstico e Gerar Parecer")

#             if btn_auditar:
#                 inconformidades = []
#                 parecer_detalhes = []
                
#                 if ia_pessoal:
#                     inconformidades.append("NSIC-05 Art. 4: É VEDADO o uso de IA via contas pessoais ou gratuitas.")
#                     parecer_detalhes.append("VIOLAÇÃO: Identificado uso de contas de IA não homologadas pela CTIC.")
#                 else:
#                     parecer_detalhes.append("CONFORME: Ausência de uso de ferramentas de IA não corporativas.")

#                 if prompts_sensiveis:
#                     inconformidades.append("NSIC-05 Art. 4: Proibido o fornecimento de prompts com dados sensíveis/policiais a IAs externas.")
#                     parecer_detalhes.append("VIOLAÇÃO: Risco de exfiltração de dados sensíveis em prompts de IA externa.")
#                 else:
#                     parecer_detalhes.append("CONFORME: Nenhum dado sensível é transmitido para modelos externos.")

#                 if not ripd_ok:
#                     inconformidades.append("NSIC-05 Item IV: Projetos de IA exigem RIPD aprovado pelo Controlador.")
#                     parecer_detalhes.append("PENDÊNCIA: Falta a apresentação de Relatório de Impacto à Proteção de Dados.")
#                 else:
#                     parecer_detalhes.append("CONFORME: RIPD devidamente aprovado pelo Controlador.")

#                 if not mfa_ok:
#                     inconformidades.append("NSIC-02 / NSIC-10: MFA é obrigatório para VPN e acessos sensíveis.")
#                     parecer_detalhes.append("PENDÊNCIA: Autenticação Multifator não está ativada nas credenciais críticas.")
#                 else:
#                     parecer_detalhes.append("CONFORME: Autenticação de Múltiplos Fatores habilitada.")

#                 if retencao_logs < 90:
#                     inconformidades.append("NSIC-03 / NSIC-08: A retenção de logs deve ser de no mínimo 90 a 180 dias.")
#                     parecer_detalhes.append(f"VIOLAÇÃO: Retenção configurada ({retencao_logs} dias) está abaixo do mínimo regulamentar.")
#                 else:
#                     parecer_detalhes.append(f"CONFORME: Retenção de logs configurada para {retencao_logs} dias.")

#                 status_final = "REPROVADO / EM INCONFORMIDADE" if inconformidades else "APROVADO / EM CONFORMIDADE"

#                 # Gravação no Banco de Dados
#                 conn = sqlite3.connect("cats_sesp.db")
#                 c = conn.cursor()
#                 c.execute('''
#                     INSERT INTO auditoria_posic 
#                     (projeto_id, uso_ia_pessoal, prompts_sensiveis_externos, ripd_aprovado, mfa_ativo, retencao_logs_dias, camara_tecnica_designada, status_conformidade, data_auditoria)
#                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#                 ''', (selected_proj_id, ia_pessoal, prompts_sensiveis, ripd_ok, mfa_ok, retencao_logs, camara, status_final, datetime.now().strftime("%Y-%m-%d %H:%M")))
#                 conn.commit()
#                 conn.close()

#                 # Exibição e Download do Parecer Oficial em PDF
#                 if inconformidades:
#                     st.error(f"Status: {status_final}")
#                     for inc in inconformidades:
#                         st.write(f"- {inc}")
#                 else:
#                     st.success(f"Status: {status_final}")

#                 pdf_buffer = gerar_pdf_parecer_tecnico(
#                     selected_proj_name, proc_val, inst_val, status_final, camara, parecer_detalhes
#                 )

#                 st.download_button(
#                     label="Descarregar Parecer Técnico Oficial (PDF Assinado com SHA-256)",
#                     data=pdf_buffer,
#                     file_name=f"Parecer_CATS_{selected_proj_id}.pdf",
#                     mime="application/pdf"
#                 )


# # -----------------------------------------------------------------------------
# # MÓDULO 6: VARREDURA DE SIGILO EM PDFS (RAG/IA)
# # -----------------------------------------------------------------------------

# elif menu == "Varredura de Sigilo em PDFs (RAG/IA)":
#     st.title("Análise Preditiva de Sigilo e DLP em Documentos PDF")
#     st.caption("Conforme Termo de Publicação Científica e diretrizes de Prevenção de Vazamento de Dados (DLP).")

#     uploaded_file = st.file_uploader("Submeta o Artigo, Tese ou Relatório Técnico em formato PDF para verificação:", type=["pdf"])

#     if uploaded_file is not None:
#         try:
#             reader = pypdf.PdfReader(uploaded_file)
#             texto_completo = ""
#             for page in reader.pages:
#                 texto_completo += page.extract_text() or ""

#             st.info(f"Ficheiro lido com sucesso! Total de páginas extraídas: {len(reader.pages)}")

#             with st.spinner("A executar a varredura DLP e análise de termos sigilosos..."):
#                 termos_sensiveis = [
#                     "inquérito policial", "dado pessoal", "CPF", "biometria", 
#                     "operação policial", "segredo de justiça", "vulnerabilidade", 
#                     "ip público", "senha", "hash de senha", "investigado"
#                 ]
                
#                 alertas = []
#                 texto_lower = texto_completo.lower()

#                 for termo in termos_sensiveis:
#                     if termo in texto_lower:
#                         ocorrencias = texto_lower.count(termo)
#                         alertas.append(f"Termo sensível detectado: **'{termo}'** ({ocorrencias} ocorrências no texto).")

#             st.subheader("Resultado do Rastreador de Vazamentos (DLP):")
#             if alertas:
#                 st.warning("Foram identificados potenciais riscos à segurança da informação ou privacidade:")
#                 for al in alertas:
#                     st.write(f"- {al}")
#                 st.error("Recomendação: Submeter o material para revisão prévia da SESP/PR conforme o Capítulo X da Resolução antes da publicação.")
#             else:
#                 st.success("Nenhuma violação óbvia de sigilo ou termo sensível de DLP foi detectada no documento.")

#             with st.expander("Visualizar Texto Extraído para Auditoria Manual"):
#                 st.text_area("Conteúdo do PDF:", texto_completo, height=250)

#         except Exception as e:
#             st.error(f"Erro ao processar o ficheiro PDF: {e}")


# # -----------------------------------------------------------------------------
# # MÓDULO 7: PAINEL DE AUDITORIA E RELATÓRIOS CONSOLIDADOS
# # -----------------------------------------------------------------------------

# elif menu == "Painel de Auditoria e Relatórios":
#     st.title(" Painel Executivo de Auditoria e Conformidade Geral")
#     st.caption("Visão consolidada para Fiscais Técnicos, Segurança da Informação (CTIC/DFIR) e Câmaras Técnicas Estaduais.")

#     query_audit = '''
#         SELECT 
#             p.nome AS Projeto,
#             p.institucion AS Executora,
#             COUNT(DISTINCT m.id) AS Ativos_Mapeados,
#             COUNT(DISTINCT ia.id) AS Modelos_IA,
#             COALESCE(e.status_encerramento, 'Em Execução / Não Encerrado') AS Status_Encerramento,
#             COALESCE(pos.status_conformidade, 'Não Auditado') AS Compliance_PoSIC
#         FROM projetos p
#         LEFT JOIN matriz_titularidade m ON p.id = m.projeto_id
#         LEFT JOIN inventario_ia ia ON p.id = ia.projeto_id
#         LEFT JOIN encerramento_aceite e ON p.id = e.projeto_id
#         LEFT JOIN auditoria_posic pos ON p.id = pos.projeto_id
#         GROUP BY p.id
#     '''
    
#     conn = sqlite3.connect("cats_sesp.db")
#     df_audit = pd.read_sql_query(query_audit, conn)
#     conn.close()

#     st.dataframe(df_audit, use_container_width=True)

#     st.markdown("---")
#     st.subheader("Exportar Relatórios de Auditoria")
    
#     conn = sqlite3.connect("cats_sesp.db")
#     df_full = pd.read_sql_query("SELECT * FROM projetos", conn)
#     conn.close()

#     st.download_button(
#         label=" Baixar Base Completa de Projetos (JSON)",
#         data=df_full.to_json(orient="records"),
#         file_name="cats_sesp_export.json",
#         mime="application/json"
#     )

import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import io
from datetime import datetime

# Importações para geração de PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Importação para extração e leitura de PDFs submetidos
import pypdf

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CATS-SESP - Governança, Segurança e Ativos Tecnológicos",
    page_icon="",
    layout="wide"
)

# -----------------------------------------------------------------------------
# INICIALIZAÇÃO DO BANCO DE DADOS (SQLite)
# -----------------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect("cats_sesp.db")
    c = conn.cursor()
    
    # Tabela: Projetos
    c.execute('''
        CREATE TABLE IF NOT EXISTS projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            processo TEXT,
            institucion TEXT,
            responsavel_tecnico TEXT,
            data_inicio TEXT
        )
    ''')
    
    # Tabela: Matriz de Titularidade 
    c.execute('''
        CREATE TABLE IF NOT EXISTS matriz_titularidade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER,
            nome_ativo TEXT,
            categoria TEXT,
            titular_sesp BOOLEAN,
            titular_instituicao BOOLEAN,
            direito_exploracao BOOLEAN,
            direito_transferencia BOOLEAN,
            FOREIGN KEY (projeto_id) REFERENCES projetos (id)
        )
    ''')

    # Tabela: Inventário de IA
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventario_ia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER,
            modelo_nome TEXT,
            modelo_base TEXT,
            licenca TEXT,
            fine_tuning BOOLEAN,
            metodo_ft TEXT,
            acuracia REAL,
            f1_score REAL,
            FOREIGN KEY (projeto_id) REFERENCES projetos (id)
        )
    ''')

    # Tabela: Checklists de Encerramento e Aceite
    c.execute('''
        CREATE TABLE IF NOT EXISTS encerramento_aceite (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER,
            codigo_fonte_entregue BOOLEAN,
            repositorio_git BOOLEAN,
            pesos_ia_entregues BOOLEAN,
            dados_devolvidos_eliminados BOOLEAN,
            vendor_lockin_identificado BOOLEAN,
            status_encerramento TEXT,
            data_registro TEXT,
            FOREIGN KEY (projeto_id) REFERENCES projetos (id)
        )
    ''')

    # Tabela: Auditoria de Conformidade PoSIC e CGD-SI (NSIC-05)
    c.execute('''
        CREATE TABLE IF NOT EXISTS auditoria_posic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER,
            uso_ia_pessoal BOOLEAN,
            prompts_sensiveis_externos BOOLEAN,
            ripd_aprovado BOOLEAN,
            mfa_ativo BOOLEAN,
            retencao_logs_dias INTEGER,
            camara_tecnica_designada TEXT,
            status_conformidade TEXT,
            data_auditoria TEXT,
            FOREIGN KEY (projeto_id) REFERENCES projetos (id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

def run_query(query, params=()):
    conn = sqlite3.connect("cats_sesp.db")
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

# -----------------------------------------------------------------------------
#  MOTOR DE GERAÇÃO DE PDFS FORMAIS COM HASH SHA-256
# -----------------------------------------------------------------------------
def gerar_pdf_parecer_tecnico(projeto_nome, processo, instituicao, status_audit, camara, parecer_detalhes):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontSize=14, textColor=colors.HexColor("#002B49"), alignment=1, spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor("#555555"), alignment=1, spaceAfter=20
    )
    normal_style = styles['Normal']
    bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontName='Helvetica-Bold')

    # Cabeçalho
    story.append(Paragraph("ESTADO DO PARANÁ - SECRETARIA DA SEGURANÇA PÚBLICA", title_style))
    story.append(Paragraph("SISTEMA CATS-SESP | PARECER TÉCNICO DE GOVERNANÇA E AUDITORIA", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#002B49"), spaceAfter=15))
    
    # Dados do Projeto
    data_emissao = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    story.append(Paragraph(f"<b>Projeto Auditado:</b> {projeto_nome}", normal_style))
    story.append(Paragraph(f"<b>Processo Administrativo:</b> {processo}", normal_style))
    story.append(Paragraph(f"<b>Instituição Executora:</b> {instituicao}", normal_style))
    story.append(Paragraph(f"<b>Data da Auditoria:</b> {data_emissao}", normal_style))
    story.append(Paragraph(f"<b>Câmara Técnica Designada:</b> {camara}", normal_style))
    story.append(Spacer(1, 15))
    
    # Resultado da Avaliação
    color_status = colors.green if "APROVADO" in status_audit else colors.red
    story.append(Paragraph(f"<b>STATUS DA AUDITORIA:</b> <font color='{color_status.hexval()}'>{status_audit}</font>", normal_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Detalhamento da Análise de Compliance e Segurança:</b>", bold_style))
    story.append(Spacer(1, 5))
    
    for item in parecer_detalhes:
        story.append(Paragraph(f"• {item}", normal_style))
        story.append(Spacer(1, 3))
        
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=15))
    
    # Cálculo de Assinatura e Integridade Hash SHA-256
    conteudo_para_hash = f"{projeto_nome}-{processo}-{status_audit}-{data_emissao}".encode('utf-8')
    hash_documento = hashlib.sha256(conteudo_para_hash).hexdigest().upper()
    
    story.append(Paragraph("<b>Código de Validação e Autenticidade (SHA-256):</b>", bold_style))
    story.append(Paragraph(f"<font fontName='Courier' size=8>{hash_documento}</font>", normal_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<i>Documento gerado automaticamente pelo Sistema CATS-SESP conforme Resolução SESP/PR 2026, PoSIC v2.0 e Deliberação CGD-SI nº 5/2025.</i>", ParagraphStyle('Foot', parent=normal_style, fontSize=8, textColor=colors.gray)))

    doc.build(story)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# NAVEGAÇÃO DA APLICAÇÃO (SIDEBAR)
# -----------------------------------------------------------------------------
st.sidebar.title("CATS - SESP/PR")
st.sidebar.caption("Cadastro de Ativos Tecnológicos e Governança")

menu = st.sidebar.radio(
    "Selecione o Módulo:",
    [
        "Gestão de Projetos",
        "Matriz de Titularidade",
        "Inventário de IA",
        "Checklist de Aceite",
        "Auditoria PoSIC & CGD-SI (NSIC-05)",
        "Varredura de Sigilo em PDFs (RAG/IA)",
        "Painel de Auditoria e Relatórios"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "Sistema em conformidade com:\n"
    "- Resolução SESP/PR 2026\n"
    "- PoSIC SESP-PR v2.0 (NSIC-01 a 11)\n"
    "- Deliberação CGD-SI nº 5/2025\n"
    "- Guia de PDTIC do SISP v2.1"
)

# -----------------------------------------------------------------------------
# MÓDULO 1: GESTÃO DE PROJETOS (COM EDIÇÃO E EXCLUSÃO)
# -----------------------------------------------------------------------------
if menu == "Gestão de Projetos":
    st.title(" Cadastro e Gestão de Projetos de Inovação / TI")
    st.caption("Cadastre, edite ou remova projetos para vincular ativos tecnológicos, modelos de IA e auditorias.")

    # Form de Cadastro
    with st.expander(" Cadastrar Novo Projeto", expanded=False):
        with st.form("form_novo_projeto"):
            col1, col2 = st.columns(2)
            nome_p = col1.text_input("Nome do Projeto *")
            proc_p = col2.text_input("Número do Processo Administrativo")
            inst_p = col1.text_input("Instituição Executora (ex: UFPR, ICT, Empresa)")
            resp_p = col2.text_input("Responsável Técnico")
            data_p = st.date_input("Data de Início", datetime.now())

            btn_salvar_proj = st.form_submit_button("Cadastrar Projeto")
            if btn_salvar_proj:
                if nome_p:
                    run_query(
                        "INSERT INTO projetos (nome, processo, institucion, responsavel_tecnico, data_inicio) VALUES (?, ?, ?, ?, ?)",
                        (nome_p, proc_p, inst_p, resp_p, str(data_p))
                    )
                    st.success(f"Projeto '{nome_p}' cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("O nome do projeto é obrigatório.")

    # Edição / Exclusão de Projetos
    conn = sqlite3.connect("cats_sesp.db")
    df_proj_edit = pd.read_sql_query("SELECT id, nome, processo, institucion, responsavel_tecnico, data_inicio FROM projetos", conn)
    conn.close()

    if not df_proj_edit.empty:
        with st.expander("Editar ou Excluir Projeto Existente", expanded=False):
            proj_dict = dict(zip(df_proj_edit['nome'], df_proj_edit['id']))
            selected_edit_name = st.selectbox("Selecione o Projeto para alterar/remover:", list(proj_dict.keys()))
            selected_edit_id = proj_dict[selected_edit_name]

            # Obter dados atuais do projeto selecionado
            proj_data = df_proj_edit[df_proj_edit['id'] == selected_edit_id].iloc[0]

            col_ed1, col_ed2 = st.columns(2)
            with st.form("form_edit_proj"):
                e_nome = col_ed1.text_input("Nome do Projeto", value=proj_data['nome'])
                e_proc = col_ed2.text_input("Número do Processo", value=proj_data['processo'])
                e_inst = col_ed1.text_input("Instituição Executora", value=proj_data['institucion'])
                e_resp = col_ed2.text_input("Responsável Técnico", value=proj_data['responsavel_tecnico'])

                btn_atualizar = st.form_submit_button("Atualizar Dados do Projeto")
                if btn_atualizar:
                    run_query(
                        "UPDATE projetos SET nome=?, processo=?, institucion=?, responsavel_tecnico=? WHERE id=?",
                        (e_nome, e_proc, e_inst, e_resp, selected_edit_id)
                    )
                    st.success(f"Projeto '{e_nome}' atualizado com sucesso!")
                    st.rerun()

            if st.button(f"❌ Excluir Definitivamente o Projeto '{selected_edit_name}'", type="primary"):
                run_query("DELETE FROM projetos WHERE id=?", (selected_edit_id,))
                run_query("DELETE FROM matriz_titularidade WHERE projeto_id=?", (selected_edit_id,))
                run_query("DELETE FROM inventario_ia WHERE projeto_id=?", (selected_edit_id,))
                run_query("DELETE FROM encerramento_aceite WHERE projeto_id=?", (selected_edit_id,))
                run_query("DELETE FROM auditoria_posic WHERE projeto_id=?", (selected_edit_id,))
                st.warning(f"Projeto '{selected_edit_name}' e todos os seus registros vinculados foram apagados!")
                st.rerun()

    st.subheader("Projetos Cadastrados no CATS-SESP")
    conn = sqlite3.connect("cats_sesp.db")
    df_proj = pd.read_sql_query("SELECT id AS ID, nome AS Projeto, processo AS Processo, institucion AS Instituicao, responsavel_tecnico AS Responsavel, data_inicio AS Inicio FROM projetos", conn)
    conn.close()
    st.dataframe(df_proj, use_container_width=True)

# -----------------------------------------------------------------------------
# MÓDULO 2: MATRIZ DE TITULARIDADE
# -----------------------------------------------------------------------------
elif menu == "Matriz de Titularidade":
    st.title("Matriz de Titularidade, Direitos de Uso e Exploração")
    st.caption("Classificação dos ativos do projeto conforme diretrizes da Resolução SESP/PR.")

    conn = sqlite3.connect("cats_sesp.db")
    df_proj = pd.read_sql_query("SELECT id, nome FROM projetos", conn)
    conn.close()

    if df_proj.empty:
        st.warning("Nenhum projeto cadastrado. Cadastre um projeto primeiro no Módulo 'Gestão de Projetos'.")
    else:
        proj_dict = dict(zip(df_proj['nome'], df_proj['id']))
        selected_proj_name = st.selectbox("Selecione o Projeto:", list(proj_dict.keys()))
        selected_proj_id = proj_dict[selected_proj_name]

        with st.form("form_matriz"):
            st.subheader("1. Classificação do Ativo Tecnológico")
            col1, col2 = st.columns(2)
            nome_ativo = col1.text_input("Nome do Ativo (ex: Módulo de Visão, Algoritmo de Busca, Base Consolidada)")
            categoria = col2.selectbox(
                "Categoria do Ativo:",
                [
                    "A - Background IP SESP/PR (Preexistente da SESP)",
                    "B - Background IP Executora (Preexistente da Universidade/Empresa)",
                    "C - Tecnologia de Terceiros (Open Source ou Proprietária)",
                    "D - Foreground IP (Criado especificamente no projeto)",
                    "E - Resultado Derivado (Modificação, fine-tuning, combinação)"
                ]
            )

            st.subheader("2. Definição de Direitos Patrimoniais e Operacionais")
            c1, c2, c3, c4 = st.columns(4)
            tit_sesp = c1.checkbox("Titularidade SESP/PR")
            tit_inst = c2.checkbox("Titularidade Instituição Executora")
            dir_exp = c3.checkbox("Direito de Exploração Econômica")
            dir_transf = c4.checkbox("Direito de Transferência a Terceiros")

            st.subheader("3. Direitos Assegurados à SESP/PR")
            m1, m2, m3, m4 = st.columns(4)
            m1.checkbox("Licença Perpétua e Irrevogável", value=True)
            m2.checkbox("Direito de Modificação/Adaptação", value=True)
            m3.checkbox("Direito de Manutenção por Terceiros", value=True)
            m4.checkbox("Direito de Auditoria", value=True)

            btn_salvar_matriz = st.form_submit_button("Registrar Ativo na Matriz")
            if btn_salvar_matriz:
                run_query(
                    '''INSERT INTO matriz_titularidade 
                       (projeto_id, nome_ativo, categoria, titular_sesp, titular_instituicao, direito_exploracao, direito_transferencia)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (selected_proj_id, nome_ativo, categoria[0], tit_sesp, tit_inst, dir_exp, dir_transf)
                )
                st.success(f"Ativo '{nome_ativo}' vinculado ao projeto e gravado com sucesso!")

        st.subheader(f"Matriz de Ativos do Projeto: {selected_proj_name}")
        conn = sqlite3.connect("cats_sesp.db")
        df_matriz = pd.read_sql_query(
            f"SELECT nome_ativo AS Ativo, categoria AS Cat, titular_sesp AS 'SESP Titular', titular_instituicao AS 'Inst. Titular', direito_exploracao AS Exploracao, direito_transferencia AS Transferencia FROM matriz_titularidade WHERE projeto_id = {selected_proj_id}",
            conn
        )
        conn.close()
        st.dataframe(df_matriz, use_container_width=True)

# -----------------------------------------------------------------------------
# MÓDULO 3: INVENTÁRIO DE IA 
# -----------------------------------------------------------------------------
elif menu == "Inventário de IA":
    st.title("Inventário de Inteligência Artificial e Modelos Derivados")
    st.caption("Conforme diretrizes da Resolução SESP/PR e NSIC-05.")

    conn = sqlite3.connect("cats_sesp.db")
    df_proj = pd.read_sql_query("SELECT id, nome FROM projetos", conn)
    conn.close()

    if df_proj.empty:
        st.warning("Cadastre um projeto antes de inventariar um modelo de IA.")
    else:
        proj_dict = dict(zip(df_proj['nome'], df_proj['id']))
        selected_proj_name = st.selectbox("Selecione o Projeto:", list(proj_dict.keys()), key="ia_proj")
        selected_proj_id = proj_dict[selected_proj_name]

        with st.form("form_ia_detalhado"):
            c1, c2, c3 = st.columns(3)
            modelo_nome = c1.text_input("Nome Interno do Modelo Resultante")
            modelo_base = c2.text_input("Modelo-Base Utilizado (ex: Llama-3-8B, YOLOv8)")
            licenca = c3.text_input("Licença (ex: Apache 2.0, MIT, Llama License)")

            fez_ft = st.radio("Foi realizado Fine-Tuning / Ajuste Fino?", ["Não", "Sim"])
            metodo_ft = st.multiselect("Métodos Empregados:", ["Full Fine-Tuning", "LoRA", "QLoRA", "Adapter", "Transfer Learning"]) if fez_ft == "Sim" else []

            st.write("**Métricas de Avaliação de Desempenho:**")
            m1, m2 = st.columns(2)
            acuracia = m1.number_input("Acurácia (0.0 a 1.0)", 0.0, 1.0, 0.90)
            f1 = m2.number_input("F1-Score (0.0 a 1.0)", 0.0, 1.0, 0.88)

            btn_ia = st.form_submit_button("Gravar Modelo no Inventário")
            if btn_ia:
                run_query(
                    '''INSERT INTO inventario_ia (projeto_id, modelo_nome, modelo_base, licenca, fine_tuning, metodo_ft, acuracia, f1_score)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (selected_proj_id, modelo_nome, modelo_base, licenca, (fez_ft == "Sim"), ", ".join(metodo_ft), acuracia, f1)
                )
                st.success("Modelo registrado no inventário do CATS-SESP!")

        st.subheader(f"Modelos Inventariados no Projeto: {selected_proj_name}")
        conn = sqlite3.connect("cats_sesp.db")
        df_ia = pd.read_sql_query(
            f"SELECT modelo_nome AS Modelo, modelo_base AS 'Modelo Base', licenca AS Licenca, fine_tuning AS 'Fine-Tuning', metodo_ft AS Metodo, acuracia AS Acuracia, f1_score AS 'F1-Score' FROM inventario_ia WHERE projeto_id = {selected_proj_id}",
            conn
        )
        conn.close()
        st.dataframe(df_ia, use_container_width=True)

# -----------------------------------------------------------------------------
# MÓDULO 4: CHECKLIST DE ACEITE E ENCERRAMENTO 
# -----------------------------------------------------------------------------
elif menu == "Checklist de Aceite":
    st.title("Checklist de Recebimento, Aceite e Desmobilização Tecnológica")
    st.caption("Verificação técnica obrigatória para emissão de Termo de Aceite Definitivo e liberação financeira.")

    conn = sqlite3.connect("cats_sesp.db")
    df_proj = pd.read_sql_query("SELECT id, nome FROM projetos", conn)
    conn.close()

    if df_proj.empty:
        st.warning("Nenhum projeto cadastrado.")
    else:
        proj_dict = dict(zip(df_proj['nome'], df_proj['id']))
        selected_proj_name = st.selectbox("Selecione o Projeto para Encerramento:", list(proj_dict.keys()), key="enc_proj")
        selected_proj_id = proj_dict[selected_proj_name]

        with st.form("form_aceite"):
            st.subheader("1. Entregáveis de Software e Código-Fonte")
            c1, c2, c3 = st.columns(3)
            cod_entregue = c1.checkbox("Código-fonte integral disponibilizado (sem ofuscação)")
            repo_git = c2.checkbox("Repositório Git com histórico e branches entregue")
            doc_api = c3.checkbox("APIs e Arquitetura documentadas")

            st.subheader("2. Entregáveis de Inteligência Artificial e Dados")
            i1, i2, i3 = st.columns(3)
            pesos_entregues = i1.checkbox("Pesos/Checkpoints do Modelo entregues")
            dados_tratados = i2.checkbox("Dados da SESP devolvidos/eliminados (com declaração)")
            ambientes_limpos = i3.checkbox("Ambientes temporários de teste eliminados")

            st.subheader("3. Prevenção ao Vendor Lock-In e Continuidade Operacional")
            v1, v2 = st.columns(2)
            vendor_lockin = v1.radio("Risco de Vendor Lock-in Identificado?", ["Não", "Sim"])
            capacitacao = v2.checkbox("Treinamento e Capacitação da equipe SESP realizados")

            st.subheader("4. Parecer Final do Encerramento")
            status_final = st.selectbox(
                "Conclusão da Fiscalização Técnica:",
                [
                    "ENCERRAMENTO APROVADO (Aceite Definitivo)",
                    "ENCERRAMENTO APROVADO COM RESSALVAS (Pendências não críticas)",
                    "ENCERRAMENTO NÃO APROVADO (Pendências críticas de código/dados/modelos)"
                ]
            )

            btn_encerramento = st.form_submit_button("Registrar Termo de Aceite / Encerramento")
            if btn_encerramento:
                run_query(
                    '''INSERT INTO encerramento_aceite 
                       (projeto_id, codigo_fonte_entregue, repositorio_git, pesos_ia_entregues, dados_devolvidos_eliminados, vendor_lockin_identificado, status_encerramento, data_registro)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (selected_proj_id, cod_entregue, repo_git, pesos_entregues, dados_tratados, (vendor_lockin == "Sim"), status_final, str(datetime.now().strftime("%Y-%m-%d %H:%M")))
                )
                if "NÃO APROVADO" in status_final:
                    st.error("Encerramento NÃO APROVADO retido até sanar as pendências apontadas.")
                else:
                    st.success("Termo de Aceite registrado com sucesso!")

# -----------------------------------------------------------------------------
# MÓDULO 5: AUDITORIA POSIC & CGD-SI (NSIC-05) + GERAÇÃO DE PDF
# -----------------------------------------------------------------------------
elif menu == "Auditoria":
    st.title(" Auditoria de Conformidade")
    st.caption("Verificação automatizada de conformidade.")

    conn = sqlite3.connect("cats_sesp.db")
    df_proj = pd.read_sql_query("SELECT id, nome, processo, institucion FROM projetos", conn)
    conn.close()

    if df_proj.empty:
        st.warning("Cadastre um projeto no Módulo 'Gestão de Projetos' para realizar a auditoria.")
    else:
        proj_dict = {row['nome']: (row['id'], row['processo'], row['institucion']) for _, row in df_proj.iterrows()}
        selected_proj_name = st.selectbox("Selecione o Projeto para Auditagem:", list(proj_dict.keys()), key="audit_posic")
        selected_proj_id, proc_val, inst_val = proj_dict[selected_proj_name]

        with st.form("form_auditoria_posic"):
            st.subheader("1. Verificação de Regras para Inteligência Artificial (NSIC-05)")
            ia_pessoal = st.checkbox("Utiliza ferramentas de IA através de contas pessoais/gratuitas (ex: ChatGPT/Gemini pessoal)?")
            prompts_sensiveis = st.checkbox("Alimenta modelos externos de IA com dados pessoais, inquéritos ou detalhes operacionais?")
            ripd_ok = st.checkbox("Possui Relatório de Impacto à Proteção de Dados (RIPD) aprovado pelo Controlador?")

            st.subheader("2. Verificação de Segurança da Informação")
            mfa_ok = st.checkbox("Autenticação Multifator (MFA/2FA) ativada para acessos externos e administrativos?")
            retencao_logs = st.number_input("Prazo configurado de retenção de logs de acesso (em dias):", min_value=0, max_value=365, value=180)

            st.subheader("3. Roteamento de Governança Estadual")
            camara = st.selectbox(
                "Câmara Técnica Responsável para Parecer:",
                [
                    "CT-IA (Inteligência Artificial)",
                    "CT-SID (Segurança da Informação e Dados)",
                    "CT-GOA (Gestão Orçamentária e Aquisições)",
                    "CT-GSTIC (Gestão de Serviços de TIC)",
                    "CT-NDGD (Normas de Governança Digital)",
                    "CT-IPE (Integração e Planejamento Estratégico)"
                ]
            )

            btn_auditar = st.form_submit_button("Executar Diagnóstico e Gerar Parecer")

            if btn_auditar:
                inconformidades = []
                parecer_detalhes = []
                
                if ia_pessoal:
                    inconformidades.append("NSIC-05 Art. 4: É VEDADO o uso de IA via contas pessoais ou gratuitas.")
                    parecer_detalhes.append("VIOLAÇÃO: Identificado uso de contas de IA não homologadas pela CTIC.")
                else:
                    parecer_detalhes.append("CONFORME: Ausência de uso de ferramentas de IA não corporativas.")

                if prompts_sensiveis:
                    inconformidades.append("NSIC-05 Art. 4: Proibido o fornecimento de prompts com dados sensíveis/policiais a IAs externas.")
                    parecer_detalhes.append("VIOLAÇÃO: Risco de exfiltração de dados sensíveis em prompts de IA externa.")
                else:
                    parecer_detalhes.append("CONFORME: Nenhum dado sensível é transmitido para modelos externos.")

                if not ripd_ok:
                    inconformidades.append("NSIC-05 Item IV: Projetos de IA exigem RIPD aprovado pelo Controlador.")
                    parecer_detalhes.append("PENDÊNCIA: Falta a apresentação de Relatório de Impacto à Proteção de Dados.")
                else:
                    parecer_detalhes.append("CONFORME: RIPD devidamente aprovado pelo Controlador.")

                if not mfa_ok:
                    inconformidades.append("NSIC-02 / NSIC-10: MFA é obrigatório para VPN e acessos sensíveis.")
                    parecer_detalhes.append("PENDÊNCIA: Autenticação Multifator não está ativada nas credenciais críticas.")
                else:
                    parecer_detalhes.append("CONFORME: Autenticação de Múltiplos Fatores habilitada.")

                if retencao_logs < 90:
                    inconformidades.append("NSIC-03 / NSIC-08: A retenção de logs deve ser de no mínimo 90 a 180 dias.")
                    parecer_detalhes.append(f"VIOLAÇÃO: Retenção configurada ({retencao_logs} dias) está abaixo do mínimo regulamentar.")
                else:
                    parecer_detalhes.append(f"CONFORME: Retenção de logs configurada para {retencao_logs} dias.")

                status_final = "REPROVADO / EM INCONFORMIDADE" if inconformidades else "APROVADO / EM CONFORMIDADE"

                # Gravação no Banco de Dados
                conn = sqlite3.connect("cats_sesp.db")
                c = conn.cursor()
                c.execute('''
                    INSERT INTO auditoria_posic 
                    (projeto_id, uso_ia_pessoal, prompts_sensiveis_externos, ripd_aprovado, mfa_ativo, retencao_logs_dias, camara_tecnica_designada, status_conformidade, data_auditoria)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (selected_proj_id, ia_pessoal, prompts_sensiveis, ripd_ok, mfa_ok, retencao_logs, camara, status_final, datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                conn.close()

                # Exibição e Download do Parecer Oficial em PDF
                if inconformidades:
                    st.error(f"Status: {status_final}")
                    for inc in inconformidades:
                        st.write(f"- {inc}")
                else:
                    st.success(f"Status: {status_final}")

                pdf_buffer = gerar_pdf_parecer_tecnico(
                    selected_proj_name, proc_val, inst_val, status_final, camara, parecer_detalhes
                )

                st.download_button(
                    label="Descarregar Parecer Técnico Oficial",
                    data=pdf_buffer,
                    file_name=f"Parecer_CATS_{selected_proj_id}.pdf",
                    mime="application/pdf"
                )

# -----------------------------------------------------------------------------
# MÓDULO 6: VARREDURA DE SIGILO EM PDFS (RAG/IA)
# -----------------------------------------------------------------------------
elif menu == "Varredura de Sigilo em PDFs":
    st.title(" Análise Preditiva de Sigilo e DLP em Documentos PDF")
    st.caption("Conforme Termo de Publicação Científica e diretrizes de Prevenção de Vazamento de Dados (DLP).")

    uploaded_file = st.file_uploader("Submeta o Artigo, Tese ou Relatório Técnico em formato PDF para verificação:", type=["pdf"])

    if uploaded_file is not None:
        try:
            reader = pypdf.PdfReader(uploaded_file)
            texto_completo = ""
            for page in reader.pages:
                texto_completo += page.extract_text() or ""

            st.info(f"Ficheiro lido com sucesso! Total de páginas extraídas: {len(reader.pages)}")

            with st.spinner("A executar a varredura DLP e análise de termos sigilosos..."):
                termos_sensiveis = [
                    "inquérito policial", "dado pessoal", "CPF", "biometria", 
                    "operação policial", "segredo de justiça", "vulnerabilidade", 
                    "ip público", "senha", "hash de senha", "investigado"
                ]
                
                alertas = []
                texto_lower = texto_completo.lower()

                for termo in termos_sensiveis:
                    if termo in texto_lower:
                        ocorrencias = texto_lower.count(termo)
                        alertas.append(f"Termo sensível detectado: **'{termo}'** ({ocorrencias} ocorrências no texto).")

            st.subheader("Resultado do Rastreador de Vazamentos (DLP):")
            if alertas:
                st.warning(" Foram identificados potenciais riscos à segurança da informação ou privacidade:")
                for al in alertas:
                    st.write(f"- {al}")
                st.error("Recomendação: Submeter o material para revisão prévia da SESP/PR conforme o Capítulo X da Resolução antes da publicação.")
            else:
                st.success(" Nenhuma violação óbvia de sigilo ou termo sensível de DLP foi detectada no documento.")

            with st.expander("Visualizar Texto Extraído para Auditoria Manual"):
                st.text_area("Conteúdo do PDF:", texto_completo, height=250)

        except Exception as e:
            st.error(f"Erro ao processar o ficheiro PDF: {e}")

# -----------------------------------------------------------------------------
# MÓDULO 7: PAINEL DE AUDITORIA E RELATÓRIOS CONSOLIDADOS
# -----------------------------------------------------------------------------
elif menu == "Painel de Auditoria e Relatórios":
    st.title("Painel Executivo de Auditoria e Conformidade Geral")
    st.caption("Visão consolidada para Fiscais Técnicos, Segurança da Informação (CTIC/DFIR) e Câmaras Técnicas Estaduais.")

    query_audit = '''
        SELECT 
            p.nome AS Projeto,
            p.institucion AS Executora,
            COUNT(DISTINCT m.id) AS Ativos_Mapeados,
            COUNT(DISTINCT ia.id) AS Modelos_IA,
            COALESCE(e.status_encerramento, 'Em Execução / Não Encerrado') AS Status_Encerramento,
            COALESCE(pos.status_conformidade, 'Não Auditado') AS Compliance_PoSIC
        FROM projetos p
        LEFT JOIN matriz_titularidade m ON p.id = m.projeto_id
        LEFT JOIN inventario_ia ia ON p.id = ia.projeto_id
        LEFT JOIN encerramento_aceite e ON p.id = e.projeto_id
        LEFT JOIN auditoria_posic pos ON p.id = pos.projeto_id
        GROUP BY p.id
    '''
    
    conn = sqlite3.connect("cats_sesp.db")
    df_audit = pd.read_sql_query(query_audit, conn)
    conn.close()

    st.dataframe(df_audit, use_container_width=True)

    st.markdown("---")
    st.subheader("Exportar Relatórios de Auditoria")
    
    conn = sqlite3.connect("cats_sesp.db")
    df_full = pd.read_sql_query("SELECT * FROM projetos", conn)
    conn.close()

    st.download_button(
        label="Baixar Base Completa de Projetos (JSON)",
        data=df_full.to_json(orient="records"),
        file_name="cats_sesp_export.json",
        mime="application/json"
    )