# Spinoza, *Ethics* (PG #3800): referências com pop-up

Edição HTML do *Ethics* (tradução de Elwes) em que as referências internas
("Deff. iii. and v.", "Prop. xv.", "the last Prop.") viram links com
pop-up mostrando o texto citado, sem JavaScript, para envio ao Project
Gutenberg.

## Pastas

```
3800-h.htm              original do PG (entrada; não editar)
3800-h-tooltips.html    livro completo com links e pop-ups (saída gerada)
build/                  scripts do pipeline (Python 3, sem dependências externas
                        exceto report.py, que usa openpyxl)
mapping/                mapeamento das referências
  items.csv               itens numerados e seus ids (gerado)
  refs-partN.csv          links de cada Parte (gerado)
  overrides.csv           correções manuais (editado à mão)
  excerpts.csv            trechos escolhidos para notas longas (editado à mão)
  ethics-dependencies.xlsx  planilha de dependências (gerada)
docs/
  CONVERSION_PLAN.md      plano, andamento e decisões da conversão (português)
  TOOLTIP_TEST_REPORT.md  testes das variantes A–D e acessibilidade (inglês, para o PG)
prototypes/             amostras de teste das variantes (só Parte I, início)
  teste_D_describedby.*   variante D, a adotada
  ebookmaker/             saída e log do ebookmaker do PG para a amostra
```

## Regerar

Na raiz do projeto:

```
python3 build/structure.py
python3 build/refs.py N --residue     # N = 1 a 5
python3 build/build_html.py
python3 build/check_text.py
python3 build/report.py
```

Detalhes e validação: [docs/CONVERSION_PLAN.md](docs/CONVERSION_PLAN.md).
