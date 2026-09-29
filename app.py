# import streamlit as st
# import sqlite3
# import pandas as pd
# import hashlib
# import io
# from datetime import datetime

# # Importações para geração de PDF
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib import colors

# # Importação para extração e leitura de PDFs submetidos
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
# # INICIALIZAÇÃO DO BANCO DE DADOS (SQLite)
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
# #  MOTOR DE GERAÇÃO DE PDFS FORMAIS COM HASH SHA-256
# # -----------------------------------------------------------------------------
# def gerar_pdf_parecer_tecnico(projeto_nome, processo, instituicao, status_audit, camara, parecer_detalhes):
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
#     story = []
    
#     styles = getSampleStyleSheet()
#     title_style = ParagraphStyle(
#         'TitleStyle', parent=styles['Heading1'], fontSize=14, textColor=colors.HexColor("#002B49"), alignment=1, spaceAfter=12
#     )
#     subtitle_style = ParagraphStyle(
#         'SubtitleStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor("#555555"), alignment=1, spaceAfter=20
#     )
#     normal_style = styles['Normal']
#     bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontName='Helvetica-Bold')

#     # Cabeçalho
#     story.append(Paragraph("ESTADO DO PARANÁ - SECRETARIA DA SEGURANÇA PÚBLICA", title_style))
#     story.append(Paragraph("SISTEMA CATS-SESP | PARECER TÉCNICO DE GOVERNANÇA E AUDITORIA", subtitle_style))
#     story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#002B49"), spaceAfter=15))
    
#     # Dados do Projeto
#     data_emissao = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
#     story.append(Paragraph(f"<b>Projeto Auditado:</b> {projeto_nome}", normal_style))
#     story.append(Paragraph(f"<b>Processo Administrativo:</b> {processo}", normal_style))
#     story.append(Paragraph(f"<b>Instituição Executora:</b> {instituicao}", normal_style))
#     story.append(Paragraph(f"<b>Data da Auditoria:</b> {data_emissao}", normal_style))
#     story.append(Paragraph(f"<b>Câmara Técnica Designada:</b> {camara}", normal_style))
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
# # st.sidebar.info(
# #     "Sistema em conformidade com:\n"
# #     "- Resolução SESP/PR 2026\n"
# #     "- PoSIC SESP-PR v2.0 (NSIC-01 a 11)\n"
# #     "- Deliberação CGD-SI nº 5/2025\n"
# #     "- Guia de PDTIC do SISP v2.1"
# # )

# # -----------------------------------------------------------------------------
# # MÓDULO 1: GESTÃO DE PROJETOS (COM EDIÇÃO E EXCLUSÃO)
# # -----------------------------------------------------------------------------
# if menu == "Gestão de Projetos":
#     st.title(" Cadastro e Gestão de Projetos de Inovação / TI")
#     st.caption("Cadastre, edite ou remova projetos para vincular ativos tecnológicos, modelos de IA e auditorias.")

#     # Form de Cadastro
#     with st.expander(" Cadastrar Novo Projeto", expanded=False):
#         with st.form("form_novo_projeto"):
#             col1, col2 = st.columns(2)
#             nome_p = col1.text_input("Nome do Projeto *")
#             proc_p = col2.text_input("Número do Processo Administrativo")
#             inst_p = col1.text_input("Instituição Executora (ex: UFPR, ICT, Empresa)")
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
#                     st.rerun()
#                 else:
#                     st.error("O nome do projeto é obrigatório.")

#     # Edição / Exclusão de Projetos
#     conn = sqlite3.connect("cats_sesp.db")
#     df_proj_edit = pd.read_sql_query("SELECT id, nome, processo, institucion, responsavel_tecnico, data_inicio FROM projetos", conn)
#     conn.close()

#     if not df_proj_edit.empty:
#         with st.expander("Editar ou Excluir Projeto Existente", expanded=False):
#             proj_dict = dict(zip(df_proj_edit['nome'], df_proj_edit['id']))
#             selected_edit_name = st.selectbox("Selecione o Projeto para alterar/remover:", list(proj_dict.keys()))
#             selected_edit_id = proj_dict[selected_edit_name]

#             # Obter dados atuais do projeto selecionado
#             proj_data = df_proj_edit[df_proj_edit['id'] == selected_edit_id].iloc[0]

#             col_ed1, col_ed2 = st.columns(2)
#             with st.form("form_edit_proj"):
#                 e_nome = col_ed1.text_input("Nome do Projeto", value=proj_data['nome'])
#                 e_proc = col_ed2.text_input("Número do Processo", value=proj_data['processo'])
#                 e_inst = col_ed1.text_input("Instituição Executora", value=proj_data['institucion'])
#                 e_resp = col_ed2.text_input("Responsável Técnico", value=proj_data['responsavel_tecnico'])

#                 btn_atualizar = st.form_submit_button("Atualizar Dados do Projeto")
#                 if btn_atualizar:
#                     run_query(
#                         "UPDATE projetos SET nome=?, processo=?, institucion=?, responsavel_tecnico=? WHERE id=?",
#                         (e_nome, e_proc, e_inst, e_resp, selected_edit_id)
#                     )
#                     st.success(f"Projeto '{e_nome}' atualizado com sucesso!")
#                     st.rerun()

#             if st.button(f"❌ Excluir Definitivamente o Projeto '{selected_edit_name}'", type="primary"):
#                 run_query("DELETE FROM projetos WHERE id=?", (selected_edit_id,))
#                 run_query("DELETE FROM matriz_titularidade WHERE projeto_id=?", (selected_edit_id,))
#                 run_query("DELETE FROM inventario_ia WHERE projeto_id=?", (selected_edit_id,))
#                 run_query("DELETE FROM encerramento_aceite WHERE projeto_id=?", (selected_edit_id,))
#                 run_query("DELETE FROM auditoria_posic WHERE projeto_id=?", (selected_edit_id,))
#                 st.warning(f"Projeto '{selected_edit_name}' e todos os seus registros vinculados foram apagados!")
#                 st.rerun()

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
# elif menu == "Auditoria":
#     st.title(" Auditoria de Conformidade")
#     st.caption("Verificação automatizada de conformidade.")

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

#             st.subheader("2. Verificação de Segurança da Informação")
#             mfa_ok = st.checkbox("Autenticação Multifator (MFA/2FA) ativada para acessos externos e administrativos?")
#             retencao_logs = st.number_input("Prazo configurado de retenção de logs de acesso (em dias):", min_value=0, max_value=365, value=180)

#             st.subheader("3. Roteamento de Governança Estadual")
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
#                     label="Descarregar Parecer Técnico Oficial",
#                     data=pdf_buffer,
#                     file_name=f"Parecer_CATS_{selected_proj_id}.pdf",
#                     mime="application/pdf"
#                 )

# # -----------------------------------------------------------------------------
# # MÓDULO 6: VARREDURA DE SIGILO EM PDFS (RAG/IA)
# # -----------------------------------------------------------------------------
# elif menu == "Varredura de Sigilo em PDFs":
#     st.title(" Análise Preditiva de Sigilo e DLP em Documentos PDF")
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
#                 st.warning(" Foram identificados potenciais riscos à segurança da informação ou privacidade:")
#                 for al in alertas:
#                     st.write(f"- {al}")
#                 st.error("Recomendação: Submeter o material para revisão prévia da SESP/PR conforme o Capítulo X da Resolução antes da publicação.")
#             else:
#                 st.success(" Nenhuma violação óbvia de sigilo ou termo sensível de DLP foi detectada no documento.")

#             with st.expander("Visualizar Texto Extraído para Auditoria Manual"):
#                 st.text_area("Conteúdo do PDF:", texto_completo, height=250)

#         except Exception as e:
#             st.error(f"Erro ao processar o ficheiro PDF: {e}")

# # -----------------------------------------------------------------------------
# # MÓDULO 7: PAINEL DE AUDITORIA E RELATÓRIOS CONSOLIDADOS
# # -----------------------------------------------------------------------------
# elif menu == "Painel de Auditoria e Relatórios":
#     st.title("Painel Executivo de Auditoria e Conformidade Geral")
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
#         label="Baixar Base Completa de Projetos (JSON)",
#         data=df_full.to_json(orient="records"),
#         file_name="cats_sesp_export.json",
#         mime="application/json"
#     )

    #================================ nova version =======

import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import io
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

import pypdf


# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================

st.set_page_config(
    page_title="CATS-SESP | Governança, Segurança e Ativos Tecnológicos",
    page_icon="️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# CSS — INTERFACE
# =============================================================================

st.markdown(
    """
    <style>
        /* ================================================================
           TEMA VISUAL CATS-SESP
           Paleta: azul institucional + branco + cinza neutro.
           Contraste alto para leitura consistente em todo o sistema.
           ================================================================ */

        :root {
            --cats-navy: #12304A;
            --cats-blue: #1769AA;
            --cats-blue-dark: #0F4F82;
            --cats-blue-soft: #EAF3FA;
            --cats-text: #1F2937;
            --cats-text-2: #4B5563;
            --cats-muted: #6B7280;
            --cats-border: #D7E0E8;
            --cats-bg: #F5F7FA;
            --cats-surface: #FFFFFF;
        }

        /* ---------- Base ---------- */
        .stApp {
            background: var(--cats-bg);
            color: var(--cats-text);
        }

        [data-testid="stHeader"] {
            background: rgba(245, 247, 250, 0.96);
        }

        .main .block-container {
            padding-top: 1.4rem;
            padding-bottom: 3rem;
            max-width: 1500px;
        }

        /* Texto geral do conteúdo principal */
        .main p,
        .main li,
        .main label,
        .main span,
        .main div {
            color: inherit;
        }

        .main .stMarkdown,
        .main [data-testid="stMarkdownContainer"] {
            color: var(--cats-text);
        }

        .main .stMarkdown p,
        .main [data-testid="stMarkdownContainer"] p {
            color: var(--cats-text);
        }

        /* ---------- Sidebar ---------- */
        section[data-testid="stSidebar"] {
            background: var(--cats-navy);
            border-right: 1px solid #0B2235;
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 1.2rem;
        }

        /* Texto da sidebar */
        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] div {
            color: #F4F8FC;
        }

        section[data-testid="stSidebar"] .stCaption,
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            color: #B9CAD8 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] label {
            color: #F4F8FC !important;
            padding: 0.68rem 0.75rem;
            margin: 0.18rem 0;
            border-radius: 9px;
            transition: background 0.18s ease, color 0.18s ease;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] label p,
        section[data-testid="stSidebar"] [data-testid="stRadio"] label span {
            color: #F4F8FC !important;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
            background: #1D4564;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] > div {
            gap: 0.15rem;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radio"][aria-checked="true"] {
            background: #245A80;
            border-radius: 9px;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radio"] div {
            color: #F4F8FC !important;
        }

        section[data-testid="stSidebar"] hr {
            border-color: #34546C;
        }

        /* ---------- Cabeçalho ---------- */
        .cats-header {
            background: var(--cats-navy);
            padding: 1.45rem 1.7rem;
            border-radius: 14px;
            margin-bottom: 1.35rem;
            box-shadow: 0 8px 24px rgba(18, 48, 74, 0.14);
            color: #FFFFFF;
        }

        .cats-header h1 {
            margin: 0;
            color: #FFFFFF !important;
            font-size: 1.75rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        .cats-header p {
            margin: 0.35rem 0 0;
            color: #D8E6F0 !important;
            font-size: 0.94rem;
        }

        /* ---------- Cards ---------- */
        .metric-card,
        .section-card {
            background: var(--cats-surface);
            border: 1px solid var(--cats-border);
            border-radius: 12px;
            box-shadow: 0 3px 12px rgba(18, 48, 74, 0.05);
        }

        .metric-card {
            padding: 1rem 1.1rem;
            min-height: 112px;
        }

        .metric-label {
            color: var(--cats-text-2) !important;
            font-size: 0.82rem;
            font-weight: 650;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .metric-value {
            color: var(--cats-navy) !important;
            font-size: 1.75rem;
            font-weight: 750;
            margin-top: 0.28rem;
        }

        .metric-sub {
            color: var(--cats-muted) !important;
            font-size: 0.78rem;
            margin-top: 0.2rem;
        }

        .section-card {
            padding: 1.2rem 1.3rem;
            margin: 0.6rem 0 1rem;
        }

        .section-title {
            color: var(--cats-navy) !important;
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.65rem;
        }

        /* ---------- Títulos e textos Streamlit ---------- */
        h1, h2, h3, h4, h5, h6 {
            color: var(--cats-navy) !important;
        }

        .main [data-testid="stHeadingWithActionElements"] h1,
        .main [data-testid="stHeadingWithActionElements"] h2,
        .main [data-testid="stHeadingWithActionElements"] h3,
        .main [data-testid="stHeadingWithActionElements"] h4 {
            color: var(--cats-navy) !important;
        }

        .stCaption,
        [data-testid="stCaptionContainer"] {
            color: var(--cats-muted) !important;
        }

        /* ---------- Labels dos widgets ---------- */
        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] label,
        [data-testid="stWidgetLabel"] span {
            color: var(--cats-text) !important;
        }

        /* ---------- Inputs / Selects / Textareas ---------- */
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        div[data-baseweb="textarea"] > div,
        textarea,
        input {
            background: #FFFFFF !important;
            color: var(--cats-text) !important;
            border-radius: 8px !important;
            border-color: var(--cats-border) !important;
        }

        input::placeholder,
        textarea::placeholder {
            color: #7B8794 !important;
            opacity: 1 !important;
        }

        div[data-baseweb="select"] *,
        div[data-baseweb="input"] *,
        div[data-baseweb="textarea"] * {
            color: var(--cats-text) !important;
        }

        /* Dropdown aberto */
        [role="listbox"],
        [role="option"] {
            background: #FFFFFF !important;
            color: var(--cats-text) !important;
        }

        [role="option"] * {
            color: var(--cats-text) !important;
        }

        [role="option"][aria-selected="true"] {
            background: var(--cats-blue-soft) !important;
        }

        /* ---------- Radio / Checkbox no conteúdo principal ---------- */
        .main [data-testid="stRadio"] label,
        .main [data-testid="stCheckbox"] label,
        .main [data-testid="stToggle"] label {
            color: var(--cats-text) !important;
        }

        .main [data-testid="stRadio"] label p,
        .main [data-testid="stCheckbox"] label p,
        .main [data-testid="stToggle"] label p {
            color: var(--cats-text) !important;
        }

        /* ---------- Botões ---------- */
        .stButton > button,
        .stDownloadButton > button,
        button[kind="primary"] {
            background: var(--cats-blue);
            color: #FFFFFF !important;
            border: 1px solid var(--cats-blue);
            border-radius: 8px;
            font-weight: 650;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover,
        button[kind="primary"]:hover {
            background: var(--cats-blue-dark);
            color: #FFFFFF !important;
            border-color: var(--cats-blue-dark);
            transform: translateY(-1px);
        }

        .stButton > button p,
        .stDownloadButton > button p,
        button[kind="primary"] p {
            color: #FFFFFF !important;
        }

        /* ---------- Tabs ---------- */
        .main [data-baseweb="tab-list"] {
            gap: 0.25rem;
        }

        .main [data-baseweb="tab"] {
            color: var(--cats-text-2) !important;
            font-weight: 600;
        }

        .main [data-baseweb="tab"] p,
        .main [data-baseweb="tab"] span {
            color: var(--cats-text-2) !important;
        }

        .main [aria-selected="true"][data-baseweb="tab"] {
            color: var(--cats-blue) !important;
        }

        .main [aria-selected="true"][data-baseweb="tab"] p,
        .main [aria-selected="true"][data-baseweb="tab"] span {
            color: var(--cats-blue) !important;
        }

        /* ---------- Dataframes / tabelas ---------- */
        [data-testid="stDataFrame"],
        [data-testid="stDataEditor"] {
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid var(--cats-border);
            background: #FFFFFF;
        }

        /* ---------- Alertas ---------- */
        .stAlert {
            border-radius: 9px;
        }

        /* ---------- Separadores ---------- */
        .main hr {
            border-color: var(--cats-border);
        }

        /* ---------- Rodapé ---------- */
        .cats-footer {
            text-align: center;
            color: var(--cats-muted) !important;
            font-size: 0.76rem;
            padding: 1.5rem 0 0.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# BANCO DE DADOS
# =============================================================================

DB_PATH = "cats_sesp.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            processo TEXT,
            institucion TEXT,
            responsavel_tecnico TEXT,
            data_inicio TEXT
        )
        """
    )

    c.execute(
        """
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
        """
    )

    c.execute(
        """
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
        """
    )

    c.execute(
        """
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
        """
    )

    c.execute(
        """
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
        """
    )

    conn.commit()
    conn.close()


init_db()


def run_query(query, params=()):
    conn = get_connection()
    try:
        conn.execute(query, params)
        conn.commit()
    finally:
        conn.close()


def read_query(query, params=()):
    conn = get_connection()
    try:
        return pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()


# =============================================================================
# FUNÇÕES DE INTERFACE
# =============================================================================

def render_header(title, subtitle):
    st.markdown(
        f"""
        <div class="cats-header">
            <h1>{escape(title)}</h1>
            <p>{escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value, subtitle=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{escape(str(label))}</div>
            <div class="metric-value">{escape(str(value))}</div>
            <div class="metric-sub">{escape(str(subtitle))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_projects():
    return read_query(
        """
        SELECT id, nome, processo, institucion, responsavel_tecnico, data_inicio
        FROM projetos
        ORDER BY nome
        """
    )


# =============================================================================
# GERAÇÃO DE PDF
# =============================================================================

def gerar_pdf_parecer_tecnico(
    projeto_nome,
    processo,
    instituicao,
    status_audit,
    camara,
    parecer_detalhes,
):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=14,
        textColor=colors.HexColor("#002B49"),
        alignment=1,
        spaceAfter=12,
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#555555"),
        alignment=1,
        spaceAfter=20,
    )

    normal_style = styles["Normal"]

    bold_style = ParagraphStyle(
        "BoldStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
    )

    footer_style = ParagraphStyle(
        "Foot",
        parent=normal_style,
        fontSize=8,
        textColor=colors.gray,
    )

    story.append(
        Paragraph(
            "ESTADO DO PARANÁ - SECRETARIA DA SEGURANÇA PÚBLICA",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "SISTEMA CATS-SESP | PARECER TÉCNICO DE GOVERNANÇA E AUDITORIA",
            subtitle_style,
        )
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1.5,
            color=colors.HexColor("#002B49"),
            spaceAfter=15,
        )
    )

    data_emissao = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")

    story.append(
        Paragraph(
            f"<b>Projeto Auditado:</b> {escape(str(projeto_nome))}",
            normal_style,
        )
    )
    story.append(
        Paragraph(
            f"<b>Processo Administrativo:</b> {escape(str(processo or 'Não informado'))}",
            normal_style,
        )
    )
    story.append(
        Paragraph(
            f"<b>Instituição Executora:</b> {escape(str(instituicao or 'Não informada'))}",
            normal_style,
        )
    )
    story.append(
        Paragraph(
            f"<b>Data da Auditoria:</b> {data_emissao}",
            normal_style,
        )
    )
    story.append(
        Paragraph(
            f"<b>Câmara Técnica Designada:</b> {escape(str(camara))}",
            normal_style,
        )
    )

    story.append(Spacer(1, 15))

    color_status = (
        colors.green if "APROVADO" in status_audit else colors.red
    )

    story.append(
        Paragraph(
            f"<b>STATUS DA AUDITORIA:</b> "
            f"<font color='{color_status.hexval()}'>{escape(status_audit)}</font>",
            normal_style,
        )
    )

    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "<b>Detalhamento da Análise de Compliance e Segurança:</b>",
            bold_style,
        )
    )

    story.append(Spacer(1, 5))

    for item in parecer_detalhes:
        story.append(
            Paragraph(f"• {escape(str(item))}", normal_style)
        )
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 20))

    story.append(
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.lightgrey,
            spaceAfter=15,
        )
    )

    conteudo_para_hash = (
        f"{projeto_nome}-{processo}-{status_audit}-{data_emissao}"
    ).encode("utf-8")

    hash_documento = hashlib.sha256(conteudo_para_hash).hexdigest().upper()

    story.append(
        Paragraph(
            "<b>Código de Validação e Autenticidade (SHA-256):</b>",
            bold_style,
        )
    )

    story.append(
        Paragraph(
            f"<font fontName='Courier' size=8>{hash_documento}</font>",
            normal_style,
        )
    )

    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "<i>Documento gerado automaticamente pelo Sistema CATS-SESP "
            "conforme Resolução SESP/PR 2026, PoSIC v2.0 e Deliberação "
            "CGD-SI nº 5/2025.</i>",
            footer_style,
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer


# =============================================================================
# =============================================================================
# SIDEBAR / NAVEGAÇÃO PARA O MENU ADPTADO
# =============================================================================

st.sidebar.markdown(
    """
    <div style="padding:0.35rem 0.2rem 1rem;">
        <div style="font-size:1.45rem;font-weight:750;">
            CATS-SESP
        </div>
        <div style="font-size:0.78rem;color:#B9CAD8;margin-top:0.2rem;">
            Governança, Segurança e Ativos Tecnológicos
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Valores internos inteiros: a lógica não depende do texto do rótulo.
modulos = {
    1: "Gestão de Projetos",
    2: "Matriz de Titularidade",
    3: "Inventário de IA",
    4: "Checklist de Aceite",
    5: "Auditoria PoSIC & CGD-SI (NSIC-05)",
    6: "Varredura de Sigilo em PDFs (RAG/IA)",
    7: "Painel de Auditoria e Relatórios",
}

menu = st.sidebar.radio(
    "MÓDULOS DO SISTEMA",
    options=list(modulos.keys()),
    format_func=lambda x: modulos[x],
    index=0,
    key="cats_menu",
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    """
    <div style="color:#B9CAD8;font-size:0.72rem;line-height:1.5;padding:0.4rem 0.2rem;">
        CATS-SESP
    </div>
    """,
    unsafe_allow_html=True,
)


# MÓDULO 1 — GESTÃO DE PROJETOS
# =============================================================================

if menu == 1:

    render_header(
        "Gestão de Projetos",
        "Cadastro e administração dos projetos de inovação e tecnologia vinculados ao CATS-SESP.",
    )

    df_proj = get_projects()

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Projetos cadastrados", len(df_proj), "Base atual do sistema")
    with c2:
        metric_card(
            "Instituições",
            df_proj["institucion"].nunique() if not df_proj.empty else 0,
            "Instituições executoras",
        )
    with c3:
        metric_card(
            "Responsáveis",
            df_proj["responsavel_tecnico"].nunique()
            if not df_proj.empty
            else 0,
            "Responsáveis técnicos",
        )

    st.markdown("###  Novo projeto")

    with st.expander("Cadastrar novo projeto", expanded=False):
        with st.form("form_novo_projeto"):
            col1, col2 = st.columns(2)

            nome_p = col1.text_input("Nome do Projeto *")
            proc_p = col2.text_input("Número do Processo Administrativo")

            inst_p = col1.text_input(
                "Instituição Executora",
                placeholder="Ex.: UFPR, ICT, empresa",
            )

            resp_p = col2.text_input("Responsável Técnico")

            data_p = st.date_input(
                "Data de Início",
                datetime.now(),
            )

            btn_salvar_proj = st.form_submit_button(
                "Cadastrar Projeto",
                type="primary",
            )

            if btn_salvar_proj:
                if nome_p.strip():
                    run_query(
                        """
                        INSERT INTO projetos
                        (nome, processo, institucion, responsavel_tecnico, data_inicio)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            nome_p.strip(),
                            proc_p.strip(),
                            inst_p.strip(),
                            resp_p.strip(),
                            str(data_p),
                        ),
                    )

                    st.success(
                        f"Projeto '{nome_p}' cadastrado com sucesso!"
                    )
                    st.rerun()
                else:
                    st.error("O nome do projeto é obrigatório.")

    if not df_proj.empty:
        st.markdown("### ️ Projetos cadastrados")

        with st.expander(
            "Editar ou excluir projeto existente",
            expanded=False,
        ):
            proj_dict = dict(zip(df_proj["nome"], df_proj["id"]))

            selected_edit_name = st.selectbox(
                "Selecione o projeto:",
                list(proj_dict.keys()),
            )

            selected_edit_id = proj_dict[selected_edit_name]

            proj_data = df_proj[
                df_proj["id"] == selected_edit_id
            ].iloc[0]

            col1, col2 = st.columns(2)

            with st.form("form_edit_proj"):
                e_nome = col1.text_input(
                    "Nome do Projeto",
                    value=proj_data["nome"],
                )

                e_proc = col2.text_input(
                    "Número do Processo",
                    value=proj_data["processo"] or "",
                )

                e_inst = col1.text_input(
                    "Instituição Executora",
                    value=proj_data["institucion"] or "",
                )

                e_resp = col2.text_input(
                    "Responsável Técnico",
                    value=proj_data["responsavel_tecnico"] or "",
                )

                btn_atualizar = st.form_submit_button(
                    "Atualizar Dados",
                    type="primary",
                )

                if btn_atualizar:
                    run_query(
                        """
                        UPDATE projetos
                        SET nome=?, processo=?, institucion=?, responsavel_tecnico=?
                        WHERE id=?
                        """,
                        (
                            e_nome,
                            e_proc,
                            e_inst,
                            e_resp,
                            selected_edit_id,
                        ),
                    )

                    st.success("Projeto atualizado com sucesso!")
                    st.rerun()

            st.warning(
                "A exclusão remove também os registros vinculados ao projeto."
            )

            if st.button(
                f"Excluir definitivamente '{selected_edit_name}'",
                type="secondary",
            ):
                run_query(
                    "DELETE FROM matriz_titularidade WHERE projeto_id=?",
                    (selected_edit_id,),
                )
                run_query(
                    "DELETE FROM inventario_ia WHERE projeto_id=?",
                    (selected_edit_id,),
                )
                run_query(
                    "DELETE FROM encerramento_aceite WHERE projeto_id=?",
                    (selected_edit_id,),
                )
                run_query(
                    "DELETE FROM auditoria_posic WHERE projeto_id=?",
                    (selected_edit_id,),
                )
                run_query(
                    "DELETE FROM projetos WHERE id=?",
                    (selected_edit_id,),
                )

                st.warning(
                    f"Projeto '{selected_edit_name}' e registros vinculados foram apagados."
                )
                st.rerun()

        st.markdown("###  Base de projetos")

        display_df = df_proj.rename(
            columns={
                "id": "ID",
                "nome": "Projeto",
                "processo": "Processo",
                "institucion": "Instituição",
                "responsavel_tecnico": "Responsável",
                "data_inicio": "Início",
            }
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("Ainda não existem projetos cadastrados.")


# =============================================================================
# MÓDULO 2 — MATRIZ DE TITULARIDADE
# =============================================================================

elif menu == 2:

    render_header(
        "Matriz de Titularidade",
        "Classificação dos ativos, direitos de uso, exploração e transferência.",
    )

    df_proj = get_projects()

    if df_proj.empty:
        st.warning(
            "Nenhum projeto cadastrado. Cadastre um projeto primeiro em Gestão de Projetos."
        )
    else:
        proj_dict = dict(zip(df_proj["nome"], df_proj["id"]))

        selected_proj_name = st.selectbox(
            "Selecione o projeto:",
            list(proj_dict.keys()),
        )

        selected_proj_id = proj_dict[selected_proj_name]

        st.markdown("### 1. Classificação do ativo tecnológico")

        with st.form("form_matriz"):
            col1, col2 = st.columns(2)

            nome_ativo = col1.text_input(
                "Nome do Ativo",
                placeholder="Ex.: módulo de visão, algoritmo, base consolidada",
            )

            categoria = col2.selectbox(
                "Categoria do Ativo",
                [
                    "A - Background IP SESP/PR (Preexistente da SESP)",
                    "B - Background IP Executora (Preexistente da Universidade/Empresa)",
                    "C - Tecnologia de Terceiros (Open Source ou Proprietária)",
                    "D - Foreground IP (Criado especificamente no projeto)",
                    "E - Resultado Derivado (Modificação, fine-tuning, combinação)",
                ],
            )

            st.markdown("### 2. Direitos patrimoniais e operacionais")

            c1, c2, c3, c4 = st.columns(4)

            tit_sesp = c1.checkbox("Titularidade SESP/PR")
            tit_inst = c2.checkbox("Titularidade Instituição Executora")
            dir_exp = c3.checkbox("Direito de Exploração Econômica")
            dir_transf = c4.checkbox("Direito de Transferência a Terceiros")

            st.markdown("### 3. Direitos assegurados à SESP/PR")

            m1, m2, m3, m4 = st.columns(4)

            m1.checkbox("Licença Perpétua e Irrevogável", value=True)
            m2.checkbox("Direito de Modificação/Adaptação", value=True)
            m3.checkbox("Direito de Manutenção por Terceiros", value=True)
            m4.checkbox("Direito de Auditoria", value=True)

            btn_salvar_matriz = st.form_submit_button(
                "Registrar Ativo na Matriz",
                type="primary",
            )

            if btn_salvar_matriz:
                if not nome_ativo.strip():
                    st.error("Informe o nome do ativo.")
                else:
                    run_query(
                        """
                        INSERT INTO matriz_titularidade
                        (
                            projeto_id,
                            nome_ativo,
                            categoria,
                            titular_sesp,
                            titular_instituicao,
                            direito_exploracao,
                            direito_transferencia
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            selected_proj_id,
                            nome_ativo.strip(),
                            categoria[0],
                            tit_sesp,
                            tit_inst,
                            dir_exp,
                            dir_transf,
                        ),
                    )

                    st.success(
                        f"Ativo '{nome_ativo}' registrado com sucesso!"
                    )
                    st.rerun()

        st.markdown("###  Ativos registrados")

        df_matriz = read_query(
            """
            SELECT
                nome_ativo AS Ativo,
                categoria AS Categoria,
                titular_sesp AS "SESP Titular",
                titular_instituicao AS "Instituição Titular",
                direito_exploracao AS "Exploração",
                direito_transferencia AS "Transferência"
            FROM matriz_titularidade
            WHERE projeto_id = ?
            ORDER BY id DESC
            """,
            (selected_proj_id,),
        )

        st.dataframe(
            df_matriz,
            use_container_width=True,
            hide_index=True,
        )


# =============================================================================
# MÓDULO 3 — INVENTÁRIO DE IA
# =============================================================================

elif menu == 3:

    render_header(
        "Inventário de Inteligência Artificial",
        "Registro de modelos, bases utilizadas, licenças, fine-tuning e métricas.",
    )

    df_proj = get_projects()

    if df_proj.empty:
        st.warning(
            "Cadastre um projeto antes de inventariar um modelo de IA."
        )
    else:
        proj_dict = dict(zip(df_proj["nome"], df_proj["id"]))

        selected_proj_name = st.selectbox(
            "Selecione o projeto:",
            list(proj_dict.keys()),
            key="ia_proj",
        )

        selected_proj_id = proj_dict[selected_proj_name]

        with st.form("form_ia_detalhado"):

            c1, c2, c3 = st.columns(3)

            modelo_nome = c1.text_input(
                "Nome Interno do Modelo Resultante"
            )

            modelo_base = c2.text_input(
                "Modelo-Base Utilizado",
                placeholder="Ex.: Llama-3-8B, YOLOv8",
            )

            licenca = c3.text_input(
                "Licença",
                placeholder="Ex.: Apache 2.0, MIT, Llama License",
            )

            fez_ft = st.radio(
                "Foi realizado Fine-Tuning / Ajuste Fino?",
                ["Não", "Sim"],
                horizontal=True,
            )

            metodo_ft = (
                st.multiselect(
                    "Métodos Empregados",
                    [
                        "Full Fine-Tuning",
                        "LoRA",
                        "QLoRA",
                        "Adapter",
                        "Transfer Learning",
                    ],
                )
                if fez_ft == "Sim"
                else []
            )

            st.markdown("###  Métricas de avaliação")

            m1, m2 = st.columns(2)

            acuracia = m1.number_input(
                "Acurácia (0.0 a 1.0)",
                min_value=0.0,
                max_value=1.0,
                value=0.90,
                step=0.01,
            )

            f1 = m2.number_input(
                "F1-Score (0.0 a 1.0)",
                min_value=0.0,
                max_value=1.0,
                value=0.88,
                step=0.01,
            )

            btn_ia = st.form_submit_button(
                "Gravar Modelo no Inventário",
                type="primary",
            )

            if btn_ia:
                if not modelo_nome.strip():
                    st.error("Informe o nome interno do modelo.")
                else:
                    run_query(
                        """
                        INSERT INTO inventario_ia
                        (
                            projeto_id,
                            modelo_nome,
                            modelo_base,
                            licenca,
                            fine_tuning,
                            metodo_ft,
                            acuracia,
                            f1_score
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            selected_proj_id,
                            modelo_nome.strip(),
                            modelo_base.strip(),
                            licenca.strip(),
                            fez_ft == "Sim",
                            ", ".join(metodo_ft),
                            acuracia,
                            f1,
                        ),
                    )

                    st.success(
                        "Modelo registrado no inventário do CATS-SESP!"
                    )
                    st.rerun()

        st.markdown("###  Modelos inventariados")

        df_ia = read_query(
            """
            SELECT
                modelo_nome AS Modelo,
                modelo_base AS "Modelo Base",
                licenca AS Licença,
                fine_tuning AS "Fine-Tuning",
                metodo_ft AS Método,
                acuracia AS Acurácia,
                f1_score AS "F1-Score"
            FROM inventario_ia
            WHERE projeto_id = ?
            ORDER BY id DESC
            """,
            (selected_proj_id,),
        )

        st.dataframe(
            df_ia,
            use_container_width=True,
            hide_index=True,
        )


# =============================================================================
# MÓDULO 4 — CHECKLIST DE ACEITE
# =============================================================================

elif menu == 4:

    render_header(
        "Checklist de Aceite e Encerramento",
        "Verificação técnica de entregáveis, código, modelos, dados e continuidade operacional.",
    )

    df_proj = get_projects()

    if df_proj.empty:
        st.warning("Nenhum projeto cadastrado.")
    else:
        proj_dict = dict(zip(df_proj["nome"], df_proj["id"]))

        selected_proj_name = st.selectbox(
            "Selecione o projeto para encerramento:",
            list(proj_dict.keys()),
            key="enc_proj",
        )

        selected_proj_id = proj_dict[selected_proj_name]

        with st.form("form_aceite"):

            st.markdown("### 1. Entregáveis de software e código-fonte")

            c1, c2, c3 = st.columns(3)

            cod_entregue = c1.checkbox(
                "Código-fonte integral disponibilizado"
            )
            repo_git = c2.checkbox(
                "Repositório Git com histórico e branches entregue"
            )
            doc_api = c3.checkbox(
                "APIs e Arquitetura documentadas"
            )

            st.markdown("### 2. Entregáveis de IA e dados")

            i1, i2, i3 = st.columns(3)

            pesos_entregues = i1.checkbox(
                "Pesos/Checkpoints do Modelo entregues"
            )
            dados_tratados = i2.checkbox(
                "Dados da SESP devolvidos/eliminados"
            )
            ambientes_limpos = i3.checkbox(
                "Ambientes temporários de teste eliminados"
            )

            st.markdown("### 3. Vendor Lock-In e continuidade")

            v1, v2 = st.columns(2)

            vendor_lockin = v1.radio(
                "Risco de Vendor Lock-in Identificado?",
                ["Não", "Sim"],
            )

            capacitacao = v2.checkbox(
                "Treinamento e Capacitação da equipe SESP realizados"
            )

            st.markdown("### 4. Parecer final")

            status_final = st.selectbox(
                "Conclusão da Fiscalização Técnica:",
                [
                    "ENCERRAMENTO APROVADO (Aceite Definitivo)",
                    "ENCERRAMENTO APROVADO COM RESSALVAS (Pendências não críticas)",
                    "ENCERRAMENTO NÃO APROVADO (Pendências críticas de código/dados/modelos)",
                ],
            )

            btn_encerramento = st.form_submit_button(
                "Registrar Termo de Aceite / Encerramento",
                type="primary",
            )

            if btn_encerramento:
                run_query(
                    """
                    INSERT INTO encerramento_aceite
                    (
                        projeto_id,
                        codigo_fonte_entregue,
                        repositorio_git,
                        pesos_ia_entregues,
                        dados_devolvidos_eliminados,
                        vendor_lockin_identificado,
                        status_encerramento,
                        data_registro
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        selected_proj_id,
                        cod_entregue,
                        repo_git,
                        pesos_entregues,
                        dados_tratados,
                        vendor_lockin == "Sim",
                        status_final,
                        datetime.now().strftime("%Y-%m-%d %H:%M"),
                    ),
                )

                if "NÃO APROVADO" in status_final:
                    st.error(
                        "Encerramento NÃO APROVADO retido até sanar as pendências apontadas."
                    )
                else:
                    st.success(
                        "Termo de Aceite registrado com sucesso!"
                    )

                st.rerun()

        st.markdown("###  Histórico de encerramentos")

        df_enc = read_query(
            """
            SELECT
                e.id AS ID,
                p.nome AS Projeto,
                e.status_encerramento AS Status,
                e.data_registro AS Registro,
                e.codigo_fonte_entregue AS "Código Entregue",
                e.repositorio_git AS "Git",
                e.pesos_ia_entregues AS "Pesos IA",
                e.dados_devolvidos_eliminados AS "Dados Devolvidos",
                e.vendor_lockin_identificado AS "Vendor Lock-in"
            FROM encerramento_aceite e
            JOIN projetos p ON p.id = e.projeto_id
            WHERE e.projeto_id = ?
            ORDER BY e.id DESC
            """,
            (selected_proj_id,),
        )

        st.dataframe(
            df_enc,
            use_container_width=True,
            hide_index=True,
        )


# =============================================================================
# MÓDULO 5 — AUDITORIA
# =============================================================================

elif menu == 5:

    render_header(
        "Auditoria PoSIC & CGD-SI",
        "Diagnóstico de conformidade, segurança da informação e geração de parecer técnico.",
    )

    df_proj = get_projects()

    if df_proj.empty:
        st.warning(
            "Cadastre um projeto em Gestão de Projetos para realizar a auditoria."
        )
    else:
        proj_dict = {
            row["nome"]: (
                row["id"],
                row["processo"],
                row["institucion"],
            )
            for _, row in df_proj.iterrows()
        }

        selected_proj_name = st.selectbox(
            "Selecione o projeto para auditagem:",
            list(proj_dict.keys()),
            key="audit_posic",
        )

        selected_proj_id, proc_val, inst_val = proj_dict[
            selected_proj_name
        ]

        with st.form("form_auditoria_posic"):

            st.markdown(
                "### 1. Regras para Inteligência Artificial — NSIC-05"
            )

            ia_pessoal = st.checkbox(
                "Utiliza ferramentas de IA através de contas pessoais/gratuitas "
                "(ex.: ChatGPT/Gemini pessoal)?"
            )

            prompts_sensiveis = st.checkbox(
                "Alimenta modelos externos de IA com dados pessoais, "
                "inquéritos ou detalhes operacionais?"
            )

            ripd_ok = st.checkbox(
                "Possui Relatório de Impacto à Proteção de Dados (RIPD) "
                "aprovado pelo Controlador?"
            )

            st.markdown("### 2. Segurança da Informação")

            mfa_ok = st.checkbox(
                "Autenticação Multifator (MFA/2FA) ativada para acessos "
                "externos e administrativos?"
            )

            retencao_logs = st.number_input(
                "Prazo configurado de retenção de logs de acesso (em dias):",
                min_value=0,
                max_value=365,
                value=180,
            )

            st.markdown("### 3. Roteamento de Governança Estadual")

            camara = st.selectbox(
                "Câmara Técnica Responsável para Parecer:",
                [
                    "CT-IA (Inteligência Artificial)",
                    "CT-SID (Segurança da Informação e Dados)",
                    "CT-GOA (Gestão Orçamentária e Aquisições)",
                    "CT-GSTIC (Gestão de Serviços de TIC)",
                    "CT-NDGD (Normas de Governança Digital)",
                    "CT-IPE (Integração e Planejamento Estratégico)",
                ],
            )

            btn_auditar = st.form_submit_button(
                "Executar Diagnóstico e Gerar Parecer",
                type="primary",
            )

            if btn_auditar:

                inconformidades = []
                parecer_detalhes = []

                if ia_pessoal:
                    inconformidades.append(
                        "NSIC-05 Art. 4: É VEDADO o uso de IA via contas pessoais ou gratuitas."
                    )
                    parecer_detalhes.append(
                        "VIOLAÇÃO: Identificado uso de contas de IA não homologadas pela CTIC."
                    )
                else:
                    parecer_detalhes.append(
                        "CONFORME: Ausência de uso de ferramentas de IA não corporativas."
                    )

                if prompts_sensiveis:
                    inconformidades.append(
                        "NSIC-05 Art. 4: Proibido o fornecimento de prompts com dados sensíveis/policiais a IAs externas."
                    )
                    parecer_detalhes.append(
                        "VIOLAÇÃO: Risco de exfiltração de dados sensíveis em prompts de IA externa."
                    )
                else:
                    parecer_detalhes.append(
                        "CONFORME: Nenhum dado sensível é transmitido para modelos externos."
                    )

                if not ripd_ok:
                    inconformidades.append(
                        "NSIC-05 Item IV: Projetos de IA exigem RIPD aprovado pelo Controlador."
                    )
                    parecer_detalhes.append(
                        "PENDÊNCIA: Falta a apresentação de Relatório de Impacto à Proteção de Dados."
                    )
                else:
                    parecer_detalhes.append(
                        "CONFORME: RIPD devidamente aprovado pelo Controlador."
                    )

                if not mfa_ok:
                    inconformidades.append(
                        "NSIC-02 / NSIC-10: MFA é obrigatório para VPN e acessos sensíveis."
                    )
                    parecer_detalhes.append(
                        "PENDÊNCIA: Autenticação Multifator não está ativada nas credenciais críticas."
                    )
                else:
                    parecer_detalhes.append(
                        "CONFORME: Autenticação de Múltiplos Fatores habilitada."
                    )

                if retencao_logs < 90:
                    inconformidades.append(
                        "NSIC-03 / NSIC-08: A retenção de logs deve ser de no mínimo 90 a 180 dias."
                    )
                    parecer_detalhes.append(
                        f"VIOLAÇÃO: Retenção configurada ({retencao_logs} dias) está abaixo do mínimo regulamentar."
                    )
                else:
                    parecer_detalhes.append(
                        f"CONFORME: Retenção de logs configurada para {retencao_logs} dias."
                    )

                status_final = (
                    "REPROVADO / EM INCONFORMIDADE"
                    if inconformidades
                    else "APROVADO / EM CONFORMIDADE"
                )

                conn = get_connection()
                c = conn.cursor()

                c.execute(
                    """
                    INSERT INTO auditoria_posic
                    (
                        projeto_id,
                        uso_ia_pessoal,
                        prompts_sensiveis_externos,
                        ripd_aprovado,
                        mfa_ativo,
                        retencao_logs_dias,
                        camara_tecnica_designada,
                        status_conformidade,
                        data_auditoria
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        selected_proj_id,
                        ia_pessoal,
                        prompts_sensiveis,
                        ripd_ok,
                        mfa_ok,
                        retencao_logs,
                        camara,
                        status_final,
                        datetime.now().strftime("%Y-%m-%d %H:%M"),
                    ),
                )

                conn.commit()
                conn.close()

                if inconformidades:
                    st.error(f"Status: {status_final}")

                    for inc in inconformidades:
                        st.write(f"• {inc}")
                else:
                    st.success(f"Status: {status_final}")

                pdf_buffer = gerar_pdf_parecer_tecnico(
                    selected_proj_name,
                    proc_val,
                    inst_val,
                    status_final,
                    camara,
                    parecer_detalhes,
                )

                st.download_button(
                    label="Baixar Parecer Técnico Oficial em PDF",
                    data=pdf_buffer,
                    file_name=f"Parecer_CATS_{selected_proj_id}.pdf",
                    mime="application/pdf",
                )

        st.markdown("###  Histórico de auditorias")

        df_aud = read_query(
            """
            SELECT
                id AS ID,
                status_conformidade AS Status,
                camara_tecnica_designada AS "Câmara Técnica",
                retencao_logs_dias AS "Retenção (dias)",
                data_auditoria AS Data
            FROM auditoria_posic
            WHERE projeto_id = ?
            ORDER BY id DESC
            """,
            (selected_proj_id,),
        )

        st.dataframe(
            df_aud,
            use_container_width=True,
            hide_index=True,
        )


# =============================================================================
# MÓDULO 6 — VARREDURA DE SIGILO EM PDFS
# =============================================================================

elif menu == 6:

    render_header(
        "Varredura de Sigilo em PDFs",
        "Análise textual de documentos PDF para identificação de termos potencialmente sensíveis.",
    )

    st.info(
        "A análise abaixo é uma triagem automatizada baseada no texto extraído "
        "do PDF. O resultado não substitui revisão técnica ou jurídica."
    )

    uploaded_file = st.file_uploader(
        "Submeta o artigo, tese ou relatório técnico em PDF:",
        type=["pdf"],
    )

    if uploaded_file is not None:

        try:
            reader = pypdf.PdfReader(uploaded_file)

            texto_completo = ""

            for page in reader.pages:
                texto_completo += page.extract_text() or ""

            st.success(
                f"Ficheiro lido com sucesso! "
                f"Total de páginas: {len(reader.pages)}."
            )

            with st.spinner(
                "Executando a varredura DLP e análise de termos sensíveis..."
            ):

                termos_sensiveis = [
                    "inquérito policial",
                    "dado pessoal",
                    "CPF",
                    "biometria",
                    "operação policial",
                    "segredo de justiça",
                    "vulnerabilidade",
                    "ip público",
                    "senha",
                    "hash de senha",
                    "investigado",
                ]

                alertas = []
                texto_lower = texto_completo.lower()

                for termo in termos_sensiveis:
                    if termo.lower() in texto_lower:
                        ocorrencias = texto_lower.count(
                            termo.lower()
                        )

                        alertas.append(
                            f"Termo sensível detectado: "
                            f"**'{termo}'** ({ocorrencias} ocorrência(s))."
                        )

            st.markdown("###  Resultado da triagem DLP")

            if alertas:
                st.warning(
                    "Foram identificados potenciais riscos à segurança "
                    "da informação ou privacidade:"
                )

                for al in alertas:
                    st.markdown(f"- {al}")

                st.error(
                    "Recomendação: submeter o material para revisão "
                    "prévia da SESP/PR antes da publicação."
                )

            else:
                st.success(
                    "Nenhuma ocorrência dos termos monitorados foi "
                    "detectada no texto extraído."
                )

            with st.expander(
                "Visualizar texto extraído para auditoria manual"
            ):
                st.text_area(
                    "Conteúdo do PDF:",
                    texto_completo,
                    height=350,
                )

        except Exception as e:
            st.error(
                f"Erro ao processar o ficheiro PDF: {e}"
            )


# =============================================================================
# MÓDULO 7 — PAINEL 
# =============================================================================

elif menu == 7:

    render_header(
        "Painel Executivo de Auditoria",
        "Visão consolidada dos projetos, ativos tecnológicos, modelos de IA e conformidade.",
    )

    df_proj = get_projects()

    df_ativos = read_query(
        "SELECT COUNT(*) AS total FROM matriz_titularidade"
    )

    df_modelos = read_query(
        "SELECT COUNT(*) AS total FROM inventario_ia"
    )

    df_aud = read_query(
        "SELECT COUNT(*) AS total FROM auditoria_posic"
    )

    total_projetos = len(df_proj)
    total_ativos = int(df_ativos.iloc[0]["total"])
    total_modelos = int(df_modelos.iloc[0]["total"])
    total_auditorias = int(df_aud.iloc[0]["total"])

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Projetos",
            total_projetos,
            "Projetos cadastrados",
        )

    with c2:
        metric_card(
            "Ativos",
            total_ativos,
            "Ativos na matriz",
        )

    with c3:
        metric_card(
            "Modelos de IA",
            total_modelos,
            "Modelos inventariados",
        )

    with c4:
        metric_card(
            "Auditorias",
            total_auditorias,
            "Auditorias registradas",
        )

    st.markdown("###  Consolidação por projeto")

    query_audit = """
        SELECT
            p.id AS ID,
            p.nome AS Projeto,
            p.institucion AS Executora,

            (
                SELECT COUNT(*)
                FROM matriz_titularidade m
                WHERE m.projeto_id = p.id
            ) AS Ativos_Mapeados,

            (
                SELECT COUNT(*)
                FROM inventario_ia ia
                WHERE ia.projeto_id = p.id
            ) AS Modelos_IA,

            COALESCE(
                (
                    SELECT e.status_encerramento
                    FROM encerramento_aceite e
                    WHERE e.projeto_id = p.id
                    ORDER BY e.id DESC
                    LIMIT 1
                ),
                'Em Execução / Não Encerrado'
            ) AS Status_Encerramento,

            COALESCE(
                (
                    SELECT pos.status_conformidade
                    FROM auditoria_posic pos
                    WHERE pos.projeto_id = p.id
                    ORDER BY pos.id DESC
                    LIMIT 1
                ),
                'Não Auditado'
            ) AS Compliance_PoSIC

        FROM projetos p
        ORDER BY p.nome
    """

    df_audit = read_query(query_audit)

    if df_audit.empty:
        st.info(
            "Nenhum projeto disponível para o painel."
        )
    else:
        st.dataframe(
            df_audit,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("###  Exportação")

    if not df_proj.empty:

        df_full = read_query(
            "SELECT * FROM projetos ORDER BY id"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="Baixar Base de Projetos (JSON)",
                data=df_full.to_json(orient="records"),
                file_name="cats_sesp_projetos.json",
                mime="application/json",
            )

        with col2:
            st.download_button(
                label="Baixar Painel Consolidado (CSV)",
                data=df_audit.to_csv(index=False).encode("utf-8-sig"),
                file_name="cats_sesp_painel_auditoria.csv",
                mime="text/csv",
            )


# =============================================================================
# RODAPÉ
# =============================================================================

st.markdown(
    """
    <div class="cats-footer">
        CATS-SESP • Cadastro de Ativos Tecnológicos e Governança
        <br>
        Interface de governança, segurança da informação e auditoria tecnológica
    </div>
    """,
    unsafe_allow_html=True,
)
