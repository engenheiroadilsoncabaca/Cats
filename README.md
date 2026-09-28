# CATS-SESP — Cadastro e Governança de Ativos Tecnológicos da SESP/PR

O **CATS-SESP** é um sistema web desenvolvido em Python e Streamlit para facilitar, modernizar e automatizar a gestão de propriedade intelectual, modelos de Inteligência Artificial, transferência tecnológica e conformidade com a segurança da informação na Secretaria de Estado da Segurança Pública do Paraná.

---

## Conformidade Normativa

O sistema foi desenvolvido para garantir conformidade direta com os seguintes marcos legais e regulamentares:

* **Resolução SESP/PR 2026:** Propriedade Intelectual, Código-Fonte, Modelos de IA e Transferência Tecnológica.
* **PoSIC SESP-PR v2.0:** Política de Segurança da Informação, Comunicações e Privacidade e suas Normas de Segurança (NSIC-01 a 11, em especial NSIC-05 para IA e NSIC-08 para DLP).
* **Deliberação CGD-SI nº 5/2025:** Política Estadual de Governança de TIC do Paraná e roteamento para as Câmaras Técnicas (CT-IA, CT-SID, CT-GOA, etc.).
* **Guia de PDTIC do SISP v2.1:** Ciclo de vida do Planejamento Diretor de TIC (Preparação, Diagnóstico e Planejamento).

---

##  Funcionalidades do Sistema

1. **Gestão de Projetos:** Cadastro, edição e exclusão de processos administrativos e instituições executoras.
2. **Matriz de Titularidade (Anexo VIII):** Mapeamento de Background IP, Foreground IP e permissões de uso e exploração econômica.
3. **Inventário de IA (Anexo VI):** Registro de modelos-base, hiperparâmetros, métodos de *fine-tuning* (LoRA/QLoRA) e métricas de acurácia/F1-Score.
4. **Checklist de Aceite e Desmobilização (Anexos III/VII):** Validação técnica de repositórios Git, entrega de pesos de IA, eliminação de bases temporárias e prevenção ao *vendor lock-in*.
5. **Auditoria PoSIC & CGD-SI (NSIC-05):** Validação automatizada de regras de segurança de IA, uso de contas pessoais, RIPD, MFA e retenção de logs com emissão de **Parecer Técnico em PDF assinado via Hash SHA-256**.
6. **Varredura Preditiva em PDFs (DLP/RAG):** Leitura de artigos e relatórios técnicos em PDF com varredura automática de termos sensíveis (CPFs, biometria, segredo de justiça).
7. **Painel Executivo de Auditoria:** Visão consolidada de compliance e exportação da base em JSON.

---

## Tecnologias Utilizadas

* **Linguagem:** Python 3.11
* **Interface Web:** Streamlit
* **Banco de Dados:** SQLite3 (Relacional)
* **Geração de Documentos:** ReportLab (com autenticação SHA-256)
* **Processamento de PDFs:** PyPDF
* **Análise de Dados:** Pandas

---

## Como Rodar Localmente

1. Clone o repositório:
   ```bash
   git clone https://github.com/engenheiroadilsoncabaca/Cats.git
   cd cats-sesp