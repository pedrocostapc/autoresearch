# 05 — Documentos

> Substitui: PandaDoc, DocuSign templates, Notion AI, Adobe Sign Templates, scribbr, getaccept.

## Por que substituir

Voce paga por **template parametrizavel + assinatura eletronica**. O Claude monta documento perfeito em 1 prompt. A assinatura voce faz com **gov.br (gratis no Brasil) ou Adobe Acrobat Reader (gratis)**.

## Comparativo de custo (Brasil, 2026)

| Ferramenta | Plano | Mensal/seat | Anual |
|---|---|---|---|
| PandaDoc | Essentials | US$ 19 (~R$ 105) | R$ 1.260 |
| PandaDoc | Business | US$ 49 (~R$ 270) | R$ 3.240 |
| DocuSign | Standard | US$ 25 (~R$ 140) | R$ 1.680 |
| DocuSign | Business Pro | US$ 40 (~R$ 220) | R$ 2.640 |
| Notion AI | add-on | US$ 10 (~R$ 55) | R$ 660 |
| Adobe Acrobat Pro | Pro | R$ 90/mes | R$ 1.080 |

vs. **Claude Pro (R$ 110/mes)** para gerar + **gov.br (gratis)** para assinar = ~R$ 110/mes.

Economia tipica: R$ 50-200/mes por seat = **R$ 600-2.400/ano**.

## Volume

| Volume | Solucao |
|---|---|
| Ate 50 documentos/mes | Claude Pro web — manual |
| 50-200/mes | Claude Pro + scripts (gera + ja salva PDF) |
| 200+/mes | API + template em codigo |

## Tipos de documento que esse pacote cobre

1. Proposta comercial
2. Contrato de prestacao de servico
3. Termo de aceite simples
4. Acordo de confidencialidade (NDA)
5. Briefing de projeto
6. Recibo
7. Carta de cobranca
8. Memorando de entendimento (MoU)

Outros tipos voce adapta facil.

## A logica deste prompt

3 partes:

### Parte A — Configurar dados das partes (1 vez)
Roda 1 vez por entidade contratante. Salva em `partes/sua-empresa.md` e `partes/{cliente}.md`. Pra evitar repetir CNPJ/endereco toda hora.

### Parte B — Gerar documento (toda hora)
Cola dados das partes + tipo + condicoes. Sai documento pronto.

### Parte C — Assinatura
Como assinar e dar validade juridica sem DocuSign.

---

## Parte A — Configurar dados das partes

Roda 1 vez pra sua empresa, 1 vez pra cada cliente novo. Salva em `partes/`.

--- COMECO PROMPT A ---

Voce vai me ajudar a montar um arquivo de qualificacao da parte (sua empresa OU cliente). Esse arquivo sera usado como input em todos os documentos legais.

# Tipo de parte

{minha empresa | cliente}

# Me pergunte os dados

Pra cada item, faca a pergunta. Se for opcional, sinalize.

1. Razao social (obrigatorio)
2. Nome fantasia (opcional)
3. CNPJ (obrigatorio se PJ) ou CPF (se PF)
4. Inscricao estadual (opcional)
5. Endereco completo: rua, numero, complemento, bairro, cidade, UF, CEP (obrigatorio)
6. Email principal (obrigatorio)
7. Telefone (obrigatorio)
8. Representante legal: nome completo + CPF + cargo (obrigatorio se PJ)
9. Dados bancarios (opcional — uso em recibo, contrato com clausula de pagamento bancario):
   - Banco (numero e nome)
   - Agencia
   - Conta
   - Tipo (corrente/poupanca)
   - Pix

# Saida

```markdown
# Parte: {Razao Social}

## Identificacao
- Razao social: {...}
- Nome fantasia: {...}
- CNPJ: {...}
- IE: {...}

## Endereco
{rua}, {num}{complemento}
{bairro}, {cidade} - {UF}
CEP {cep}

## Contato
- Email: {...}
- Telefone: {...}

## Representante legal
{nome}, brasileiro(a), {cargo}, CPF {cpf}

## Dados bancarios
{se preenchido}
```

Pode comecar.

--- FIM PROMPT A ---

---

## Parte B — Gerar documento

Esse e o que voce roda toda hora.

--- COMECO PROMPT B ---

Voce e um advogado(a) e gestor(a) comercial juniores que monta documentos profissionais em portugues do Brasil, formato pronto pra enviar ao cliente.

# Partes envolvidas

## Contratada (eu/minha empresa)
{COLE AQUI O CONTEUDO DO partes/sua-empresa.md}

## Contratante (cliente)
{COLE AQUI O CONTEUDO DO partes/{cliente}.md OU preencha aqui se for one-off:
- Razao social: ...
- CNPJ: ...
- Endereco: ...
- Email: ...
- Representante: ...
}

# Tipo de documento

{ESCOLHA: 
- proposta comercial (com prazo de validade)
- contrato de prestacao de servico
- termo de aceite (simples, 1 pagina)
- NDA / acordo de confidencialidade
- briefing de projeto
- recibo
- carta de cobranca (1ª, 2ª ou 3ª — escalonando o tom)
- memorando de entendimento}

# Objeto

{Descreva o que sera entregue/contratado/cobrado, com o maximo de especificidade. Quanto mais especifico, melhor o documento sai. Inclua entregas, prazos por etapa, exclusoes (o que NAO esta incluso).}

# Valor e pagamento

- Valor total: R$ {VALOR}
- Forma: {ex: 50% no aceite, 50% na entrega; OU em 3x; OU mensalidade R$ X}
- Meio: {pix / boleto / transferencia / cartao}
- Vencimento: {DATAS especificas}
- Reajuste (se aplicavel): {ex: anual pelo IPCA}
- Multa por atraso: {ex: 2% + juros 1%am — pode usar default mercado}

# Prazo

{ex: "Entrega em 30 dias corridos a partir do aceite. Aprovacao do cliente em ate 5 dias uteis a partir da entrega de cada etapa, apos o que considera-se aprovada por aceite tácito."}

# Clausulas especiais (opcional)

{ex: "Direito de portfolio". "Confidencialidade por 2 anos apos termino". "Multa rescisoria de 30%". "Sem clausulas especiais"}

# Foro

{cidade/UF — usado pra clausula de eleicao de foro}

# Saida obrigatoria

Documento completo, formato markdown, com:

1. **Cabecalho**: titulo do documento + data + numero (se aplicavel)
2. **Qualificacao das partes**: usando o conteudo dos arquivos de partes
3. **Clausulas numeradas** (1ª, 2ª, 3ª...) cada uma com titulo curto
4. **Espaco para assinatura ao final** com:
   ```
   _______________________________
   {Nome}, {qualificacao}
   CONTRATADA
   
   _______________________________
   {Nome}, {qualificacao}
   CONTRATANTE
   ```
5. **Local e data**

Estrutura tipica de clausulas (adapte ao tipo):
- 1ª — DO OBJETO
- 2ª — DAS OBRIGACOES DA CONTRATADA
- 3ª — DAS OBRIGACOES DO CONTRATANTE
- 4ª — DO PRAZO
- 5ª — DO VALOR E DAS CONDICOES DE PAGAMENTO
- 6ª — DO REAJUSTE
- 7ª — DA RESCISAO
- 8ª — DA CONFIDENCIALIDADE
- 9ª — DAS DISPOSICOES GERAIS
- 10ª — DO FORO

# Estilo

- Linguagem juridica padrao (formal mas legivel — sem floreio escolastico)
- Evite "outrossim", "destarte", "ad quem" — usa portugues que o cliente le sem dicionario
- Numero por extenso quando for valor relevante: "R$ 5.000,00 (cinco mil reais)"
- Datas por extenso: "vinte e tres de marco de dois mil e vinte e seis"

# Aviso obrigatorio (incluir no rodape)

```
*Este documento foi elaborado com auxilio de IA e e recomendada revisao por advogado(a) antes da assinatura, especialmente em valores acima de R$ 10.000 ou em clausulas de responsabilidade ou propriedade intelectual.*
```

# Antes de gerar

Confira se faltou alguma informacao critica. Se sim, pergunte SO o essencial em uma unica mensagem (max 3 perguntas), depois gere o documento completo.

--- FIM PROMPT B ---

---

## Parte C — Como assinar (sem DocuSign)

### Opcao 1 — gov.br (Brasil — gratis e oficial)

Validade juridica conforme Lei 14.063/2020 (assinatura eletronica avancada).

Passos pro cliente:
1. Vai em https://www.gov.br/governodigital/pt-br/assinatura-eletronica
2. Loga (todos brasileiros tem conta)
3. Sobe o PDF do contrato
4. Assina digitalmente (com codigo do celular)
5. Baixa PDF assinado
6. Manda de volta pra voce

Voce repete o processo do seu lado pra contra-assinar.

**Custo:** zero. **Validade:** total.

### Opcao 2 — Adobe Acrobat Reader (gratis)

Pra cliente que prefere caminho mais conhecido:

1. Baixa Adobe Acrobat Reader (gratis)
2. Abre PDF
3. "Preencher e assinar" → desenha assinatura ou faz upload de imagem dela
4. Salva
5. Manda de volta

Validade no Brasil: aceitavel pra documentos comuns. Nao tem o peso da gov.br pra processos judiciais.

### Opcao 3 — WhatsApp + identificacao clara

Pra documentos baixos riscos (orcamento, briefing, termo simples):

```
Cliente envia mensagem no WhatsApp com:
"Eu, {nome completo}, CPF {cpf}, declaro estar de acordo com a proposta {numero} de {data}, no valor de R$ {valor}, e autorizo o inicio dos servicos."
```

Tem peso juridico (varias decisoes ja confirmaram). Pra processo serio, voce tem o documento + a tela do WhatsApp + telefone do cliente.

### Opcao 4 — PDF + foto da assinatura

Cliente imprime, assina, fotografa, manda de volta. Validade no Brasil aceita pra varios tipos de documento.

### Como gerar PDF a partir do markdown

```bash
# Instala pandoc + LaTeX (uma vez):
brew install pandoc          # Mac
brew install --cask basictex # se quiser PDF bonitinho

# Converte:
pandoc contrato.md -o contrato.pdf --pdf-engine=xelatex

# OU mais simples (sem LaTeX, gera HTML+CSS limpo):
pandoc contrato.md -o contrato.pdf
```

Ou online: https://www.markdowntopdf.com (gratis).

---

## Caso de uso real — Camisa BR

Marcelo precisava de:

- 1 contrato de fornecedor (TecidoCo) — anual
- ~5 propostas/mes pra atacado
- 1 termo de aceite por pedido especial

**Antes:** PandaDoc Essentials (R$ 105/mes).

**Migracao:**
1. Rodou Parte A pra "Camisa BR" — gerou `partes/camisa-br.md`
2. Cada cliente novo de atacado: roda Parte A pra ele — `partes/loja-estilo-sp.md`
3. Pra cada documento: Parte B com info do tipo + objeto + valor

Tempo medio por proposta: **8 minutos** (antes no PandaDoc: 15 min preenchendo template).

Assinatura: gov.br pra contratos grandes, WhatsApp confirmado pra propostas pequenas.

**Economia:** R$ 105/mes = R$ 1.260/ano.

**Bonus:** os documentos ficaram **mais customizados pro estilo da Camisa BR** porque o Marcelo edita facil. No PandaDoc, mexer em template era chato.

---

## Quando NAO substituir

| Situacao | Recomendacao |
|---|---|
| Volume alto (50+ contratos/mes) | DocuSign vale o seat |
| Compliance/auditoria (saber quem leu, quando, IP) | DocuSign | Adobe Sign |
| Time juridico que padroniza templates aprovados | Mantem ferramenta de template |
| Contratos > R$ 100k ou com clausulas complexas | Sempre revisar com advogado, independente da ferramenta |

## Erros comuns

1. **Confiar 100% no documento gerado** — sempre da uma lida. Em valores > R$ 10k, advogado ve
2. **Esquecer foro** — clausula chata mas necessaria
3. **Numero por extenso errado** — Claude erra as vezes. Confere
4. **Falta de aviso de IA no rodape** — pratica boa pra transparencia
5. **Salvar PDF antes de revisar** — ainda tem pra editar; salve so a versao final

## Biblioteca de tipos prontos

Casos especificos onde voce so adapta o prompt:

### Recibo simples
> Tipo: recibo. Objeto: pagamento de R$ {valor} referente a {servico/produto}. Pago em {data} via {meio}.

### Termo de uso de imagem
> Tipo: termo de cessao de imagem. Objeto: cessao de direito de uso de imagem do depoimento gravado em {data}, para uso em material institucional, redes sociais e materiais de marketing por prazo de {N} anos.

### Carta de cobranca 1ª
> Tipo: carta de cobranca tom amigavel. Objeto: lembrete de fatura {numero} no valor R$ {x} vencida em {data}, atrasada {N} dias. Oferecer prazo de 5 dias adicionais pra regularizar.

### Carta de cobranca 3ª (ja com tom de protesto)
> Tipo: carta de cobranca formal extra-judicial. Mencionar protesto + spc/serasa em 10 dias se nao regularizar. Tom firme mas profissional.

### NDA mutuo
> Tipo: NDA mutuo (ambas as partes se obrigam). Prazo de confidencialidade: 3 anos apos termino. Multa por violacao: R$ {valor} + perdas e danos.

### Briefing de projeto
> Tipo: briefing de projeto criativo. Objeto: {projeto}. Coletar informacoes sobre objetivo, publico-alvo, prazo, restricoes, referencias e criterios de aprovacao.

Sempre ajuste pro seu caso especifico.
