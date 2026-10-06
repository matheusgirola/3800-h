# Conversão completa — plano e andamento

Edição completa do *Ethics* (PG #3800) com links e pop-ups em todas as
referências, seguindo a **variante D** (ver `TOOLTIP_TEST_REPORT.md` §6).
O trabalho é feito **uma Parte por vez**, para que cada etapa possa ser
retomada numa sessão nova sem precisar do histórico.

## Andamento

| Parte | Itens | Links | Revisão | Observações |
|-------|------:|------:|---------|-------------|
| I     | 120 | 157 | **feita** (05/10/2026) | 4 correções manuais; nada pendente |
| II    | 188 | 268 | **feita** (05/10/2026) | 35 correções manuais; 6 excertos manuais; nada pendente |
| III   | 260 | 360 | **feita** (06/10/2026) | 40 correções manuais (dúvidas resolvidas no latim); 2 excertos manuais; nada pendente |
| IV    | 243 | 374 | **feita** (06/10/2026) | 35 correções manuais (dúvidas resolvidas no latim); 2 excertos manuais; nada pendente |
| V     | 113 | 235 | **feita** (06/10/2026) | 13 correções manuais (dúvidas resolvidas no latim); 2 excertos manuais; nada pendente |

Total: 1.394 links (1.410 linhas, 16 `skip`).

## Pipeline (`build/`)

Os comandos rodam na raiz do projeto (a organização das pastas está no
`README.md`).

```
python3 build/structure.py        # mapping/items.csv   — todos os itens numerados e seus ids
python3 build/refs.py N --residue  # mapping/refs-partN.csv — links da Parte N (+ possíveis omissões)
python3 build/build_html.py        # 3800-h-tooltips.html — o livro inteiro, links das partes já mapeadas
python3 build/check_text.py        # texto visível idêntico ao 3800-h.htm original?
python3 build/report.py            # mapping/ethics-dependencies.xlsx — planilha de dependências
```

Validação depois de cada parte (o alvo é zero mensagens):

```
curl -s -H "Content-Type: text/html; charset=utf-8" --data-binary @3800-h-tooltips.html "https://validator.w3.org/nu/?out=json"
curl -s -F "file=@3800-h-tooltips.html;type=text/html" -F "profile=css3" -F "output=text/plain" https://jigsaw.w3.org/css-validator/validator
```

## Arquivos de mapeamento (`mapping/`)

- **`items.csv`**: um item por linha (definição, axioma, postulado, lema,
  proposição, demonstração, corolário, nota, explicação, prefácio, apêndice),
  com id, parte, rótulo, item-pai, número de palavras e palavras iniciais.
- **`refs-partN.csv`**: um link por linha:
  - as palavras exatas que viram link e o item em que aparecem;
  - o alvo;
  - a regra que o resolveu (`pattern`, `last-prop` ou `manual`);
  - a situação (`ok`, `check`, `skip` ou `unresolved`) e um trecho de contexto.

  Só as linhas `ok`/`check` com alvo viram link. **Esta é a fonte de verdade
  do que entra no HTML.** O arquivo é regerado pelo `refs.py`, por isso não
  deve ser editado à mão.
- **`overrides.csv`**: as correções manuais, que o `refs.py` aplica ao regerar.
  Colunas: `source`, `text`, `occ` (enésima ocorrência; vazio = todas),
  `action` (`set`, `skip` ou `add`), `target` e `note`. A coluna `note`
  registra o porquê.
- **`ethics-dependencies.xlsx`**: a planilha, gerada a partir dos CSVs. Tem três abas:
  - **Items**: quantas referências cada item faz e recebe;
  - **References**: todos os links;
  - **Dependencies**: por item, o que ele cita e quem o cita.

## Convenções

**Ids:** `p{parte}-{tipo}{n}`.
- Tipos: `def`, `ax`, `post`, `prop`, `emodef` (Definições das Emoções, Parte III).
- Sufixos:
  - `-proof` (`-proof2`… para “Another proof”);
  - `-cor` / `-cor1`, `-cor2`…;
  - `-note` / `-note1`, `-note2`…;
  - `-expl`;
  - `-nb`.
- Casos especiais:
  - Parte II: `p2-ax1-bodies`, `p2-ax2-bodies` (axiomas após a Prop. XIII); `p2-lem1`…`p2-lem7`; `p2-lem3-ax1`…`3` e `p2-lem3-def` (após o Lema III).
  - `p3-emodef-gen`: Definição Geral das Emoções.
  - `p4-app1`…`p4-app32` (capítulos do Apêndice da Parte IV); `p{n}-pref`; `p1-app`.

**Demonstrações e notas depois de um corolário:**
- Uma demonstração logo após um corolário pertence ao corolário (`-cor-proof`).
- Uma nota sem número depois de um corolário pertence à proposição (o
  *Scholium*), a menos que a proposição já tenha nota. Nesse caso é nota do
  corolário (`-cor-note`), como em III. xl., xli., lv. e IV. lxiii.

**“The last Prop.”:**
- Numa demonstração da Prop. n, significa a Prop. n−1.
- Num corolário ou numa nota, é tomado como a própria Prop. n e marcado
  `check` para revisão.

**Pop-up:**
- O texto do pop-up é rótulo + primeiro parágrafo do alvo, sem o numeral
  inicial e sem as marcas de nota de rodapé.
- Em referências entre partes, o rótulo leva a parte (“Part I, Prop. XI. …”).
- **Posição (decisão do usuário em 06/10/2026):** o pop-up entra no fluxo
  e empurra as linhas seguintes para baixo, em vez de cobrir o texto. É
  um float de largura total (`float: left; width: 100%`), que fica abaixo
  da linha da referência sem alterá-la; o `p::after { clear: both }`
  segura o pop-up da última linha dentro do parágrafo. A primeira
  tentativa (`display: block`) piscava no hover: a linha cortada perdia a
  justificação e o link saía de baixo do ponteiro. Descrito no
  `TOOLTIP_TEST_REPORT.md` §3.10; a amostra da variante D em
  `prototypes/` continua com a versão sobreposta.
- **Alvos longos (decisão do usuário em 05/10/2026):**
  - até **200 palavras** no primeiro parágrafo, o alvo aparece inteiro e o
    link tem `aria-describedby` (`FULL_TIP_WORDS = 200` em `build_html.py`);
  - acima disso, o pop-up mostra as primeiras 60 palavras + “…” e o link
    fica **sem** `aria-describedby`, para o leitor de tela não ler uma nota
    inteira no meio da demonstração;
  - nas notas longas e muito citadas, o excerto é escolhido à mão em
    `mapping/excerpts.csv` (colunas `target`, `excerpt`, `note`), mostrando
    a passagem que as citações usam em vez das primeiras palavras. O excerto
    tem de ser um trecho literal do primeiro parágrafo do alvo (o
    `build_html.py` para com erro se não for); ganha “… ” no início e/ou
    “ …” no fim quando não começa ou não termina junto com a nota. Os
    excertos são escolhidos na revisão da parte em que a nota está, lendo
    também as citações vindas das partes seguintes (o `refs.collect(N)`
    permite isso sem gravar nada).
  - Excertos feitos: II. xvii., xviii., xxxv., xliv., xlvii., xlviii. (notas);
    III. xi. nota (as definições de prazer, dor etc.; o resto da nota explica
    III. x.) e III. xxx. nota (sem a frase inicial; tem 206 palavras);
    IV. xxxvii. nota I (as definições de religião, piedade, honra, honesto e
    torpe) e IV. xliv. nota (só o começo; o resto trata da loucura);
    IV. xxxix. nota (as duas primeiras frases, sobre a morte, citadas em
    V. xxxviii. nota) e V. iv. nota (conhecer as emoções e separá-las da
    ideia da causa externa; citada 3 vezes em V. xx. nota).
    As notas da Parte I (I. viii. nota II, I. xv. nota) ficaram com as
    primeiras 60 palavras.
  - Por que essa regra (contagem preliminar, com as Partes II–V ainda não
    revisadas): são cerca de 1.354 links, 203 deles para notas (63 notas
    distintas, de 20 a 812 palavras). Com o limite de 120, seriam cortados
    157 links; com 200, são 110 links para 27 alvos; com 300, 72 links.
  - As citações se concentram em poucas notas longas. São os candidatos a
    excerto manual:

    | Alvo | Palavras | Citações |
    |---|---:|---:|
    | III. xi. nota | 463 | 30 |
    | II. xvii. nota | 400 | 10 |
    | II. xviii. nota | 379 | 6 |
    | III. xxx. nota | 206 | 6 |
    | II. xl. nota I | 674 | 5 |
    | II. xliv. nota | 430 | 5 |
    | II. xlvii. nota | 370 | 5 |

  - O corolário de II. xi. (131 palavras, 17 citações) passa inteiro com o
    limite de 200.
  - Na Parte I, com o limite de 200, a nota da Prop. X (164 palavras)
    aparece inteira; só a nota II da Prop. VIII (439 palavras) é cortada.

**Marcação (só marcação; o texto não muda):**
- HTML 4.01 convertido para HTML5.
- Os títulos ganharam uma hierarquia consistente:
  - as linhas da folha de rosto viraram parágrafos estilizados;
  - as Partes são `h2`;
  - os subtítulos das Partes são `h3`;
  - as seções são `h3` na Parte I e `h4` nas demais.

## Roteiro para cada parte (N = 2…5)

1. `python3 build/refs.py N --residue`: o contador mostra quantas linhas
   são `ok`/`check`/`unresolved`, e o resíduo lista palavras com cara de
   referência que não viraram link.
2. Revisar `unresolved`, `check` e o resíduo, e conferir por amostragem as
   linhas `ok`, sobretudo:
   - “Coroll.” sem número quando há vários corolários;
   - “note” de proposições com mais de uma nota;
   - referências a outras obras (“Principles of the Cartesian Philosophy”);
   - “the same Axiom / Post.”.
3. Registrar cada correção em `overrides.csv`, com o motivo, e rodar o passo
   1 de novo até não sobrar nada `unresolved`.
4. Rodar `build_html.py`, `check_text.py`, os dois validadores e `report.py`.
5. Atualizar a tabela de andamento acima.

## Observações da Parte II, úteis para as próximas

- O tokenizador agora reconhece “Prop. xxviii. of Part i.” e “Ax. i.,
  after (the Coroll. of) Lemma iii.” / “Def. after Lemma iii.” (alvos
  `p2-lem3-ax1..3`, `p2-lem3-def`). Ele **não** reconhece, e o resíduo às
  vezes também não mostra:
  - números arábicos (“i. 15”, “III. 30”, “I. 36”); há casos em III. i.
    e III. xxxiv.;
  - “Lemma I.” com algarismo maiúsculo;
  - “Appendix” (“the Appendix to Part I.”);
  - “the following proposition” e “the last” sem substantivo.
- Na digressão física, “Ax. i.” sozinho nas demonstrações dos lemas é o
  axioma dos corpos (`p2-ax1-bodies`), não II. Ax. i.
- **Esta tradução omite o Corolário de II. xiii.** (“o homem consiste de
  mente e corpo”). As referências a ele (“Coroll. after II. xiii.”) apontam
  para a Prop. XIII, com o motivo no `overrides.csv`.
- “II. xl. note” sem número: Prop. XL tem duas notas. Na Parte II, a
  citação sobre o terceiro gênero de conhecimento é a Nota II. Na Parte III,
  conferido no latim: III. i. → Nota II (o latim diz “scholia”, as duas; a
  Nota II é a das ideias “fragmentarily, confusedly”); III. lv. e III. lvi.
  → Nota I (“scholium I”). IV. xxvii. → Nota II (o latim diz “scholia”; a
  Nota II define a razão, que é ter ideias adequadas).

## Observações da Parte III, úteis para as próximas

- **Texto latino para tirar dúvidas:** `https://www.thelatinlibrary.com/spinoza.ethicaN.html`
  (N = 1…5). Baixar com `curl`, tirar as tags e procurar com `grep`; o
  resumo do WebFetch não é confiável para citações exatas.
- **Erros de impressão na tradução de Elwes**, corrigidos no alvo (o rótulo
  do pop-up mostra o número certo) e registrados no `overrides.csv`:
  - III. i.: “II. xl. Coroll.” → II. xi. Coroll.;
  - III. xix.: “III. xii. note” → III. xiii. nota;
  - Def. das Emoções 34: “xl.” → III. xli. nota (gratidão).
- Nas citações “III. xviii. note” e “III. xxvii. note”, a nota certa depende
  do assunto: esperança e medo estão na Nota II de III. xviii.; compaixão e
  emulação na Nota I de III. xxvii., benevolência na Nota II.
- O tokenizador agora aceita “Ax.i.” sem espaço. Continuam fora dele, e
  entram como `add`: “note II. xvii.” (nota antes do número),
  “Corollary to II. viii.”, “the same Post./Axiom/note”, “the preceding one”,
  “the note appended thereto”, “the next Prop.”.
- Prop. LV tem dois corolários com o mesmo título (“Corollary.”); os ids são
  `p3-prop55-cor` e `p3-prop55-cor2`. Conferir citações a eles nas Partes IV–V.

## Observações da Parte IV, úteis para a Parte V

- **Erro de impressão:** IV. i.: “IV. iii.” → III. iv. (latim: Prop. 4 partis III).
- **Elwes omite muitas citações do latim** (por exemplo, em IV. viii., na nota de
  IV. xviii. e em IV. lxxii.). Só se faz link do que está impresso; não se
  acrescentam referências.
- Quando o latim é mais preciso que Elwes, o alvo segue o latim e o motivo vai
  para o `overrides.csv`: IV. lx. nota, “IV. ix.” → IV. ix. Coroll.; Apêndice
  XIX, “III. xxxi. Coroll.” → III. xxxi. nota.
- “Def. of the Emotions, iv. explanation” e “Explanation xii. and xiii.”
  apontam para as explicações (`p3-emodef4-expl`, `p3-emodef13-expl`).
- “notes. i. and ii.” / “notes. i. ii.”: o tokenizador liga o “ii.” solto a uma
  proposição; tem de ser corrigido à mão (houve dois casos).
- “The last Prop.” / “the foregoing Proposition” num corolário é a própria
  proposição (latim *praecedentem propositionem*); conferido em IV. xxxv. e lxvi.
- O axioma único da Parte IV tem o rótulo “Axiom” (antes “Ax.”, que dava
  “Ax..” no pop-up).
- Entraram como `add`: “the Appendix to Part I.” (`p1-app`), “the foregoing
  preface” / “Preface to this Part” / “the preface to Pt. IV.” (`p4-pref`),
  “IV. Ax.”, “Coroll. I.”, “the foregoing corollary/one”, “the following
  note”, “the same note to III. xi.”, “the note to IV. l.”, “the Corollary to
  IV. lxv.” / “the said IV. lxv.”. A Parte V deve ter casos parecidos
  (“the Appendix to Part IV.”, “the Preface”).
- Ficaram sem link: “(as we showed in Pt. II.)” em IV. lix. nota (vago) e “in
  the following Part” em IV. lxxiii. nota.
- Citações da Parte V às notas longas da Parte IV: IV. xxxvii. nota I já tem
  excerto; IV. xxxix. nota ganhou excerto na revisão da Parte V.

## Observações da Parte V

- **Prefácio:** “I.27” e “I.50.” são artigos das *Paixões da alma* de
  Descartes (latim *articulum 27 partis I passionum animae*); `skip`.
- **“Another Proof”** com P maiúsculo não era reconhecido pelo
  `structure.py`; agora é. Ganharam id próprio `p4-prop37-proof2`,
  `p4-prop51-proof2` e `p4-prop59-proof2` (os links que estavam nesses
  parágrafos só mudaram de item de origem; o `add` “the preface to Pt. IV.”
  passou para `p4-prop59-proof2`). O `LABEL_RE` do `build_html.py` também
  aceita “Another Proof”, para o rótulo não sair duplicado no pop-up. Isso
  permitiu ligar “second proof” em V. iv. nota (latim *II demonstrationem*).
- “The foregoing/preceding Prop.” em corolário ou nota = a própria
  proposição (V. iv. Coroll., V. xvii. Coroll., V. xxxiii. nota). Mas em
  V. xxxiii. nota “the Coroll. of the last Prop.” é V. xxxii. Coroll. (V.
  xxxiii. não tem corolário), e em V. xxxix. nota “the note to the last
  Proposition” é V. xxxviii. nota (latim *in scholio propositionis
  praecedentis*).
- Entraram como `add`: “Def of the Emotions, xxv.” (sem ponto após Def),
  “the same Axiom” (I. Ax. iii.), “The Axiom of Part IV.”.
- Ficaram sem link, por vagos: “as I have shown above” no prefácio, “in Part
  I. I showed in general terms” em V. xxxvi. nota, “in Part IV.” em V. xli.
- Notas longas citadas uma só vez na Parte V ficaram com as primeiras 60
  palavras: III. xxxv. nota (a 1.ª frase já é a definição de ciúme citada) e
  V. x. nota.

## Decisões pendentes

- ~~Notas longas~~: decidido em 05/10/2026 (limite de 200 palavras + excertos manuais); ver “Pop-up”.
- Nome do arquivo final para envio ao PG (hoje `3800-h-tooltips.html`).
- Teste de leitor de tela / EasyReader no livro completo, quando todas as partes estiverem prontas.
