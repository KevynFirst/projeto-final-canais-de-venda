<!-- CAPA -->

**Kevyn Bezerra Ladislau**

# Loja física, marketplace ou e-commerce próprio? Transição de canais de venda de MEIs e MEs no Brasil entre a pré-pandemia e o cenário de 2025–2026

**2026**

<!-- FOLHA DE ROSTO -->

**Kevyn Bezerra Ladislau**

**Loja física, marketplace ou e-commerce próprio? Transição de canais de venda de MEIs e MEs no Brasil entre a pré-pandemia e o cenário de 2025–2026**

> Artigo técnico desenvolvido como projeto final do curso Profissão: Análise de Dados, da EBAC. O estudo compara a loja física, o marketplace e o e-commerce próprio como canais de venda de microempreendedores individuais e microempresas do varejo brasileiro, com base em dados públicos do IBGE e em um painel simulado e calibrado.

**2026**

<!-- RESUMO -->

## Resumo Executivo

Este artigo técnico investiga quando compensa, para microempreendedores individuais (MEIs) e microempresas (MEs) do varejo brasileiro, vender pela loja física, pelo marketplace, pelo e-commerce próprio ou por uma combinação desses canais, em quatro recortes: pré-pandemia (jan/2018–fev/2020), pandemia (mar/2020–mai/2022), pós-pandemia (jun/2022–dez/2024) e cenário atual (jan/2025–ago/2026). Como não existe série pública mensal de receitas, custos e clientes por canal para esses portes, o estudo combina dados oficiais do IBGE (Pesquisa Mensal de Comércio, Pesquisa Anual de Comércio e IPCA) com um painel simulado, determinístico e calibrado de 2.500 negócios em cinco segmentos, construído com regras tributárias e tarifas verificadas nas fontes. Todos os indicadores são calculados por razão de somas. Nos dados oficiais, a Internet passou de 5,26% para 9,78% da receita do varejo com 20 ou mais pessoas ocupadas entre 2019 e 2024, e o volume de vendas caiu 19,67% entre fevereiro e abril de 2020. No painel, a participação digital na receita real sobe de 10,31% para 33,31%, e a margem líquida recua de 8,15% para 5,44%. A análise custo-volume-lucro aponta o e-commerce próprio como o canal que mais compensa no cenário atual: ele integra a recomendação em 9 das 10 combinações de porte e segmento. O marketplace só o supera abaixo de R$ 1.619,18 por mês no MEI (R$ 11.246,39 na ME), e a loja física, acima de R$ 5.256,34 (R$ 23.443,58 na ME). Recomenda-se uma trajetória híbrida por estágio, válida sob as premissas declaradas.

**Palavras-chave:** canais de venda; microempreendedor individual; marketplace; e-commerce; ponto de equilíbrio.

> **Como citar este trabalho:** LADISLAU, Kevyn Bezerra. **Loja física, marketplace ou e-commerce próprio?**: transição de canais de venda de MEIs e MEs no Brasil entre a pré-pandemia e o cenário de 2025–2026. 2026. Artigo técnico. Disponível em: https://github.com/KevynFirst. Acesso em: 18 out. 2026.

<!-- ABSTRACT -->

## Abstract

This technical article examines when Brazilian retail individual microentrepreneurs (MEIs) and microenterprises (MEs) are better off selling through a physical store, a marketplace, their own e-commerce or a combination of these channels, across four periods: pre-pandemic (Jan 2018–Feb 2020), pandemic (Mar 2020–May 2022), post-pandemic (Jun 2022–Dec 2024) and the current scenario (Jan 2025–Aug 2026). Since no public monthly series of revenue, costs and customers by sales channel exists for these business sizes, the study combines official IBGE data (Monthly Trade Survey, Annual Trade Survey and the IPCA consumer price index) with a deterministic, calibrated simulated panel of 2,500 businesses in five segments, built with tax rules and platform fees verified at the source. All indicators are computed as ratios of sums. In the official data, the Internet share of revenue among retailers with 20 or more persons employed rose from 5.26% to 9.78% between 2019 and 2024, and retail sales volume fell 19.67% between February and April 2020. In the panel, the digital share of real revenue rises from 10.31% to 33.31%, while the net margin falls from 8.15% to 5.44%. The cost-volume-profit analysis points to own e-commerce as the most rewarding channel in the current scenario: it is part of the recommendation in 9 of the 10 size-segment combinations. The marketplace only beats it below BRL 1,619.18 per month for MEIs (BRL 11,246.39 for MEs), and the physical store only above BRL 5,256.34 (BRL 23,443.58 for MEs). A staged hybrid path is recommended, valid under the stated assumptions.

**Keywords:** sales channels; individual microentrepreneur; marketplace; e-commerce; break-even point.

<!-- SUMARIO -->

## Sumário

- 1 Introdução
- 2 Referencial Teórico & Evolução de Mercado
    - 2.1 Canais de venda, plataformas e valor do cliente
    - 2.2 Pré-pandemia (jan/2018–fev/2020)
    - 2.3 Pandemia (mar/2020–mai/2022)
    - 2.4 Pós-pandemia (jun/2022–dez/2024) e Cenário Atual (jan/2025–ago/2026)
    - 2.5 Tributação do MEI e da ME
- 3 Metodologia de Dados & Matriz de Variáveis
    - 3.1 Natureza da pesquisa e fluxo quali-quanti
    - 3.2 Fontes de dados
    - 3.3 Arquitetura do pipeline
    - 3.4 Modelo do painel simulado
    - 3.5 Matriz de variáveis
    - 3.6 Fórmulas dos indicadores
    - 3.7 Premissas e calibração
    - 3.8 Qualidade dos dados
    - 3.9 Limitações
- 4 Resultados e Discussão
    - 4.1 Contexto real: consumo, inflação e Internet no varejo
    - 4.2 Transição da receita e participação dos canais
    - 4.3 Custos e margens
    - 4.4 Clientes e economia unitária
    - 4.5 Taxa de intermediação do marketplace e custo de aquisição do canal próprio
    - 4.6 Ponto de equilíbrio e receitas de indiferença
    - 4.7 Calibração e robustez
    - 4.8 Discussão: o que os dados sustentam e o que é premissa
- 5 Conclusão e Recomendação Estratégica
- Referências

## 1 Introdução

Para quem vende no varejo como microempreendedor individual (MEI) ou como microempresa (ME), escolher o canal de venda é uma decisão de alocação de capital escasso. A loja física exige aluguel e estrutura, mas recebe o cliente que passa pela porta sem custo de mídia. O marketplace oferece audiência imediata e cobra por isso uma comissão sobre cada venda, mantendo o relacionamento com o comprador dentro da plataforma. O e-commerce próprio, que neste estudo reúne a loja virtual em plataforma por assinatura e a venda por redes sociais e WhatsApp com *checkout* ou link de pagamento próprio, dispensa a comissão, mas obriga o negócio a pagar pela atenção do cliente com anúncios, frete e relacionamento. Cada canal desloca o custo para uma linha diferente do resultado, e uma escolha errada pesa muito para quem trabalha com margens de um dígito.

A pandemia de COVID-19 transformou essa escolha em urgência. Entre fevereiro e abril de 2020, o volume de vendas do varejo brasileiro caiu 19,67%, e o de tecidos, vestuário e calçados, 79,51% (IBGE, 2026d). Segundo o Sebrae, vender pela internet foi um dos caminhos de cerca de 70% dos donos de pequenos negócios para atravessar a crise (SEBRAE, 2021), muitas vezes sem tempo de comparar o que cada canal custava e devolvia.

Passada a emergência sanitária, o tema continua atual. Em 2025–2026, o Pix está disponível nos checkouts próprios com tarifa bem menor que a do cartão (NUVEMSHOP, [2026]), o TikTok Shop passou a operar no país (TIKTOK, 2025), as compras internacionais de pequeno valor passaram a pagar imposto de importação de 20% (BRASIL, 2024) e as plataformas seguem revendo tarifas, como a Shopee, que elevou de R$ 4,00 para R$ 4,50 a parcela fixa por item de até R$ 79,99 em outubro de 2026 (SHOPEE, 2026b). A dúvida do microempreendedor permanece: manter o ponto físico, concentrar-se no marketplace, investir na própria loja virtual ou combinar canais?

O recorte em MEIs e MEs não é apenas de tamanho. A Lei Complementar nº 123/2006 limita a receita bruta anual do MEI a R$ 81.000,00 e a da ME a R$ 360.000,00 (BRASIL, 2006), com o teto atual do MEI em vigor desde 2018 (BRASIL, 2016). O MEI paga um valor fixo mensal de tributos, e a ME recolhe o Simples Nacional sobre a receita, o que muda a estrutura de custos e, como se verá, a resposta sobre o melhor canal. Além disso, o teto do MEI não é corrigido pela inflação: com IPCA acumulado de 55,26% entre jan/2018 e ago/2026, os R$ 81 mil de hoje compram o que R$ 52.171,26 compravam em dez/2017 (IBGE, 2026a). Com menos espaço para crescer dentro do regime, extrair mais margem de cada real vendido ficou mais importante.

Falta, porém, evidência pública para orientar essa escolha. A Pesquisa Mensal de Comércio (PMC) do IBGE investiga empresas com 20 ou mais pessoas ocupadas (IBGE, 2026c), e as tabelas da Pesquisa Anual de Comércio (PAC) sobre formas de comercialização descrevem o mesmo estrato (IBGE, 2026b). O levantamento do Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC) com notas fiscais mostra o crescimento das vendas on-line de micro e pequenas empresas, mas não suas margens por canal (BRASIL, 2025). Como não existe série mensal de receita, custos e clientes por canal para MEIs e MEs, este trabalho constrói um painel simulado, calibrado e auditável, dirigido por dados oficiais e regras verificadas, e deixa explícito, em cada resultado, o que é dado oficial e o que é premissa.

A pergunta de pesquisa que orienta o estudo é a seguinte: sob quais condições de escala de receita, margem, taxa de intermediação (*take rate*), custo de aquisição de clientes (CAC) e retenção a loja física, o marketplace, o e-commerce próprio ou uma combinação deles maximiza o resultado de MEIs e MEs do varejo, e como essa resposta mudou entre a pré-pandemia e o cenário de 2025–2026?

O objetivo geral é oferecer ao microempreendedor um critério quantitativo, expresso em faturamento mensal por negócio, para escolher e combinar canais de venda. Os objetivos específicos correspondem às etapas da análise. O primeiro é descrever o comportamento do consumidor e as regras de mercado em cada fase, porque nenhuma comparação de canais faz sentido fora do contexto em que o consumidor compra e paga. O segundo é construir um *pipeline* reprodutível que integre os dados oficiais a um painel simulado e calibrado, já que as estatísticas públicas não respondem sozinhas à pergunta. O terceiro é calcular, por razão de somas, ticket médio, CAC, taxa de intermediação, margens, retenção, valor do cliente no tempo de vida (LTV) e ponto de equilíbrio por canal, porte, segmento e fase. O quarto é estimar as receitas de indiferença entre canais, os faturamentos em que dois canais deixam a mesma margem, e convertê-las em uma recomendação por estágio do negócio.

A contribuição é dupla: no método, mostra como responder a uma pergunta de negócio sem dado direto, com uma simulação calibrada e separada dos fatos oficiais; na prática, entrega limiares em reais por mês que o empreendedor pode comparar com o próprio faturamento. Como projeto final do curso Profissão: Análise de Dados, da EBAC, o trabalho também documenta o ciclo completo de um projeto de dados, da extração à recomendação. O texto segue com o referencial teórico (seção 2), a metodologia (seção 3), os resultados (seção 4) e a conclusão (seção 5).

## 2 Referencial Teórico & Evolução de Mercado

Esta seção reúne os conceitos usados para comparar canais e descreve, fase a fase, como mudaram o consumidor, as plataformas e as regras do micro varejo. Os números aqui são oficiais ou de fontes de mercado verificadas; os resultados do painel aparecem na seção 4.

### 2.1 Canais de venda, plataformas e valor do cliente

O estudo adota três canais, definidos pelo canal principal de cada negócio. A Loja Física é o ponto de venda presencial (loja, box, quiosque ou feira). O Marketplace é a plataforma de terceiros que intermedia a venda mediante comissão; o Mercado Livre é a referência da série histórica de tarifas, e Shopee e Amazon entram na comparação de 2026. O E-commerce Próprio reúne os canais digitais sem comissão de intermediação, da loja virtual por assinatura à venda por redes sociais ou WhatsApp com link de pagamento próprio, agrupados porque têm a mesma economia: não pagam comissão, mas precisam atrair o cliente com recursos próprios.

A diferença econômica entre os canais está na forma como cada um transforma receita em custo. Na loja física, a maior parte do custo é fixa (aluguel, energia, sistema de caixa e, na ME, ao menos um funcionário), mas o custo de atrair o cliente de passagem já está no aluguel, o que explica o marketing baixo. No marketplace, o custo fixo é pequeno, e a plataforma retém uma fração de cada venda: a taxa de intermediação, ou take rate, igual a comissões e tarifas divididas pela receita bruta. No canal próprio, a tarifa se limita ao pagamento e à plataforma, e o negócio arca com o custo de aquisição de clientes (CAC), o investimento em marketing dividido pelo número de clientes novos, além do frete que decide subsidiar.

Comparar uma comissão com um gasto em anúncios exige uma régua comum, oferecida pelo conceito de valor do cliente. Gupta, Lehmann e Stuart (2004) definem esse valor como a soma esperada dos resultados futuros que o cliente gera, descontados no tempo, e mostram, com dados públicos de cinco empresas, que melhorar a retenção em 1% eleva o valor da empresa em cerca de 5%, contra 1% para a mesma melhora na margem e 0,1% no custo de aquisição. Berger e Nasr (1998) sistematizam modelos de valor do cliente no tempo de vida (*customer lifetime value*, LTV) e suas aplicações em marketing. A mensagem comum é que um cliente caro pode compensar se voltar a comprar, e um barato pode não compensar se não voltar.

Com retenção mensal r constante e sem desconto financeiro, simplificação adotada aqui por se tratar de relações de poucos meses, o LTV reduz-se à margem de contribuição mensal do cliente multiplicada por 1 ÷ (1 − r), fator que representa o tempo de vida esperado em meses: cerca de 1,43 mês com retenção de 30% e 1,11 mês com 10%. A razão LTV/CAC indica quantas vezes o cliente devolve, em margem, o que custou, e o *payback* do CAC, em quantos meses isso ocorre. A razão 3 serve aqui apenas como referência visual, e não como meta.

O último elemento é a análise custo-volume-lucro, que compara canais pela estrutura de custos, e não só pelo resultado médio. Se v é o custo variável por real vendido (mercadoria, comissões, frete, impostos sobre a receita e marketing) e F é o custo fixo mensal por negócio, a margem mensal de um canal vale R × (1 − v) − F, em que R é a receita mensal por negócio, e o ponto de equilíbrio é PE = F ÷ (1 − v). Dois canais A e B empatam na receita de indiferença R\* = (F_A − F_B) ÷ (v_B − v_A): abaixo dela vence o canal de menor custo fixo; acima, o de menor custo variável. Como o marketplace troca custo fixo por variável e a loja física faz o inverso, a escala de faturamento decide qual estrutura compensa.

### 2.2 Pré-pandemia (jan/2018–fev/2020)

A primeira fase começa com a Lei Complementar nº 155/2016, que elevou o teto do MEI para R$ 81.000,00 e reorganizou o Anexo I do Simples Nacional a partir de 1º de janeiro de 2018 (BRASIL, 2016). O consumo estava estável: o volume da PMC com ajuste sazonal oscilou entre 92,90 e 99,61 (2022 = 100) em 2018 e 2019 e estava em 98,13 em fevereiro de 2020 (IBGE, 2026d), com IPCA em 12 meses de 3,75% em dezembro de 2018 e de 4,31% em dezembro de 2019 (IBGE, 2026a).

O comércio eletrônico ocupava pouco espaço mesmo entre as empresas maiores: em 2019, a Internet respondeu por 5,26% da receita de revenda do varejo com 20 ou mais pessoas ocupadas, ou R$ 67,79 bilhões, e 1.888 empresas desse estrato vendiam por esse meio (IBGE, 2026b). A compra on-line era concentrada, com 29,67% da receita via Internet em 32 empresas do comércio não especializado sem predominância de produtos alimentícios. Entre os segmentos com dado divulgado, a Internet pesava 9,45% em Casa, 4,33% em Alimentos e 2,78% em Beleza; em Moda e Eletrônicos, havia parcela sob sigilo estatístico.

O marketplace de referência cobrava 11% por venda no anúncio Clássico até junho de 2018 e, a partir de julho, passou a acrescentar R$ 5,00 por unidade abaixo de R$ 120, segundo cópias arquivadas da página oficial (MERCADO LIVRE, [2026]). O consumidor pagava com cartão ou boleto, pois o Pix só surgiria em novembro de 2020 (OLIVEIRA, 2020). Ao menos entre as empresas maiores, as únicas medidas pela PAC, o digital era complemento da venda presencial.

### 2.3 Pandemia (mar/2020–mai/2022)

O recorte da Pandemia começa em março de 2020, mês em que a Organização Mundial da Saúde (OMS) caracterizou a COVID-19 como pandemia, em 11/03/2020 (ORGANIZAÇÃO PAN-AMERICANA DA SAÚDE, 2020). A Emergência em Saúde Pública de Importância Nacional (ESPIN) já vigorava desde 04/02/2020, pela Portaria GM/MS nº 188/2020 (BRASIL, 2020), revogada pela Portaria GM/MS nº 913/2022 (BRASIL, 2022), mas fevereiro de 2020 ainda não mostra choque de consumo na PMC e serve de base pré-choque. O fim é maio de 2022, último mês em que a ESPIN vigorou na maior parte dos dias (até 21/05), pois a Portaria GM/MS nº 913/2022 produziu efeitos em 22/05/2022.

O choque foi imediato e desigual. O volume de vendas do varejo com ajuste sazonal caiu de 98,13 em fevereiro para 78,83 em abril de 2020, queda de 19,67% e ponto mais baixo da série (IBGE, 2026d). Na série sem ajuste por atividade, a queda entre fevereiro e abril foi de 79,51% em tecidos, vestuário e calçados, 41,56% em informática e comunicação, 40,39% em móveis e eletrodomésticos e 11,61% em artigos farmacêuticos e de perfumaria, enquanto supermercados e alimentos cresceram 3,49%. A recuperação foi rápida, com o índice em 104,57 em outubro de 2020, e a desigualdade entre atividades é central para o estudo, porque os segmentos do painel herdam esses choques.

A resposta dos pequenos negócios foi a migração para o digital. A 11ª edição da pesquisa do Sebrae com a FGV sobre o impacto da pandemia indicou que mais da metade do faturamento vinha da internet para um terço dos MEIs que vendiam on-line, contra 22% entre os donos de micro e pequenas empresas (SEBRAE, 2021). Outra edição da pesquisa, citada na mesma fonte, apontou o WhatsApp como canal de 84% dos negócios digitalizados, seguido de Instagram (54%) e Facebook (51%), com apenas 23% vendendo por site próprio. O canal próprio do micro varejo se parece, portanto, mais com conversa e link de pagamento do que com loja virtual estruturada, o que justifica agrupar as duas formas.

Em 16 de novembro de 2020, o Pix entrou em funcionamento pleno, com 734 instituições (OLIVEIRA, 2020), e abriu ao lojista uma alternativa de recebimento mais barata que o cartão, como mostram as tarifas atuais (seção 2.4). Na PAC, a Internet subiu para 8,36% da receita do varejo com 20 ou mais pessoas ocupadas em 2020 e 9,84% em 2021, com 2.768 e 3.100 empresas vendendo pela rede (IBGE, 2026b). Único ano com os cinco segmentos sem sigilo, 2021 serve de retrato da intensidade digital: 44,88% em Eletrônicos, 19,63% em Casa, 14,60% em Moda, 5,85% em Beleza e 4,84% em Alimentos, ordem que orienta a calibração do painel (seção 3.4).

Na segunda metade da fase, a inflação acelerou: o IPCA em 12 meses foi de 4,52% em dezembro de 2020 para 10,06% em dezembro de 2021 e 12,13% em abril de 2022 (IBGE, 2026a). O marketplace de referência passou a cobrar comissão por categoria e reduziu o limite da tarifa fixa de R$ 5,00 para produtos abaixo de R$ 99, em outubro de 2020, e de R$ 79, em abril de 2021 (MERCADO LIVRE, [2026]).

### 2.4 Pós-pandemia (jun/2022–dez/2024) e Cenário Atual (jan/2025–ago/2026)

Depois da emergência sanitária, o digital não devolveu o espaço conquistado nem manteve o ritmo do choque. Na PAC, a Internet ficou em 9,11% da receita em 2022, 8,77% em 2023 e 9,78% em 2024, este já na série nova da pesquisa, com quebra de comparabilidade (IBGE, 2026b). A receita do varejo via Internet chegou a R$ 217,91 bilhões em 2024, 3,21 vezes a de 2019, com 3.850 empresas vendendo pela rede, e a concentração seguiu alta: 63 empresas de lojas de departamento e comércio não especializado via Internet detinham 35,52% da receita on-line, numa classificação diferente da usada até 2023.

Para as micro e pequenas empresas, o dado mais próximo vem do levantamento do MDIC com notas fiscais da Receita Federal, que traz um recorte das optantes do Simples Nacional: suas vendas on-line passaram de R$ 5 bilhões em 2019 para R$ 67 bilhões em 2024, alta próxima de 1.200%, contra 220% nas empresas de médio e grande porte, que foram de R$ 49 bilhões para R$ 158 bilhões (BRASIL, 2025). O comércio eletrônico com nota fiscal somou R$ 225 bilhões em 2024, 30% deles vindos das micro e pequenas empresas, grupo em que cresceu 76,3% entre 2022 e 2024. Como a fonte mede vendas com nota fiscal, parte do crescimento pode refletir maior formalização da emissão, hipótese que os dados disponíveis não permitem testar.

A oferta de canais também se multiplicou. O Sebrae mapeou 157 marketplaces em 18 segmentos (JOVCHELEVICH, 2024), e a 9ª edição da pesquisa Pulso dos Pequenos Negócios indicou que 70% dos pequenos negócios já usam canais digitais para vender (GOMES, 2025). Em 8 de maio de 2025, o TikTok Shop começou a operar no Brasil, trazendo a compra por descoberta para dentro de uma rede social (TIKTOK, 2025). No comércio internacional, a Lei nº 14.902/2024 fixou o imposto de importação do regime simplificado em 20% até US$ 50 e em 60% entre US$ 50,01 e US$ 3.000, com parcela a deduzir de US$ 20 (BRASIL, 2024), regra somada ao Programa Remessa Conforme, em que as empresas certificadas recolhem os tributos na compra (BRASIL, [2026]); ambas alteram a comparação de preço entre o produto nacional e o importado de baixo valor.

As tarifas também ficaram mais complexas. No Mercado Livre, o custo fixo por unidade abaixo de R$ 79 subiu para R$ 5,50 em março de 2023 e para R$ 6,00 em janeiro de 2024, com comissão de 10% a 14% no anúncio Clássico e de 15% a 19% no Premium (MERCADO LIVRE, [2026]). Na Shopee, vendedores com CNPJ pagam, em 2026, 20% mais R$ 4,50 por item de até R$ 79,99 e 14% mais R$ 16, R$ 20 ou R$ 26 nas faixas superiores, com taxa de transação e frete grátis incluídos; o subsídio Pix de 5% a 8% é desconto ao comprador custeado pela plataforma e não reduz o valor recebido pelo vendedor (SHOPEE, 2026a, 2026b). A Amazon cobra de 10% a 15% de comissão, mais R$ 2,00 por produto no plano Individual ou R$ 19,00 mensais a partir do 13º mês no Profissional (AMAZON, [2026]). No canal próprio, o plano Essencial da Nuvemshop custa R$ 69 por mês, sem comissão por venda com o meio de pagamento da plataforma, que cobra 4,19% no cartão e 0,99% no Pix (NUVEMSHOP, [2026]).

A inflação desacelerou, com IPCA em 12 meses de 5,78% em dezembro de 2022, 4,62% em 2023, 4,83% em 2024 e 4,26% em 2025, mas o acumulado de jan/2018 a ago/2026 chegou a 55,26% (IBGE, 2026a); manter o poder de compra de dezembro de 2017 exigiria um teto do MEI de R$ 125.758,90. O volume do varejo fechou agosto de 2026 em 108,69 (2022 = 100), depois do pico de 110,14 em março (IBGE, 2026d). O Quadro 1 resume o comportamento do consumidor nas três fases.

**Quadro 1 – Comportamento do consumidor nas três fases**

| Dimensão | Pré-pandemia (jan/2018–fev/2020) | Pandemia (mar/2020–mai/2022) | Pós-pandemia e Cenário Atual (jun/2022–ago/2026) |
|---|---|---|---|
| Onde compra | Internet = 5,26% da receita de revenda do varejo com 20 ou mais pessoas ocupadas em 2019 (IBGE, 2026b) | 8,36% em 2020 e 9,84% em 2021; cerca de 70% dos donos de pequenos negócios recorreram à venda pela internet (IBGE, 2026b; SEBRAE, 2021) | 9,11% (2022), 8,77% (2023) e 9,78% (2024, série nova); micro e pequenas empresas com R$ 67 bilhões vendidos pela internet em 2024, ante R$ 5 bilhões em 2019 (IBGE, 2026b; BRASIL, 2025) |
| Como paga | cartão e boleto; o Pix só entraria em funcionamento em novembro de 2020 (OLIVEIRA, 2020) | Pix em funcionamento pleno desde 16/11/2020, com 734 instituições (OLIVEIRA, 2020) | Pix no checkout próprio a 0,99%, contra 4,19% no cartão do plano Essencial da Nuvemshop (NUVEMSHOP, [2026]) |
| Intensidade de consumo | volume do varejo entre 92,90 e 99,61 (2022 = 100) em 2018–2019 e de 98,13 em fev/2020 (IBGE, 2026d) | volume do varejo −19,67% e de vestuário −79,51% entre fev e abr/2020 (IBGE, 2026d) | volume em 108,69 em ago/2026, depois do pico de 110,14 em mar/2026 (IBGE, 2026d) |
| Canais de descoberta | compra on-line concentrada: 32 empresas do comércio não especializado com 29,67% da receita via Internet em 2019 (IBGE, 2026b) | WhatsApp (84%), Instagram (54%) e Facebook (51%) como canais de venda dos pequenos negócios; só 23% vendiam por site próprio (SEBRAE, 2021) | 157 marketplaces mapeados (JOVCHELEVICH, 2024); TikTok Shop desde 08/05/2025 (TIKTOK, 2025); 63 empresas com 35,52% da receita on-line do varejo em 2024 (IBGE, 2026b) |
| Sensibilidade a preço | IPCA em 12 meses de 3,75% (dez/2018) e de 4,31% (dez/2019) (IBGE, 2026a) | 10,06% em dez/2021 e pico de 12,13% em abr/2022 (IBGE, 2026a) | de 5,78% (dez/2022) a 4,26% (dez/2025); acumulado de 55,26% entre jan/2018 e ago/2026; imposto de importação de 20% até US$ 50 no regime simplificado (IBGE, 2026a; BRASIL, 2024) |

Fonte: elaborado pelo autor com base nas fontes indicadas em cada célula.

O quadro mostra três consumidores diferentes. Na pré-pandemia, o comprador usava a internet sobretudo em grandes varejistas generalistas e pagava com cartão ou boleto. Na pandemia, foi empurrado para o digital, com o WhatsApp como ponte com o pequeno negócio e o Pix mudando a forma de pagar. Depois, o uso do digital estabilizou-se em patamar mais alto, as plataformas se multiplicaram, a descoberta passou também pelas redes sociais e a compra acontece com preços 55,26% mais altos que no fim de 2017.

### 2.5 Tributação do MEI e da ME

O MEI do comércio recolhe mensalmente um valor fixo pelo Documento de Arrecadação do Simples Nacional (DAS): 5% do salário mínimo de contribuição previdenciária (BRASIL, 1991) mais R$ 1,00 de ICMS (BRASIL, 2006). Com salário mínimo de R$ 1.621 em 2026 (INSTITUTO DE PESQUISA ECONÔMICA APLICADA, 2026), o DAS é de R$ 82,05 por mês, contra R$ 48,70 em 2018, quando o mínimo era de R$ 954; a alta de 68,48% supera o IPCA acumulado de 55,26% no período. O MEI pode ter um único empregado, com um salário mínimo ou o piso da categoria (BRASIL, 2006). Para a análise de canais, o ponto central é que o imposto do MEI é custo fixo e entra no termo F.

A ME do comércio recolhe o Simples Nacional pelo Anexo I da Lei Complementar nº 123/2006, cuja tabela vigora desde 1º/01/2018 (BRASIL, 2006, 2016). A alíquota efetiva é (RBT12 × alíquota nominal − parcela a deduzir) ÷ RBT12, em que RBT12 é a receita bruta dos 12 meses anteriores. Até R$ 180.000,00, a alíquota é de 4,00%; na faixa seguinte, até R$ 360.000,00, a nominal é de 7,30%, com parcela a deduzir de R$ 5.940,00. Uma ME com RBT12 de R$ 240.000,00 paga (240.000 × 7,30% − 5.940) ÷ 240.000 = 4,825% da receita, e uma ME no teto, 5,65%. Como as faixas são nominais e permanecem as mesmas desde 2018 no texto consultado, o crescimento nominal da receita eleva a alíquota efetiva. O imposto da ME é, portanto, custo variável e entra no termo v.

## 3 Metodologia de Dados & Matriz de Variáveis

Esta seção descreve como a pergunta foi transformada em dados e indicadores, na ordem do raciocínio: natureza da pesquisa, fontes, pipeline, modelo do painel e, por fim, variáveis, fórmulas, premissas, qualidade dos dados e limitações.

### 3.1 Natureza da pesquisa e fluxo quali-quanti

A pesquisa é aplicada, descritiva e exploratória, com abordagem quali-quanti. A etapa qualitativa é documental: levanta legislação, tarifas das plataformas, marcos sanitários e econômicos e evidências sobre o consumidor, em fontes abertas verificadas na data da extração, 18/10/2026, e produz dois insumos, as regras do modelo (teto do MEI, DAS, Anexo I e tarifas) e as referências de calibração (PAC, MDIC e Sebrae). A etapa quantitativa combina as séries oficiais do IBGE com o painel simulado. O fluxo tem cinco passos encadeados: o levantamento documental define regras e referências; as séries oficiais são extraídas e guardadas; o painel é simulado a partir delas; calculam-se indicadores, pontos de equilíbrio e receitas de indiferença; e seis checagens de calibração confrontam o painel com as referências qualitativas. Esse retorno ao ponto de partida dá credibilidade ao painel, porque uma checagem que falhe gera alerta e permite rever a premissa sem esconder a divergência.

### 3.2 Fontes de dados

A Tabela 1 resume as fontes e a natureza de cada informação, distinção mantida em todo o artigo para que o leitor saiba o que é fato e o que depende de premissa.

**Tabela 1 – Fontes de dados e natureza de cada informação**

| Fonte | Conteúdo usado | Natureza | Período |
|---|---|---|---|
| IBGE – PMC, tabela 8880 | índice de volume de vendas do varejo com ajuste sazonal (2022 = 100) | oficial (contexto e calibração) | dez/2017 a ago/2026 |
| IBGE – PMC, tabela 8882 | índices de volume e de receita nominal de cinco atividades, sem ajuste sazonal | oficial (direcionador do painel) | dez/2017 a ago/2026 |
| IBGE – PAC, tabelas 9349 e 10656 | receita de revenda e número de empresas por forma de comercialização, com destaque para a Internet | oficial (contexto e calibração) | 2019 a 2023 e 2024 (série nova) |
| IBGE – PAC, tabela 10645 | relação entre custo das mercadorias vendidas e receita por classe de atividade | oficial (parâmetro) | 2024 |
| IBGE – IPCA, tabela 1737 | variação mensal do IPCA | oficial (usada na execução) | jan/2018 a set/2026 |
| BCB – SGS, série 433 | variação mensal do IPCA (fonte primária configurada) | oficial (indisponível na extração) | não se aplica |
| Legislação e Ipeadata | tetos do MEI e da ME, DAS, Anexo I do Simples Nacional e salário mínimo | regra oficial | 2018 a 2026 |
| Mercado Livre, Shopee, Amazon e Nuvemshop | comissões, tarifas fixas, planos e processamento de pagamento | regra de mercado | Mercado Livre de 2018 a 2024; demais em out/2026 |
| Painel simulado do projeto | 3.120 linhas no grão mês × canal × porte × segmento | simulado e calibrado | jan/2018 a ago/2026 |

Fonte: elaborado pelo autor com base em IBGE (2026a, 2026b, 2026d), Brasil (1991, 2006, 2016) e nas páginas oficiais das plataformas.

A série 433 do Sistema Gerenciador de Séries Temporais do Banco Central é a fonte primária configurada para o IPCA, mas, na extração, respondeu com uma página de erro; o pipeline usou então, automaticamente, a tabela 1737 do SIDRA, do próprio IBGE, e registrou a fonte efetiva em todas as saídas. Cada resposta foi gravada com data, hora e código de verificação SHA-256, às 20h36 e às 20h37 de 18/10/2026. Essas cópias datadas, os *snapshots*, permitem repetir a análise sem rede e conferir que os arquivos não mudaram.

Algumas fontes foram avaliadas e descartadas: os relatórios de Neotrust/Confi, NielsenIQ Ebit (Webshoppers) e ClearSale, proprietários ou mediante cadastro, sem número verificável obtido; a Associação Brasileira de Comércio Eletrônico (ABComm), sem série pública verificável na data da extração; a contagem oficial de MEIs, disponível apenas em aplicação web sem interface estável de dados; e os dados abertos do Pix no Banco Central, cuja filtragem mensal falhou no teste, razão pela qual o marco do Pix vem da Agência Brasil.

### 3.3 Arquitetura do pipeline

O pipeline foi escrito em Python 3.13, com pandas, NumPy, Matplotlib, seaborn e requests, é orquestrado pelo arquivo `main.py` e foi dividido em cinco módulos, para que um erro em uma etapa não contamine as demais e cada controle tenha um responsável claro no código (Quadro 2). A execução padrão, `python main.py`, lê apenas os snapshots e funciona sem rede; `python main.py --atualizar` consulta de novo as fontes.

**Quadro 2 – Arquitetura do pipeline de dados**

| Etapa | Módulo | O que faz | Controles principais |
|---|---|---|---|
| 1. Extração | `src/extracao.py` | consulta as APIs do IBGE (PMC 8880 e 8882, PAC 9349 e 10656, IPCA 1737) e do Banco Central (SGS 433), grava snapshots datados e simula o painel de canais, exportado como arquivo bruto com problemas de qualidade | até três tentativas por requisição; validação de formato; código SHA-256; uso do snapshot anterior em caso de falha; sementes fixas |
| 2. Limpeza | `src/limpeza.py` | converte os sinais convencionais do IBGE, aplica soma estrita na PAC, padroniza rótulos, datas e números, remove duplicatas e imputa ausentes por razão | conferência com o gabarito da injeção; relatório de qualidade antes e depois |
| 3. Tratamento | `src/tratamento.py` | cria fases e recortes, integra PMC e IPCA e calcula medidas derivadas e indicadores | faixas de sanidade linha a linha; tetos legais do MEI e da ME; identidades de clientes |
| 4. Transformação | `src/transformacao.py` | agrega por razão de somas, monta as 14 tabelas de apoio e exporta o arquivo final | grão único e completo; ausência de nulos; tipos conferidos após a gravação |
| 5. Visualização | `src/visualizacao.py` | produz os 10 gráficos com rodapé de fonte | cores fixas por canal; médias móveis por razão de somas |

Fonte: elaborado pelo autor.

As saídas são o arquivo `data/processed/dados_processados_canais_vendas.csv`, com 3.120 linhas e 59 colunas no grão mês × canal × porte × segmento, em formato longo; 14 tabelas de apoio em `outputs/tabelas/`; 10 gráficos em `outputs/graficos/`; e o relatório `outputs/relatorio_qualidade_dados.json`. Todos os números da seção 4 foram lidos dessas tabelas.

### 3.4 Modelo do painel simulado

O painel é um conjunto de dados em painel, ou seja, a mesma grade de combinações observada mês a mês, com 2.500 negócios sintéticos: 400 MEIs e 100 MEs em cada um dos cinco segmentos (Moda e Acessórios; Casa e Decoração; Eletrônicos e Acessórios; Beleza e Cuidados Pessoais; Alimentos e Bebidas). Cada negócio tem um canal principal, e a transição é modelada como migração de negócios entre canais, definida por âncoras temporais interpoladas: no MEI, o marketplace passa de 7% dos negócios em dez/2017 para 28% em ago/2026, e o canal próprio, de 5% para 14%; na ME, de 6% para 21% e de 4% para 13%. Multiplicadores por segmento reproduzem a ordem da intensidade digital na PAC, com Eletrônicos muito acima de Casa e Moda, que superam Beleza e Alimentos.

A receita mensal de cada combinação é o produto do número de negócios, da receita média de referência de 2019, de um fator do canal (negócios digitais começam menores), de um direcionador do segmento e de um impulso digital, com ruído aleatório de 5%. O direcionador vem da PMC por atividade: o volume sem ajuste sazonal preserva a sazonalidade e os choques reais, depois de removida a tendência de longo prazo das grandes redes, estimada por regressão do logaritmo do volume com ajuste contra o tempo nos meses fora da pandemia. Sem essa remoção, a expansão das empresas grandes seria atribuída aos microempreendedores e levaria parte deles acima do teto legal. O volume é multiplicado pelo preço implícito da atividade (receita nominal ÷ volume), para que o ticket acompanhe os preços do setor, e o impulso digital vale 1,00 até fev/2020, 1,70 em abr/2020 e volta a 1,00 em dez/2022.

Os pedidos resultam da receita dividida pelo ticket; os clientes ativos, da frequência de compra; e os recorrentes, da retenção aplicada aos clientes do mês anterior, de 32% na loja física, 10% no marketplace e de 20% a 30% no canal próprio, com ajustes por segmento e um choque de −10 pontos na loja física entre abr e jun/2020. Os demais são clientes novos, que multiplicam o CAC. A construção garante, em toda linha, que os ativos sejam a soma de novos e recorrentes e que haja ao menos um cliente novo, para que o CAC tenha denominador.

As comissões do marketplace seguem as regras históricas do Mercado Livre, com a tarifa fixa aplicada só à fração estimada de pedidos abaixo do limite de cada época (valores de pedido com distribuição lognormal), porque aplicá-la ao ticket médio criaria saltos artificiais. O canal próprio paga 4,5% de processamento até out/2020 e, depois, uma média entre cartão (4,19%) e Pix (0,99%) ponderada pela adoção do Pix; a loja física paga 2,2% de cartão sobre a parcela não paga com Pix. O CMV segue a relação com a receita da PAC 2024 por segmento; custos fixos, frete e CAC são corrigidos pelo IPCA, e o CAC digital tem ainda alta real de 2% ao ano no marketplace e de 3% no canal próprio. O MEI paga o DAS do mês, e a ME, o Simples pela alíquota efetiva do RBT12. A receita anual por negócio nunca passa de R$ 81 mil no MEI nem de R$ 360 mil na ME, e uma violação interromperia o pipeline.

Os recortes seguem os marcos da seção 2.3: Pré-pandemia de jan/2018 a fev/2020, com fev/2020 como base pré-choque, embora a ESPIN vigorasse desde 04/02/2020; Pandemia de mar/2020, mês da caracterização pela OMS, a mai/2022, último mês com ESPIN na maior parte dos dias, antes dos efeitos da Portaria GM/MS nº 913/2022 em 22/05/2022; Pós-pandemia de jun/2022 a dez/2024; e Cenário Atual de jan/2025 a ago/2026, último mês com PMC e IPCA. A simulação é determinística: a semente 2026 gera o painel, e a 2027, os problemas de qualidade do arquivo bruto (seção 3.8).

### 3.5 Matriz de variáveis

O arquivo final tem 59 colunas, agrupadas na Tabela 2. As medidas (receitas, pedidos, clientes e custos) vêm do painel e são aditivas, isto é, podem ser somadas em qualquer agregação; os indicadores derivam delas e não podem ser somados nem promediados; as colunas da PMC e do IPCA são dados oficiais repetidos em cada linha do mês.

**Tabela 2 – Matriz de variáveis do arquivo final**

| Variável (coluna) | Tipo | Unidade | Origem | Papel na análise |
|---|---|---|---|---|
| `data`, `ano`, `mes`, `ano_mes`, `trimestre` | data, inteiro e texto | mês (AAAA-MM-01) | calendário | eixo temporal |
| `fase`, `recorte_temporal`, `flag_cenario_atual` e colunas de ordenação | texto e inteiro | 3 fases, 4 recortes, 0 ou 1 | regra sobre marcos oficiais | comparação entre períodos |
| `canal`, `porte`, `segmento` e respectivos códigos | texto | 3 canais, 2 portes, 5 segmentos | modelo | dimensões da decisão |
| `atividade_pmc_referencia` | texto | nome oficial da atividade | IBGE (PMC 8882) | linhagem do direcionador |
| `negocios_ativos` | inteiro | negócios | simulado | base da receita por negócio e do PE |
| `receita_bruta` | decimal | R$ correntes | simulado | receita transacionada; base das margens |
| `receita_bruta_real` | decimal | R$ de ago/2026 | simulado e deflacionado pelo IPCA oficial | participação e comparação entre fases |
| `pedidos` | inteiro | pedidos | simulado | ticket médio e frequência |
| `clientes_ativos`, `clientes_novos`, `clientes_recorrentes`, `clientes_ativos_mes_anterior` | inteiro | clientes | simulado | CAC, retenção e LTV |
| `investimento_marketing` | decimal | R$ correntes | simulado | CAC |
| `comissoes_tarifas` | decimal | R$ correntes | simulado com regras oficiais de tarifa | taxa de intermediação |
| `frete_subsidiado` | decimal | R$ correntes | simulado | custo variável |
| `cmv` | decimal | R$ correntes | simulado e calibrado na PAC 10645 | margem bruta |
| `custos_fixos` | decimal | R$ correntes | simulado | custo fixo do canal |
| `impostos_fixos`, `impostos_variaveis`, `impostos` | decimal | R$ correntes | simulado com regras legais (DAS e Anexo I) | F no MEI; v na ME |
| `margem_contribuicao`, `margem_liquida`, `margem_liquida_real` | decimal | R$ correntes e R$ de ago/2026 | derivado | resultado |
| indicadores (`ticket_medio`, `cac`, `take_rate`, `margem_liquida_pct`, `taxa_retencao`, `ltv`, `ltv_cac`, `payback_cac_meses`, `ponto_equilibrio_receita` e outros) | decimal | reais, fração ou meses | derivado por razão de somas | indicadores de decisão |
| `pmc_indice_volume_varejo_sa` | decimal | índice 2022 = 100 | oficial (PMC 8880) | contexto |
| `pmc_indice_volume_segmento`, `pmc_indice_receita_segmento` | decimal | índice 2022 = 100 | oficial (PMC 8882) | direcionador do painel |
| `ipca_variacao_mensal`, `ipca_indice`, `deflator_ipca` | decimal | %, índice e fator | oficial (IPCA, SIDRA 1737) | deflação e correção de custos |
| `fonte_ipca`, `qtd_campos_imputados` | texto e inteiro | rótulo; 0 ou 1 | metadado | linhagem e qualidade |

Fonte: elaborado pelo autor com base no arquivo `data/processed/dados_processados_canais_vendas.csv`.

### 3.6 Fórmulas dos indicadores

Todos os indicadores são calculados por razão de somas: somam-se primeiro as medidas aditivas e só então se divide. A média simples de margens já calculadas daria o mesmo peso a combinações de tamanhos muito diferentes, e uma combinação com poucos negócios pesaria tanto quanto outra com centenas. Uma única função de cálculo atende linhas e agregados, o que impede fórmulas divergentes. O Quadro 3 apresenta as fórmulas em texto plano, com Σ indicando a soma no nível de agregação.

**Quadro 3 – Fórmulas dos indicadores**

| Indicador | Fórmula |
|---|---|
| Ticket médio | Σ `receita_bruta` ÷ Σ `pedidos` |
| Frequência de compra | Σ `pedidos` ÷ Σ `clientes_ativos` |
| CAC | Σ `investimento_marketing` ÷ Σ `clientes_novos` |
| Taxa de intermediação (take rate) | Σ `comissoes_tarifas` ÷ Σ `receita_bruta` |
| Margem de contribuição | `receita_bruta` − `cmv` − `comissoes_tarifas` − `frete_subsidiado` − `impostos_variaveis` |
| Margem de contribuição % | Σ `margem_contribuicao` ÷ Σ `receita_bruta` |
| Margem líquida estimada | `margem_contribuicao` − `investimento_marketing` − `custos_fixos` − `impostos_fixos` |
| Margem líquida % | Σ `margem_liquida` ÷ Σ `receita_bruta` |
| Taxa de retenção mensal (r) | Σ `clientes_recorrentes` ÷ Σ `clientes_ativos_mes_anterior` |
| Tempo de vida (meses) | 1 ÷ (1 − r) |
| LTV | (Σ `receita_bruta` ÷ Σ `clientes_ativos`) × margem de contribuição % × 1 ÷ (1 − r) |
| LTV/CAC | LTV ÷ CAC (referência visual: 3) |
| Payback do CAC (meses) | CAC ÷ (Σ `margem_contribuicao` ÷ Σ `clientes_ativos`) |
| Receita por negócio | Σ `receita_bruta` ÷ Σ `negocios_ativos` |
| Custo variável (v) | (Σ `cmv` + Σ `comissoes_tarifas` + Σ `frete_subsidiado` + Σ `impostos_variaveis` + Σ `investimento_marketing`) ÷ Σ `receita_bruta` |
| Custo fixo por negócio (F) | (Σ `custos_fixos` + Σ `impostos_fixos`) ÷ Σ `negocios_ativos` |
| Ponto de equilíbrio (PE) | F ÷ (1 − v) |
| Folga sobre o PE | receita por negócio ÷ PE − 1 |
| Receita de indiferença (R\*) | (F_A − F_B) ÷ (v_B − v_A) |
| Participação do canal | Σ `receita_bruta_real` do canal ÷ Σ `receita_bruta_real` de todos os canais |

Fonte: elaborado pelo autor.

O marketing entra em v como custo proporcional à receita, premissa razoável no micro varejo, em que o gasto com anúncios acompanha as vendas. Por construção, a margem líquida por negócio é igual a (receita por negócio − PE) × (1 − v), identidade conferida em teste automatizado: folga sobre o ponto de equilíbrio e margem líquida contam a mesma história.

### 3.7 Premissas e calibração

O registro de premissas tem 45 parâmetros, classificados pela origem: 7 de fonte oficial, 4 de fonte de mercado, 3 de fonte com ajuste do autor e 31 premissas do autor, concentradas no tamanho do painel, nas receitas e tickets de referência, na retenção, no CAC, no frete e nos custos fixos, justamente onde não há dado público para MEIs e MEs (Tabela 3). Seis checagens de calibração (C1 a C6) confrontam o painel com referências externas: crescimento da receita digital entre 2019 e 2024, ganho de participação digital entre 2019 e 2021, variação da loja física e do digital em abr/2020, participação digital no Cenário Atual e taxa de intermediação do marketplace (seção 4.7).

**Tabela 3 – Principais premissas e parâmetros do painel**

| Parâmetro | Valor | Origem | Referência |
|---|---|---|---|
| Negócios por segmento | 400 MEIs e 100 MEs | premissa do autor | não se aplica |
| Proporção de negócios nos canais digitais (âncoras) | MEI: marketplace de 7% (dez/2017) a 28% (ago/2026) e próprio de 5% a 14%; ME: de 6% a 21% e de 4% a 13% | fonte com ajuste do autor | Sebrae (2021); PAC |
| Multiplicadores de segmento sobre a proporção digital | de 0,45 (Alimentos, marketplace) a 1,60 (Eletrônicos, marketplace) | fonte com ajuste do autor | PAC (ordem da participação da Internet) |
| Receita média mensal por negócio em 2019 | MEI de R$ 3.500 a R$ 4.100; ME de R$ 14.500 a R$ 17.500 | premissa do autor | não se aplica |
| Receita relativa à loja física | MEI 1,00 / 0,80 / 0,75; ME 1,00 / 0,85 / 0,90 (física / marketplace / próprio) | premissa do autor | não se aplica |
| Impulso da demanda digital | 1,00 até fev/2020; 1,70 em abr/2020; 1,00 a partir de dez/2022 | premissa do autor | não se aplica |
| Ticket médio de 2019 | de R$ 45 a R$ 165 por segmento e canal | premissa do autor | não se aplica |
| Frequência de compra | de 1,01 a 1,60 pedido por cliente ativo no mês | premissa do autor | não se aplica |
| Retenção mensal de base | física 32%; marketplace 10%; próprio de 20% a 30% | premissa do autor | não se aplica |
| CAC de 2019 e tendência real | de R$ 2 a R$ 20 por cliente novo; 0%, 2% e 3% ao ano | premissa do autor | não se aplica |
| Comissão do marketplace | 11% até ago/2022; 12% a partir de set/2022 | fonte de mercado | Mercado Livre |
| Tarifa fixa do marketplace | de R$ 5,00 abaixo de R$ 120 (jul/2018) a R$ 6,00 abaixo de R$ 79 (jan/2024) | fonte de mercado | Mercado Livre |
| Processamento no canal próprio | 4,5% antes do Pix (premissa); 4,19% no cartão e 0,99% no Pix | fonte de mercado | Nuvemshop |
| Taxa de cartão na loja física | 2,2% sobre a parcela não paga com Pix | premissa do autor | não se aplica |
| Adoção do Pix | próprio de 0% (out/2020) a 35% (dez/2022) e 45% (ago/2026); física de 0% a 30% e 40% | premissa do autor | não se aplica |
| Frete por pedido e parcela paga pelo vendedor | marketplace R$ 18 × 25%; próprio R$ 22 × 40% | premissa do autor | não se aplica |
| CMV ÷ receita | Moda 55,1%; Casa 59,3%; Eletrônicos 58,0%; Beleza 60,2%; Alimentos 65,7% | fonte com ajuste do autor | PAC 10645 (2024) |
| Custos fixos mensais por negócio em 2019 | MEI R$ 950 / 260 / 320; ME R$ 4.200 / 1.000 / 1.400 (física / marketplace / próprio) | premissa do autor | não se aplica |
| DAS do MEI | 5% do salário mínimo + R$ 1,00 de ICMS | fonte oficial | Lei nº 8.212/1991; LC nº 123/2006 |
| Salário mínimo | de R$ 954 (2018) a R$ 1.621 (2026) | fonte oficial | Ipeadata |
| Simples Nacional, Anexo I | 4,00% até R$ 180 mil; 7,30% com dedução de R$ 5.940 até R$ 360 mil | fonte oficial | LC nº 123/2006 |
| Tetos de receita anual | MEI R$ 81.000; ME R$ 360.000 | fonte oficial | LC nº 123/2006 |
| Sementes aleatórias | 2026 (painel) e 2027 (problemas de qualidade) | premissa do autor | não se aplica |

Fonte: elaborado pelo autor com base em `outputs/tabelas/premissas.csv`.

Nota: o CMV de Eletrônicos parte da referência da PAC (65,8%) com ajuste de −7,8 pontos percentuais, porque no micro varejo predominam acessórios, de margem maior que a dos eletrônicos vendidos pelas grandes redes.

### 3.8 Qualidade dos dados

Para exercitar a limpeza como em um caso real, o painel é exportado como extração de um sistema de gestão, com problemas injetados de forma controlada: datas em três formatos, números em padrão brasileiro com e sem o símbolo da moeda, rótulos variantes, duplicatas e células vazias. A Tabela 4 compara o arquivo antes e depois da limpeza; como a injeção fica registrada em um gabarito, é possível conferir se cada problema foi corrigido.

**Tabela 4 – Qualidade do arquivo bruto simulado antes e depois da limpeza**

| Item | Arquivo bruto (antes) | Tratamento | Resultado (depois) |
|---|---|---|---|
| Linhas | 3.183 | remoção de duplicatas | 3.120 (104 meses × 30 combinações) |
| Duplicatas exatas | 47 | remoção sobre o texto bruto | 0 |
| Duplicatas por chave, com formatação diferente | 16 | mantida a linha com menos ausentes | 0 |
| Datas | três formatos: AAAA-MM (1.914), MM/AAAA (808) e AAAA-MM-01 (461) | leitura por padrão, com dia 01 obrigatório | data única no padrão ISO |
| Números em formato brasileiro | 8.663 valores no padrão `1.234,56`, 1.205 no padrão `R$ 1.234,56` e 1.120 contagens com separador de milhar | conversão para número | nenhum número armazenado como texto |
| Rótulos variantes | 621 em canal, 318 em porte e 341 em segmento | normalização do texto e mapa de rótulos | 3 canais, 2 portes e 5 segmentos |
| Células vazias | 1.113, ou 1.092 após remover as duplicatas (78 por coluna de medida) | imputação por razão | nenhum nulo; 1.092 linhas com uma célula imputada |
| Conferência com o gabarito | não se aplica | duplicatas, células imputadas e conjunto de células | todas aprovadas |

Fonte: elaborado pelo autor com base em `outputs/relatorio_qualidade_dados.json`.

A imputação das 1.092 células vazias é a etapa que mais poderia distorcer o painel. Interpolar uma medida isolada entre meses vizinhos falharia justamente no pico de dezembro e no choque de abril de 2020, gerando uma receita incoerente com os custos da mesma linha. Por isso, cada célula é reconstruída com um valor presente na própria linha e uma razão estável dos meses vizinhos: a receita vem do CMV dividido pela relação entre CMV e receita, o marketing vem dos clientes novos multiplicados pelo CAC, o DAS segue a regra legal e os clientes seguem identidades exatas. A conferência com o gabarito foi integralmente aprovada.

Nos dados oficiais, a limpeza converte os sinais do IBGE, em que "-" é zero absoluto e "X" é valor omitido por sigilo, e aplica soma estrita na PAC: qualquer parcela sob sigilo torna a soma indisponível, nunca zero nem soma parcial. A tabela 9349 trouxe 25 sinais "X" e 56 "-", e a 10656, 14 e 24. Das 42 combinações de ano e grupo da tabela de Internet, 25 têm a participação calculada e 17 ficam sem valor por sigilo em alguma parcela; a soma parcial esconderia o sigilo e inflaria a participação da Internet.

### 3.9 Limitações

As limitações devem ser lidas junto com os resultados. A principal é a natureza do painel: as medidas por canal são simuladas e calibradas, não representam empresas reais, e as conclusões valem sob as premissas declaradas. As pesquisas oficiais cobrem empresas com 20 ou mais pessoas ocupadas, a PAC de 2024 é série nova e o sigilo estatístico só deixa 2021 com os cinco segmentos completos.

Cada negócio tem um único canal principal, de modo que a recomendação "híbrida" indica empate técnico entre dois canais, e não uma operação multicanal modelada. Custos fixos, CAC, frete e retenção são premissas do autor, e o CAC da loja física é baixo por construção, porque o tráfego de passagem é pago pelo aluguel. A tarifa histórica usa o Mercado Livre como referência, com o custo fixo posterior a jan/2024 mantido como premissa, e o histórico da Shopee não pôde ser verificado. Há ainda limitações de medida: a imputação tem erro pequeno, mas não nulo, e a coluna `qtd_campos_imputados` isola as 1.092 linhas afetadas; o MDIC mede vendas com nota fiscal; o LTV não desconta fluxos futuros; e 2026 está incompleto (jan–ago), o que exige comparar anos por participações ou médias mensais.

## 4 Resultados e Discussão

Os resultados seguem a ordem em que respondem à pergunta de pesquisa. Primeiro, o contexto real mostra o que mudou no mercado segundo os dados oficiais (4.1). Depois, o painel mostra como a receita se redistribuiu entre os canais (4.2), quanto de cada real vendido sobra em cada um (4.3), quanto vale cada cliente conquistado (4.4) e como a comissão do marketplace se compara ao custo de aquisição do canal próprio (4.5). Esses elementos se combinam na análise de ponto de equilíbrio e de receitas de indiferença, que traduz a comparação em faturamento mensal (4.6). A seção termina com a calibração (4.7) e com a separação entre o que os dados sustentam e o que é premissa (4.8). Os números oficiais trazem sempre a citação da fonte, e os do painel são identificados como tal. Os valores monetários do painel estão em reais correntes, salvo quando indicados em reais de ago/2026, isto é, deflacionados pelo IPCA.

### 4.1 Contexto real: consumo, inflação e Internet no varejo

A Figura 1 reúne apenas dados oficiais. Na parte (a), o volume do varejo cai de 98,13 em fevereiro para 78,83 em abril de 2020 e se recupera em forma de V, até 104,57 em outubro. A partir de fevereiro de 2022, o índice não volta a ficar abaixo do nível de fevereiro de 2020; depois, sobe de forma gradual até 110,14 em março de 2026 e fecha agosto de 2026 em 108,69 (IBGE, 2026d). Na parte (b), a maior alta mensal do IPCA no período é de 1,62% (mar/2022), a maior queda é de −0,68% (jul/2022), e o acumulado em 12 meses atinge 12,13% em abril de 2022 (IBGE, 2026a). Na parte (c), a participação da Internet no varejo com 20 ou mais pessoas ocupadas aparece por segmento apenas nos anos sem sigilo estatístico, para não sugerir continuidade onde o dado não existe.

**Figura 1 – Contexto macroeconômico real: (a) volume de vendas do varejo com ajuste sazonal (PMC, tabela 8880); (b) IPCA mensal e acumulado em 12 meses (tabela 1737); (c) participação da Internet na receita de revenda do varejo com 20 ou mais pessoas ocupadas (PAC), 2018–2026**

![Figura 1 – Três gráficos com dados oficiais do IBGE: volume do varejo com ajuste sazonal, IPCA mensal e acumulado em 12 meses e participação da Internet na receita do varejo](../outputs/graficos/09_contexto_macro_real.png)

Fonte: elaborado pelo autor com base em IBGE (2026a, 2026b, 2026d). Somente dados oficiais.

A Tabela 5 resume os indicadores anuais. Dois fatos oficiais emolduram a análise de canais. O primeiro é que a migração para a Internet nas empresas maiores foi rápida em 2020 e 2021 e depois se estabilizou entre 8,77% e 9,84% da receita, enquanto a receita on-line nominal mais que triplicou entre 2019 e 2024. O segundo é que a inflação acumulada de 55,26% corroeu o teto do MEI e encareceu os custos fixos num período em que o volume de vendas cresceu de forma moderada. Qualquer resultado do painel precisa ser coerente com esse pano de fundo, o que a seção 4.7 confirma.

**Tabela 5 – Indicadores oficiais selecionados, 2018–2025**

| Ano | IPCA acumulado em 12 meses até dezembro (%) | Internet na receita de revenda do varejo com 20 ou mais pessoas ocupadas (%) | Receita do varejo via Internet (R$ bilhões) | Empresas que vendem pela Internet |
|---|---|---|---|---|
| 2018 | 3,75 | ... | ... | ... |
| 2019 | 4,31 | 5,26 | 67,79 | 1.888 |
| 2020 | 4,52 | 8,36 | 116,78 | 2.768 |
| 2021 | 10,06 | 9,84 | 161,44 | 3.100 |
| 2022 | 5,78 | 9,11 | 171,60 | 3.340 |
| 2023 | 4,62 | 8,77 | 177,57 | 3.730 |
| 2024 | 4,83 | 9,78 | 217,91 | 3.850 |
| 2025 | 4,26 | ... | ... | ... |

Fonte: elaborado pelo autor com base em IBGE (2026a, 2026b); arquivos `outputs/tabelas/indicadores_reais.csv` e `outputs/tabelas/pac_internet.csv`.

Nota: sinal convencional "..." = dado numérico não disponível, porque as tabelas da PAC por forma de comercialização usadas cobrem 2019 a 2024; 2024 pertence à série nova da PAC (tabela 10656), com quebra de comparabilidade; valores monetários nominais.

### 4.2 Transição da receita e participação dos canais

No painel, a pandemia reorganiza a receita entre os canais (Figura 2). Entre fevereiro e abril de 2020, a receita real da Loja Física cai 38,71%, enquanto a dos canais digitais cresce 87,10%; em maio, a Loja Física responde por 68,64% da receita real, contra 89,37% em fevereiro. A queda da Loja Física no painel é quase o dobro da registrada pelo varejo oficial (−19,67%), e a diferença tem três explicações. A primeira é a composição: no painel, os cinco segmentos têm o mesmo número de negócios, e três deles (Moda, Casa e Eletrônicos) sofreram quedas oficiais de 40% a 80% entre fevereiro e abril, enquanto o agregado oficial inclui atividades que caíram pouco ou cresceram, como supermercados e alimentos (+3,49%). A segunda é a migração: o modelo concentra nesses meses a passagem de negócios para os canais digitais, e o número de negócios com canal principal na loja física cai de 2.149 para 1.888 entre fevereiro e abril (−12,1%). A terceira é de medida, pois a série oficial é de volume com ajuste sazonal, e a do painel, de receita real sem ajuste.

**Figura 2 – Evolução da receita real mensal por canal de venda, em R$ de ago/2026 (2018–2026)**

![Figura 2 – Linhas da receita real mensal da Loja Física, do Marketplace e do E-commerce Próprio, com médias móveis de 3 meses e as fases sombreadas](../outputs/graficos/01_receita_real_por_canal.png)

Fonte: elaborado pelo autor com base no painel simulado calibrado (elaboração própria) e em dados do IBGE (2026a, 2026b, 2026d).

A participação digital anual no painel passa de 10,00% em 2018 e 10,58% em 2019 para 26,04% em 2020 e 30,08% em 2021, oscila perto de 30% em 2022 e 2023 (29,55% e 30,10%) e chega a 31,54% em 2024, 32,95% em 2025 e 33,88% em 2026 (jan–ago). O salto, portanto, é de 2020; depois, o avanço do digital é lento, mas não se reverte. Por recorte (Figura 3 e Tabela 6), a Loja Física cai de 89,69% da receita real na pré-pandemia para 70,47% na pandemia, 69,50% no pós-pandemia e 66,69% no Cenário Atual, sem voltar ao nível anterior. O Marketplace mais que triplica sua fatia, de 6,18% para 21,40%, e o E-commerce Próprio quase a triplica, de 4,13% para 11,91%. O marketplace absorve a maior parte do ganho digital porque, nas âncoras de migração calibradas com o Sebrae e a PAC, é o canal que mais recebe negócios.

**Figura 3 – Participação dos canais na receita real, por recorte temporal**

![Figura 3 – Barras empilhadas com a participação de cada canal na receita real nos quatro recortes temporais](../outputs/graficos/02_participacao_canal_por_fase.png)

Fonte: elaborado pelo autor com base no painel simulado calibrado (elaboração própria) e em dados do IBGE (2026a, 2026b, 2026d).

O painel amplifica o fenômeno observado na PAC: a participação digital vai de 10,31% para 33,31% no painel, enquanto a Internet passou de 5,26% (2019) para 9,78% (2024) nas empresas maiores. A diferença é coerente com a evidência de que o digital pesa mais no micro varejo: um terço dos MEIs que vendiam on-line obtinha mais da metade do faturamento pela internet, contra 22% entre os donos de micro e pequenas empresas (SEBRAE, 2021).

A receita real total do painel recua de R$ 22,37 milhões por mês na pré-pandemia para R$ 19,83 milhões no Cenário Atual, em reais de ago/2026. Como o número de negócios é fixo e a tendência das grandes redes foi removida, o recuo combina dois efeitos do modelo. O ticket de cada segmento acompanha o preço implícito da atividade na PMC, que, na composição do painel, subiu menos que o IPCA usado na deflação, como mostra a queda do ticket real em todos os canais (seção 4.4). Além disso, os negócios que migram para os canais digitais faturam, por premissa, de 75% a 90% do que fatura um negócio da loja física. Por isso, o painel não deve ser lido como medida do crescimento do micro varejo, e sim como um laboratório para comparar canais em condições comuns.

**Tabela 6 – Indicadores por recorte temporal e canal**

| Recorte | Canal | Participação na receita real (%) | Receita real média mensal (R$ milhões de ago/2026) | Ticket médio real (R$ de ago/2026) | Taxa de intermediação (%) | Margem líquida (%) | Retenção mensal (%) |
|---|---|---|---|---|---|---|---|
| Pré-pandemia | Loja Física | 89,69 | 20,06 | 117,54 | 2,20 | 8,33 | 34,81 |
| Pré-pandemia | Marketplace | 6,18 | 1,38 | 128,38 | 14,62 | 5,99 | 9,50 |
| Pré-pandemia | E-commerce Próprio | 4,13 | 0,92 | 166,67 | 4,50 | 7,41 | 22,93 |
| Pandemia | Loja Física | 70,47 | 15,31 | 112,12 | 2,02 | 6,77 | 34,56 |
| Pandemia | Marketplace | 17,89 | 3,89 | 125,91 | 14,16 | 6,44 | 9,72 |
| Pandemia | E-commerce Próprio | 11,64 | 2,53 | 160,70 | 3,96 | 7,69 | 25,70 |
| Pós-pandemia (jun/2022–dez/2024) | Loja Física | 69,50 | 14,38 | 111,54 | 1,51 | 7,47 | 35,67 |
| Pós-pandemia (jun/2022–dez/2024) | Marketplace | 19,17 | 3,97 | 120,92 | 14,20 | 4,21 | 9,69 |
| Pós-pandemia (jun/2022–dez/2024) | E-commerce Próprio | 11,33 | 2,34 | 160,50 | 3,02 | 6,56 | 28,37 |
| Cenário Atual (2025–2026) | Loja Física | 66,69 | 13,23 | 106,35 | 1,37 | 6,39 | 35,66 |
| Cenário Atual (2025–2026) | Marketplace | 21,40 | 4,24 | 113,85 | 14,22 | 2,71 | 9,42 |
| Cenário Atual (2025–2026) | E-commerce Próprio | 11,91 | 2,36 | 153,95 | 2,82 | 5,03 | 30,66 |

Fonte: elaborado pelo autor com base no painel simulado calibrado (elaboração própria); arquivo `outputs/tabelas/kpis_recorte_canal.csv`.

Nota: taxa de intermediação = comissões e tarifas ÷ receita bruta; na Loja Física, corresponde à taxa de cartão; no E-commerce Próprio, ao processamento de pagamento. Receita média mensal = receita real do recorte ÷ número de meses (26, 27, 31 e 20).

### 4.3 Custos e margens

A composição de custos do Cenário Atual (Figura 4 e Tabela 7) mostra que cada canal gasta a receita em um lugar diferente. A mercadoria consome de 58,29% a 60,52% da receita em todos os canais e portes, e a diferença está no restante. Na Loja Física do MEI, o maior custo depois do CMV é o fixo, de 24,50% da receita, e a tarifa de cartão é de apenas 1,37%. No Marketplace do MEI, a comissão leva 14,19%, o frete subsidiado 5,77% e o marketing 6,86%, enquanto o custo fixo cai para 8,93%. No E-commerce Próprio do MEI, a tarifa é de 2,82%, mas marketing (11,16%) e frete (8,36%) somam quase 20% da receita. O resultado é uma margem líquida de 9,13% na Loja Física, 5,65% no Próprio e 3,44% no Marketplace do MEI. Na ME, o Simples Nacional acrescenta de 4,43% a 4,98% de impostos sobre a receita, e as margens caem para 4,09%, 4,49% e 1,85%, na mesma ordem, com o Próprio na liderança.

**Figura 4 – Composição de custos e margem líquida por canal e porte, em % da receita bruta, Cenário Atual (2025–2026)**

![Figura 4 – Barras horizontais com CMV, comissões, frete, marketing, custos fixos, impostos e margem líquida de cada canal, para MEI e ME](../outputs/graficos/03_composicao_custos_margem_por_canal.png)

Fonte: elaborado pelo autor com base no painel simulado calibrado (elaboração própria) e em dados do IBGE (2026a, 2026b, 2026d).

**Tabela 7 – Composição da receita e margem líquida por porte e canal, em % da receita bruta**

| Porte | Canal | CMV | Comissões e tarifas | Frete subsidiado | Marketing | Custos fixos | Impostos | Margem líquida (Cenário Atual) | Margem líquida (Pré-pandemia) |
|---|---|---|---|---|---|---|---|---|---|
| MEI | Loja Física | 60,52 | 1,37 | 0,00 | 2,95 | 24,50 | 1,53 | 9,13 | 10,45 |
| MEI | Marketplace | 58,80 | 14,19 | 5,77 | 6,86 | 8,93 | 2,01 | 3,44 | 6,58 |
| MEI | E-commerce Próprio | 58,29 | 2,82 | 8,36 | 11,16 | 11,60 | 2,12 | 5,65 | 7,89 |
| ME | Loja Física | 60,41 | 1,37 | 0,00 | 3,01 | 26,14 | 4,98 | 4,09 | 6,39 |
| ME | Marketplace | 58,94 | 14,25 | 5,81 | 6,92 | 7,81 | 4,43 | 1,85 | 5,35 |
| ME | E-commerce Próprio | 58,34 | 2,82 | 8,38 | 11,35 | 9,96 | 4,66 | 4,49 | 6,90 |

Fonte: elaborado pelo autor com base no painel simulado calibrado (elaboração própria); arquivos `outputs/tabelas/composicao_custos_atual.csv` e `outputs/tabelas/kpis_recorte_canal_porte.csv`.

Nota: os sete componentes do Cenário Atual (do CMV à margem líquida) somam 100% da receita, com diferença de até 0,01 ponto por arredondamento.

Entre a pré-pandemia e o Cenário Atual, a margem líquida cai em todos os canais e portes (Figura 5): de 10,45% para 9,13% na Loja Física do MEI, de 7,89% para 5,65% no Próprio do MEI, de 6,58% para 3,44% no Marketplace do MEI e de 5,35% para 1,85% no Marketplace da ME, a maior queda. No conjunto do painel, a margem líquida recua de 8,15% para 5,44% da receita. Três mecanismos do modelo explicam a compressão. O primeiro é a diferença entre preços: custos fixos, frete e CAC acompanham o IPCA, enquanto a receita acompanha os preços das atividades na PMC, que subiram menos; por isso, o custo fixo da Loja Física do MEI passa de 23,45% para 24,50% da receita. O segundo é a alta real dos custos digitais, com o CAC crescendo acima da inflação, a comissão de referência subindo de 11% para 12% em set/2022 e a tarifa fixa passando de R$ 5,00 para R$ 6,00. O terceiro é o peso dos impostos: o DAS acompanha o salário mínimo, que subiu mais que a inflação, e passa de 1,34% para 1,53% da receita da Loja Física do MEI; na ME, a alíquota efetiva do Simples sobe com a receita nominal, porque as faixas do Anexo I são fixas, e vai de 4,19% para 4,98% da receita na Loja Física.

**Figura 5 – Margem líquida estimada por canal e porte, Pré-pandemia e Cenário Atual (razão de somas)**

![Figura 5 – Mapas de calor da margem líquida por canal e porte na pré-pandemia e no cenário atual](../outputs/graficos/08_heatmap_margem_canal_porte.png)

Fonte: elaborado pelo autor com base no painel simulado calibrado (elaboração própria) e em dados do IBGE (2026a, 2026b, 2026d).

O choque de 2020 mostra o risco da estrutura fixa. Em abril de 2020, a margem líquida mensal agregada da Loja Física chega a −8,92% no painel e continua negativa em maio (−0,51%), porque o aluguel e os demais custos fixos se mantêm enquanto as vendas de vestuário, móveis e eletrônicos desabam, como no dado oficial, em que o volume de vestuário caiu 79,51%. O Marketplace e o Próprio, com custos majoritariamente variáveis, atravessam o mesmo mês com margem positiva, de 2,35% e 3,08%. Custo fixo alto amplia o resultado nos meses bons e o prejuízo nos meses ruins.

### 4.4 Clientes e economia unitária

A Figura 6 cruza o CAC e o LTV das 30 combinações de canal, porte e segmento no Cenário Atual. As dez combinações da Loja Física ficam acima da reta LTV = 3 × CAC, com LTV/CAC entre 7,40 (Eletrônicos e Acessórios, ME) e 24,41 (Alimentos e Bebidas, MEI). Marketplace e Próprio se espalham em torno da reta: 4 combinações do Marketplace e 2 do Próprio atingem LTV/CAC de pelo menos 3, o que totaliza 16 de 30, e o menor valor é o do Marketplace de Eletrônicos e Acessórios na ME (1,70).

**Figura 6 – CAC × LTV por canal, porte e segmento, Cenário Atual (2025–2026), em escala logarítmica**

![Figura 6 – Dispersão de CAC e LTV das 30 combinações de canal, porte e segmento, com as retas LTV = CAC e LTV = 3 × CAC](../outputs/graficos/04_dispersao_cac_ltv.png)

Fonte: elaborado pelo autor com base no painel simulado calibrado (elaboração própria) e em dados do IBGE (2026a, 2026b, 2026d).

A leitura exige cuidado. O CAC da Loja Física é baixo (R$ 6,19 no Cenário Atual) porque, no modelo, o tráfego de passagem é pago pelo aluguel do ponto, registrado nos custos fixos; LTV/CAC alto, portanto, não significa canal mais lucrativo, e a comparação correta é feita pela margem e pelo ponto de equilíbrio (seções 4.3 e 4.6). No E-commerce Próprio, o CAC é o maior (R$ 27,53), mas a retenção mensal é de 30,66%, mais de três vezes a do Marketplace (9,42%), onde o cliente pertence à plataforma. Por isso, o LTV do Próprio (R$ 68,10) é quase o triplo do LTV do Marketplace (R$ 23,82), e os dois canais digitais terminam com LTV/CAC próximos, de 2,47 e 2,77 (Tabela 8). É a aplicação direta do argumento de Gupta, Lehmann e Stuart (2004): a retenção compensa um custo de aquisição maior.

**Tabela 8 – Economia unitária por canal e porte, Cenário Atual (2025–2026)**

| Canal | Porte | Ticket médio (R$ correntes) | CAC (R$ correntes) | Retenção mensal (%) | LTV (R$ correntes) | LTV/CAC | Payback do CAC (meses) |
|---|---|---|---|---|---|---|---|
| Loja Física | MEI | 102,99 | 6,15 | 35,87 | 78,88 | 12,83 | 0,12 |
| Loja Física | ME | 103,48 | 6,22 | 35,49 | 68,17 | 10,95 | 0,14 |
| Marketplace | MEI | 110,95 | 8,59 | 9,49 | 26,57 | 3,09 | 0,36 |
| Marketplace | ME | 110,18 | 8,58 | 9,33 | 20,55 | 2,39 | 0,46 |
| E-commerce Próprio | MEI | 149,76 | 27,38 | 30,70 | 74,38 | 2,72 | 0,53 |
| E-commerce Próprio | ME | 149,37 | 27,66 | 30,62 | 62,62 | 2,26 | 0,64 |
| Loja Física | Todos | 103,25 | 6,19 | 35,66 | 73,03 | 11,80 | 0,13 |
| Marketplace | Todos | 110,60 | 8,59 | 9,42 | 23,82 | 2,77 | 0,40 |
| E-commerce Próprio | Todos | 149,55 | 27,53 | 30,66 | 68,10 | 2,47 | 0,58 |

Fonte: elaborado pelo autor com base no painel simulado calibrado (elaboração própria); arquivos `outputs/tabelas/kpis_recorte_canal_porte.csv` e `outputs/tabelas/kpis_recorte_canal.csv`.

O ticket real completa o quadro (Figura 7). O E-commerce Próprio tem o maior ticket em todos os recortes, de R$ 166,67 na pré-pandemia a R$ 153,95 no Cenário Atual, em reais de ago/2026, e o ticket real cai em todos os canais, pelo efeito de preços explicado na seção 4.2. Um ticket maior ajuda o canal próprio a diluir o frete e o custo de aquisição de cada pedido, o que explica parte da sua margem.

**Figura 7 – Ticket médio real por canal e recorte temporal, em R$ de ago/2026**

![Figura 7 – Barras agrupadas com o ticket médio real de cada canal nos quatro recortes temporais](../outputs/graficos/05_ticket_medio_canal_fase.png)

Fonte: elaborado pelo autor com base no painel simulado calibrado (elaboração própria) e em dados do IBGE (2026a, 2026b, 2026d).

A retenção do Próprio sobe de 22,93% para 30,66% entre a pré-pandemia e o Cenário Atual (Figura 8), reflexo da premissa de que o relacionamento direto, por WhatsApp e listas de clientes, amadurece com o tempo; como essa alta é premissa, o resultado mostra a consequência da hipótese, e não a prova. A do Marketplace fica entre 9,42% e 9,72% em todos os recortes, e a da Loja Física, entre 34,56% e 35,67%, com a queda temporária causada pelo fechamento do comércio em 2020. O payback do CAC é inferior a um mês em todas as 30 combinações e de 0,22 mês no conjunto do Cenário Atual: sob as premissas de CAC do modelo, a aquisição se paga rápido em todos os canais, e a diferença entre eles está menos no prazo de retorno e mais no valor acumulado por cliente e na margem que sobra depois dos custos fixos.

**Figura 8 – Taxa de retenção mensal de clientes por canal (média móvel de 3 meses, razão de somas)**

![Figura 8 – Linhas da taxa de retenção mensal da Loja Física, do Marketplace e do E-commerce Próprio entre 2018 e 2026](../outputs/graficos/06_taxa_retencao_tempo.png)

Fonte: elaborado pelo autor com base no painel simulado calibrado (elaboração própria) e em dados do IBGE (2026a, 2026b, 2026d).

### 4.5 Taxa de intermediação do marketplace e custo de aquisição do canal próprio

A parte (a) da Figura 9 mostra que, nos dados simulados, a comissão do marketplace e o custo de aquisição do canal próprio disputam o mesmo espaço da margem. A taxa de intermediação do Marketplace salta de 11,00% em jun/2018 para 15,49% em jul/2018, quando entra a tarifa fixa de R$ 5,00 por unidade abaixo de R$ 120. Depois recua, para 14,56% em out/2020 e 13,81% em abr/2021, com a redução do limite para R$ 99 e para R$ 79 e com o aumento do ticket, que deixa menos pedidos abaixo do limite, e volta a subir com a comissão de 12% (14,10% em set/2022) e com as tarifas fixas de R$ 5,50 e R$ 6,00. Na média anual, vai de 13,46% em 2018 e 15,56% em 2019 para 14,27% em 2025 e 14,14% em 2026, e fica em 14,22% no Cenário Atual, dentro da faixa de 10% a 19% das modalidades Clássico e Premium. No E-commerce Próprio, o marketing passa de 9,46% para 11,26% da receita entre a pré-pandemia e o Cenário Atual, enquanto as tarifas de pagamento caem de 4,50% para 2,82% com a adoção do Pix; na Loja Física, a tarifa de cartão cai de 2,20% para 1,37%. O Pix barateou o recebimento nos canais sem intermediário, mas, no canal próprio, o ganho foi mais do que absorvido pelo custo de atrair clientes: o marketing subiu cerca de 1,8 ponto percentual da receita, e as tarifas caíram cerca de 1,7 ponto.

**Figura 9 – Taxa de intermediação do marketplace × custos do e-commerce próprio: (a) painel simulado, 2018–2026; (b) regras oficiais vigentes de tarifas por valor do item**

![Figura 9 – Parte (a) com a taxa de intermediação do marketplace e os custos do canal próprio ao longo do tempo; parte (b) com o custo efetivo por valor do item no Mercado Livre, na Shopee e na Amazon](../outputs/graficos/07_take_rate_marketplace_vs_cac_ecommerce.png)

Fonte: elaborado pelo autor com base no painel simulado calibrado (elaboração própria), em IBGE (2026a, 2026b, 2026d) e nas regras oficiais de Mercado Livre ([2026]), Shopee (2026a, 2026b) e Amazon ([2026]), consultadas em 18/10/2026.

A parte (b) da figura e a Tabela 9 aplicam as regras oficiais vigentes em outubro de 2026 a um item isolado, sem simulação. Para itens baratos, a parcela fixa domina: um item de R$ 30 paga 32,00% no Mercado Livre Clássico (12% mais R$ 6), 35,00% na Shopee CNPJ e 19,17% na Amazon Individual. A partir de R$ 79, o Clássico cai para a comissão pura de 12,00%, enquanto a Shopee tem degraus, com 25,63% em R$ 79,99 e 34,00% em R$ 80, o que torna relevante a precificação logo abaixo de R$ 80. Em R$ 500, a Shopee cobra 19,20%, e a Amazon Individual, 12,90%. Na Amazon, como o plano Profissional custa R$ 19,00 por mês depois do primeiro ano e o Individual cobra R$ 2,00 por item, o Profissional compensa a partir do 10º item vendido no mês, pois 19 ÷ 2 = 9,5. O subsídio Pix da Shopee não reduz a tarifa do vendedor, porque é um desconto ao comprador custeado pela plataforma (SHOPEE, 2026b). Para o microempreendedor, a lição é que o custo do marketplace depende do valor do item, e preço e tamanho do pedido podem mudar a faixa de tarifa.

**Tabela 9 – Taxa de intermediação efetiva por valor do item, regras oficiais vigentes em outubro de 2026 (%)**

| Valor do item (em reais) | Mercado Livre Clássico | Shopee CNPJ | Amazon Individual | Amazon Profissional |
|---|---|---|---|---|
| 30,00 | 32,00 | 35,00 | 19,17 | 12,50 |
| 50,00 | 24,00 | 29,00 | 16,50 | 12,50 |
| 79,99 | 12,00 | 25,63 | 15,00 | 12,50 |
| 80,00 | 12,00 | 34,00 | 15,00 | 12,50 |
| 99,99 | 12,00 | 30,00 | 14,50 | 12,50 |
| 100,00 | 12,00 | 34,00 | 14,50 | 12,50 |
| 150,00 | 12,00 | 27,33 | 13,83 | 12,50 |
| 199,99 | 12,00 | 24,00 | 13,50 | 12,50 |
| 200,00 | 12,00 | 27,00 | 13,50 | 12,50 |
| 300,00 | 12,00 | 22,67 | 13,17 | 12,50 |
| 500,00 | 12,00 | 19,20 | 12,90 | 12,50 |

Fonte: elaborado pelo autor com base em Mercado Livre ([2026]), Shopee (2026a, 2026b) e Amazon ([2026]); arquivo `outputs/tabelas/tarifas_marketplaces_2026.csv`.

Nota: Mercado Livre Clássico com comissão no ponto médio (12%) da faixa oficial de 10% a 14% e R$ 6 por item abaixo de R$ 79; Amazon com comissão no ponto médio (12,5%) da faixa de 10% a 15%, mais R$ 2 por item no plano Individual ou R$ 19 por mês, fora da tarifa por item, no Profissional; Shopee com taxa de transação e frete grátis incluídos e sem desconto do subsídio Pix. Frete à parte no Mercado Livre e na Amazon.

### 4.6 Ponto de equilíbrio e receitas de indiferença

A Figura 10 e as Tabelas 10 e 11 traduzem a economia dos canais em faturamento mensal por negócio, a etapa que responde diretamente à pergunta de pesquisa. No MEI, a Loja Física tem o menor custo variável (v = 64,84%) e o maior custo fixo (F = R$ 1.340,25 por mês, incluído o DAS), o que exige R$ 3.811,80 de receita mensal para empatar. O Marketplace tem o maior custo variável (85,62%) e o menor custo fixo (R$ 429,44), com ponto de equilíbrio de R$ 2.986,93. O Próprio fica no meio (80,63% e R$ 510,30) e tem o menor ponto de equilíbrio, R$ 2.634,34, porque seu custo fixo é próximo do custo fixo do marketplace e sua margem por real vendido é maior. Na ME, a ordem se repete em escala maior, com pontos de equilíbrio de R$ 18.480,16, R$ 13.962,75 e R$ 13.060,91. No Cenário Atual, o negócio médio opera acima do ponto de equilíbrio em todos os canais e portes, com folga de 15,63% (Loja Física da ME) a 45,04% (Próprio da ME). No nível de segmento, porém, quatro combinações do Marketplace operam abaixo do ponto de equilíbrio, com margem líquida negativa: Eletrônicos e Acessórios nos dois portes e Beleza e Cuidados Pessoais e Alimentos e Bebidas na ME.

**Figura 10 – Ponto de equilíbrio e receitas de indiferença entre canais, Cenário Atual (2025–2026), MEI e ME**

![Figura 10 – Retas de margem mensal por canal em função da receita por negócio, com os pontos de equilíbrio e os cruzamentos entre canais para MEI e ME](../outputs/graficos/10_ponto_equilibrio_canal.png)

Fonte: elaborado pelo autor com base no painel simulado calibrado (elaboração própria) e em dados do IBGE (2026a, 2026b, 2026d).

Os cruzamentos entre as retas definem três faixas de decisão. No MEI, abaixo de R$ 1.619,18 por mês, o Marketplace deixa mais margem que o Próprio, ou, mais precisamente, perde menos, porque nessa faixa todos os canais estão abaixo do ponto de equilíbrio. Entre R$ 1.619,18 e R$ 5.256,34, o E-commerce Próprio é o mais lucrativo dos três. Acima de R$ 5.256,34, a Loja Física passa à frente. O cruzamento entre Loja Física e Marketplace ocorre em R$ 4.382,43, mas, nesse nível, o Próprio ainda supera os dois. Na ME, as faixas são análogas: o Marketplace vence abaixo de R$ 11.246,39, também numa faixa em que nenhum canal cobre seus custos; o Próprio, entre R$ 11.246,39 e R$ 23.443,58; e a Loja Física, acima disso.

**Tabela 10 – Parâmetros de custo-volume-lucro por porte e canal, Cenário Atual (2025–2026)**

| Porte | Canal | Custo variável v (% da receita) | Custo fixo F (R$ por mês) | Ponto de equilíbrio (R$ por mês) | Receita média por negócio (R$ por mês) | Folga sobre o PE (%) | Margem na receita de referência (R$ por mês) |
|---|---|---|---|---|---|---|---|
| MEI | Loja Física | 64,84 | 1.340,25 | 3.811,80 | 5.149,23 | 35,09 | 274,41 |
| MEI | Marketplace | 85,62 | 429,44 | 2.986,93 | 3.924,84 | 31,40 | 230,80 |
| MEI | E-commerce Próprio | 80,63 | 510,30 | 2.634,34 | 3.719,76 | 41,20 | 379,26 |
| ME | Loja Física | 69,77 | 5.586,80 | 18.480,16 | 21.368,73 | 15,63 | 509,27 |
| ME | Marketplace | 90,35 | 1.347,95 | 13.962,75 | 17.264,55 | 23,65 | 598,73 |
| ME | E-commerce Próprio | 85,55 | 1.887,57 | 13.060,91 | 18.943,46 | 45,04 | 1.026,65 |

Fonte: elaborado pelo autor com base no painel simulado calibrado (elaboração própria); arquivos `outputs/tabelas/cvp_parametros_atual.csv` e `outputs/tabelas/kpis_recorte_canal_porte.csv`.

Nota: F inclui o DAS no MEI; receita de referência = receita média por negócio de todos os canais do porte (R$ 4.592,23 no MEI e R$ 20.164,71 na ME); margem = R × (1 − v) − F.

**Tabela 11 – Receitas de indiferença entre canais, Cenário Atual (2025–2026)**

| Porte | Par de canais | R\* (R$ por mês) | R\* anualizada (em reais) | Fração do teto anual do porte (%) | Melhor abaixo de R\* | Melhor acima de R\* |
|---|---|---|---|---|---|---|
| MEI | Loja Física × Marketplace | 4.382,43 | 52.589,16 | 64,92 | Marketplace | Loja Física |
| MEI | Loja Física × E-commerce Próprio | 5.256,34 | 63.076,08 | 77,87 | E-commerce Próprio | Loja Física |
| MEI | Marketplace × E-commerce Próprio | 1.619,18 | 19.430,16 | 23,99 | Marketplace | E-commerce Próprio |
| ME | Loja Física × Marketplace | 20.599,49 | 247.193,88 | 68,66 | Marketplace | Loja Física |
| ME | Loja Física × E-commerce Próprio | 23.443,58 | 281.322,96 | 78,15 | E-commerce Próprio | Loja Física |
| ME | Marketplace × E-commerce Próprio | 11.246,39 | 134.956,68 | 37,49 | Marketplace | E-commerce Próprio |

Fonte: elaborado pelo autor com base no painel simulado calibrado (elaboração própria), arquivo `outputs/tabelas/receita_indiferenca_canais.csv`, e nos tetos de R$ 81.000 (MEI) e R$ 360.000 (ME) da LC nº 123/2006 (BRASIL, 2006).

Os limiares ganham sentido quando comparados aos tetos legais (Tabela 11). Em termos anuais, a Loja Física só supera o Próprio a partir de R$ 63.076,08 no MEI e de R$ 281.322,96 na ME, o equivalente a 77,87% e 78,15% dos respectivos tetos; a vantagem da loja física aparece, portanto, na faixa alta de faturamento de cada regime, perto do limite em que o MEI precisa migrar para ME. A Loja Física média do MEI fatura R$ 5.149,23 por mês, pouco abaixo de R$ 5.256,34, e, nessa escala, praticamente empata com o canal próprio.

Na receita média por negócio de cada porte, R$ 4.592,23 no MEI e R$ 20.164,71 na ME, o Próprio deixa R$ 379,26 por mês no MEI, contra R$ 274,41 na Loja Física e R$ 230,80 no Marketplace; na ME, deixa R$ 1.026,65, contra R$ 598,73 no Marketplace e R$ 509,27 na Loja Física (Tabela 10). Essa comparação a receita igual isola a economia do canal. As margens realizadas da Tabela 7, ao contrário, misturam o canal com a escala dos negócios que o usam: a Loja Física do MEI tem a maior margem realizada porque seus negócios faturam mais, e não porque o canal seja mais eficiente na mesma receita.

A mesma análise, aplicada às somas da pré-pandemia, mostra como a resposta mudou (Tabela 12). Naquele recorte, o canal próprio já deixava a maior margem na receita média por negócio dos dois portes, mas, no MEI, sua vantagem sobre a loja física era de apenas 0,89 ponto percentual da receita, um empate técnico pelo limiar de materialidade de 1 ponto adotado neste estudo; no Cenário Atual, a vantagem sobre o segundo colocado sobe para 2,28 pontos no MEI e passa de 1,49 para 2,12 pontos na ME. A faixa em que o canal próprio vence também se alargou: no MEI, ia de 0,39 a 1,06 vez a receita média e agora vai de 0,35 a 1,14 vez; na ME, foi de 0,62 a 1,12 vez para 0,56 a 1,16 vez. Duas forças explicam o movimento. O custo variável do marketplace subiu mais que o do canal próprio (de 83,80% para 85,62% da receita no MEI, contra 79,79% e 80,63%), e o custo fixo por negócio da loja física cresceu mais que a receita: equivalia a 25,52% da receita média por negócio do MEI na pré-pandemia e equivale a 29,19% no Cenário Atual, porque acompanha o IPCA, enquanto a receita acompanha os preços das atividades.

**Tabela 12 – Comparação de custo-volume-lucro por porte, Pré-pandemia e Cenário Atual**

| Porte | Recorte | Receita média por negócio (R$ correntes por mês) | Margem na receita média: Loja Física (%) | Margem na receita média: Marketplace (%) | Margem na receita média: E-commerce Próprio (%) | R\* Marketplace × Próprio (múltiplo da receita média) | R\* Loja Física × Próprio (múltiplo da receita média) |
|---|---|---|---|---|---|---|---|
| MEI | Pré-pandemia | 3.638,18 | 9,72 | 8,14 | 10,61 | 0,39 | 1,06 |
| MEI | Cenário Atual | 4.592,23 | 5,98 | 5,03 | 8,26 | 0,35 | 1,14 |
| ME | Pré-pandemia | 15.598,23 | 6,03 | 6,28 | 7,77 | 0,62 | 1,12 |
| ME | Cenário Atual | 20.164,71 | 2,53 | 2,97 | 5,09 | 0,56 | 1,16 |

Fonte: elaborado pelo autor com base no painel simulado calibrado (elaboração própria); somas do arquivo `outputs/tabelas/kpis_recorte_canal_porte.csv`, conferidas, no Cenário Atual, com `outputs/tabelas/cvp_parametros_atual.csv` e `outputs/tabelas/receita_indiferenca_canais.csv`.

Nota: margem = R × (1 − v) − F, em % da receita média por negócio de todos os canais do porte no recorte; R\* expressa como múltiplo dessa receita média, para neutralizar a inflação entre os recortes.

### 4.7 Calibração e robustez

As seis checagens de calibração ficaram dentro das faixas aceitas (Tabela 13). O multiplicador da receita digital nominal entre 2019 e 2024, de 3,64, fica entre o da PAC para empresas maiores (3,21) e o do MDIC para micro e pequenas empresas (13,4), mais perto do primeiro, o que é uma escolha conservadora. A razão entre as participações digitais de 2021 e 2019, de 2,84, supera a da PAC (1,87), coerente com a maior dependência digital do micro varejo. A queda da Loja Física em abril de 2020 (−38,71%) é mais intensa que a do varejo oficial (−19,67%), pelos motivos da seção 4.2, e a receita digital cresce 87,10% no mesmo mês. A participação digital do Cenário Atual (33,31%) e a taxa de intermediação do Marketplace (14,22%) ficam dentro das faixas derivadas do Sebrae e das tarifas do Mercado Livre.

**Tabela 13 – Checagens de calibração do painel simulado**

| Código | Métrica | Valor no painel | Faixa aceita | Referência | Situação |
|---|---|---|---|---|---|
| C1 | Multiplicador da receita digital nominal, 2019 → 2024 | 3,64 | de 3,21 a 13,4 | PAC, empresas com 20 ou mais pessoas ocupadas (217,91 ÷ 67,79); MDIC, micro e pequenas empresas (67 ÷ 5) | OK |
| C2 | Participação digital de 2021 ÷ a de 2019 | 2,84 | de 1,87 a 4,0 | PAC (9,84 ÷ 5,26); teto da faixa definido pelo autor | OK |
| C3 | Variação da receita real da Loja Física, abr/2020 em relação a fev/2020 | −38,71% | igual ou inferior a −15% | PMC, tabela 8880: −19,7% | OK |
| C4 | Variação da receita real digital, abr/2020 em relação a fev/2020 | +87,10% | acima de 0% | migração para o digital (SEBRAE, 2021) | OK |
| C5 | Participação digital no Cenário Atual | 33,31% | de 25% a 45% | um terço dos MEIs on-line com mais da metade do faturamento pela internet (SEBRAE, 2021); faixa definida pelo autor | OK |
| C6 | Taxa de intermediação do Marketplace no Cenário Atual | 14,22% | de 10% a 19% | faixas Clássico (10% a 14%) e Premium (15% a 19%) do Mercado Livre | OK |

Fonte: elaborado pelo autor com base no painel simulado calibrado (elaboração própria); arquivo `outputs/tabelas/calibracao.csv`.

Passar nas checagens não prova que o painel está certo; mostra apenas que ele não contradiz as referências disponíveis. A robustez depende do tipo de conclusão. A ordem dos custos fixos, maior na Loja Física, intermediária no Próprio e menor no Marketplace, decorre da natureza de cada canal e é robusta. A ordem dos custos variáveis depende de dois blocos: a diferença de tarifas, verificada nas fontes, e o gasto com marketing e frete do canal próprio, que é premissa. No MEI, a vantagem de custo variável do Próprio sobre o Marketplace é de apenas 4,99 pontos percentuais (80,63% contra 85,62%), porque a diferença de tarifas (2,82% contra 14,19%) é em parte compensada pelo marketing e pelo frete mais altos do canal próprio. Bastaria um custo variável cerca de 5 pontos maior no Próprio, o equivalente a um gasto com marketing cerca de 45% maior, para que ele deixasse de superar o Marketplace em qualquer faturamento. Um CAC acima da premissa estreitaria, portanto, pelos dois lados a faixa em que o canal próprio vence: o limiar inferior de R$ 1.619,18 subiria, e o superior, de R$ 5.256,34, cairia.

### 4.8 Discussão: o que os dados sustentam e o que é premissa

Três resultados se apoiam diretamente em dados oficiais e em regras verificadas e, por isso, independem do painel: a pandemia acelerou a migração para a Internet, que nas empresas maiores passou de 5,26% para 9,84% da receita entre 2019 e 2021 e depois se estabilizou; o choque de abril de 2020 foi severo e desigual entre atividades, com perda de quase 80% em vestuário e alta em supermercados; e as tarifas dos marketplaces pesam mais nos itens de baixo valor e têm degraus que afetam a precificação.

Os resultados do painel dependem das premissas em graus diferentes. A participação digital de um terço da receita e a compressão das margens são consistentes com as referências de calibração, mas sua magnitude reflete as âncoras de migração e os custos definidos pelo autor. A posição relativa dos canais na análise de custo-volume-lucro combina regras verificadas, como tarifas e impostos, com premissas de marketing, frete e custos fixos; por isso, os limiares devem ser lidos como ordens de grandeza, e não como valores exatos para um negócio específico. Duas leituras pedem cautela adicional. O LTV/CAC alto da Loja Física é, em grande parte, um efeito contábil, porque o custo de atrair o cliente está no aluguel. E a vantagem do marketplace em faturamentos baixos ocorre numa faixa em que todos os canais dão prejuízo; o argumento a favor dele como porta de entrada é o menor custo fixo e o acesso imediato a compradores, fator dinâmico que a análise estática de custo-volume-lucro não captura, porque supõe que o negócio alcançaria a mesma receita em qualquer canal.

Com essas ressalvas, os resultados permitem responder à pergunta de pesquisa. A resposta não é um canal vencedor universal, mas uma regra de decisão que combina porte, segmento e faturamento, apresentada a seguir.

## 5 Conclusão e Recomendação Estratégica

No Cenário Atual (2025–2026), o painel simulado e calibrado indica que o e-commerce próprio é o canal que mais compensa para MEIs e MEs do varejo. Ele é a recomendação isolada em 5 das 10 combinações de porte e segmento e faz parte das outras 4, que são híbridas; está presente, portanto, em 9 das 10 recomendações (Tabela 14). A loja física só vence sozinha em Alimentos e Bebidas, no MEI. O marketplace funciona como porta de entrada e deixa mais margem que o e-commerce próprio apenas abaixo de R$ 1.619,18 por mês no MEI e de R$ 11.246,39 por mês na ME. A loja física só supera o e-commerce próprio acima de R$ 5.256,34 por mês no MEI e de R$ 23.443,58 por mês na ME. Esses resultados valem sob as premissas do painel e devem ser lidos como critérios de decisão, e não como previsão para um negócio específico.

**Tabela 14 – Matriz de recomendação por porte e segmento, Cenário Atual (2025–2026)**

| Porte | Segmento | 1º canal (margem, R$ por mês) | 2º canal (margem, R$ por mês) | Vantagem (p.p. da receita de referência) | Recomendação |
|---|---|---|---|---|---|
| MEI | Moda e Acessórios | E-commerce Próprio (604,72) | Marketplace (506,82) | 2,05 | E-commerce Próprio |
| MEI | Casa e Decoração | E-commerce Próprio (335,16) | Marketplace (275,51) | 1,37 | E-commerce Próprio |
| MEI | Eletrônicos e Acessórios | E-commerce Próprio (234,05) | Loja Física (41,19) | 5,17 | E-commerce Próprio |
| MEI | Beleza e Cuidados Pessoais | Loja Física (196,69) | E-commerce Próprio (195,22) | 0,03 | Híbrido: Loja Física + E-commerce Próprio |
| MEI | Alimentos e Bebidas | Loja Física (584,66) | E-commerce Próprio (495,54) | 1,56 | Loja Física |
| ME | Moda e Acessórios | E-commerce Próprio (1.916,10) | Marketplace (1.613,79) | 1,46 | E-commerce Próprio |
| ME | Casa e Decoração | Marketplace (978,84) | E-commerce Próprio (836,55) | 0,74 | Híbrido: Marketplace + E-commerce Próprio |
| ME | Eletrônicos e Acessórios | E-commerce Próprio (713,22) | Loja Física (−134,28) | 5,05 | E-commerce Próprio |
| ME | Beleza e Cuidados Pessoais | E-commerce Próprio (253,03) | Loja Física (237,63) | 0,08 | Híbrido: E-commerce Próprio + Loja Física |
| ME | Alimentos e Bebidas | Loja Física (1.421,38) | E-commerce Próprio (1.232,48) | 0,76 | Híbrido: Loja Física + E-commerce Próprio |

Fonte: elaborado pelo autor com base no painel simulado calibrado (elaboração própria); arquivo `outputs/tabelas/matriz_recomendacao.csv`.

Nota: margem estimada na receita média por negócio do porte e do segmento, com margem = R × (1 − v) − F; recomenda-se o 1º canal quando a vantagem sobre o 2º é de pelo menos 1,0 ponto percentual dessa receita (limiar de materialidade definido pelo autor); abaixo disso, a recomendação é híbrida.

A loja física compensa na faixa alta de faturamento de cada regime, perto de 78% do teto anual, e em segmentos de compra frequente e local, como Alimentos e Bebidas, em que a retenção mensal da loja física do MEI chega a 44,00% no Cenário Atual. É o canal de maior margem líquida realizada no MEI (9,13%), mas também o de maior custo fixo e de maior ponto de equilíbrio (R$ 3.811,80 por mês no MEI e R$ 18.480,16 na ME), e o mais exposto a choques como o de 2020, quando sua margem mensal agregada chegou a −8,92% no painel. Para quem já tem ponto e clientela de bairro, a loja continua valiosa; para quem ainda não tem, abrir um ponto só faz sentido quando o faturamento esperado supera com folga as receitas de indiferença.

O marketplace é a porta de entrada. Tem o menor custo fixo (R$ 429,44 por mês no MEI) e dá acesso imediato a compradores, mas a taxa de intermediação de 14,22%, o frete subsidiado e a retenção de 9,42% comprimem a margem para 3,44% no MEI e 1,85% na ME. Compensa nos primeiros meses, para validar produto e preço com pouco capital, e em faturamentos baixos, nos quais nenhum canal ainda cobre seus custos. Em itens de R$ 30 a R$ 50, as tarifas fixas elevam o custo efetivo para 24% a 35% no Mercado Livre e na Shopee (Tabela 9), o que exige atenção ao preço e ao tamanho do pedido. Em Casa e Decoração, na ME, o marketplace lidera por pequena diferença e forma com o canal próprio uma recomendação híbrida: o maior ticket do marketplace entre os segmentos da ME (R$ 146,11) reduz o peso da tarifa fixa e leva a taxa de intermediação a 12,96%, abaixo da média do canal, enquanto o canal próprio desse segmento tem o maior CAC entre as 30 combinações do Cenário Atual (R$ 36,12).

O e-commerce próprio tem o menor ponto de equilíbrio (R$ 2.634,34 por mês no MEI e R$ 13.060,91 na ME) e a maior folga sobre ele (41,20% e 45,04%) e é o mais lucrativo na faixa intermediária de faturamento, onde estão os negócios médios dos dois portes. Seu custo está no marketing, com CAC de R$ 27,53, e no frete; por isso, ele só se paga com recompra, e a retenção de 30,66% e o LTV de R$ 68,10 sustentam o resultado. É também o canal mais sensível às premissas, pois um CAC muito maior que o modelado reduziria a faixa em que ele vence (seção 4.7). Nos quatro casos de empate técnico, com vantagem menor que 1 ponto percentual da receita, combinar canais reduz o risco sem sacrificar margem relevante: Beleza e Cuidados Pessoais nos dois portes e Alimentos e Bebidas na ME pedem loja física e canal próprio, e Casa e Decoração na ME pede marketplace e canal próprio.

Desses resultados decorre uma recomendação por estágio do negócio. Na entrada, com faturamento de até R$ 1.619,18 por mês no MEI ou de até R$ 11.246,39 na ME, o marketplace é a forma de menor risco para validar sortimento, preço e demanda, desde que a tarifa por item não consuma a margem dos produtos baratos. Na fase de tração, entre esses limiares e os de R$ 5.256,34 (MEI) e R$ 23.443,58 (ME), o negócio deve levar os clientes recorrentes para o canal próprio (WhatsApp, redes sociais ou loja virtual), com Pix como meio de pagamento preferencial e investimento em retenção, mantendo o marketplace como fonte de clientes novos. Na fase de escala, acima desses limiares, a loja física ou a operação com vários canais integrados passam a compensar, sobretudo em segmentos de alta retenção e compra local. No MEI, essa faixa coincide com a proximidade do teto, e a migração para ME troca o DAS fixo por um imposto proporcional à receita; no painel, a margem líquida do conjunto é de 7,33% no MEI e de 3,72% na ME, diferença em que pesam esse imposto e os custos fixos maiores da ME, e por isso a mudança de porte precisa ser planejada junto com a de canal.

As principais limitações do estudo são a natureza simulada das medidas por canal, a cobertura das pesquisas oficiais, restrita a empresas com 20 ou mais pessoas ocupadas, a hipótese de um canal principal por negócio e as premissas de CAC, retenção e custos fixos. Como trabalhos futuros, propõe-se substituir o painel por dados reais de vendas de MEIs e MEs, obtidos com consentimento junto a plataformas de gestão ou parceiros; medir CAC e retenção efetivos com testes controlados entre canais; modelar negócios com vários canais simultâneos e rateio de custos fixos; incluir desconto financeiro no LTV e análise de sensibilidade sistemática das premissas; e incorporar a contagem oficial de MEIs e os dados abertos do Pix quando houver acesso estável.

Em resposta à pergunta de pesquisa, conclui-se que, no cenário de 2025–2026 e sob as premissas do painel simulado e calibrado, o e-commerce próprio é o canal que mais compensa para MEIs e MEs do varejo, presente em 9 das 10 recomendações por porte e segmento. O marketplace se justifica como porta de entrada e só deixa mais margem que o canal próprio abaixo de R$ 1.619,18 por mês no MEI e de R$ 11.246,39 na ME; a loja física só supera o canal próprio acima de R$ 5.256,34 por mês no MEI e de R$ 23.443,58 na ME, perto do teto de cada regime, e vence sozinha apenas em Alimentos e Bebidas no MEI. Em relação à pré-pandemia, a resposta mudou em intensidade, e não em direção: o canal próprio já liderava na receita média por negócio, mas por margem estreita, e no Cenário Atual sua vantagem e a faixa de faturamento em que vence aumentaram; ao mesmo tempo, o digital passou de 10,31% a 33,31% da receita real, e as margens ficaram mais estreitas em todos os canais. Por isso, a escolha do canal, e o momento de mudar de canal, tornaram-se mais decisivos para o resultado do microempreendedor.

## Referências

AMAZON. **Quanto custa vender na Amazon?**: comissões de 10% a 15%. [*S. l.*]: Amazon, [2026]. Disponível em: https://venda.amazon.com.br/precos. Acesso em: 18 out. 2026.

BERGER, Paul D.; NASR, Nada I. Customer lifetime value: marketing models and applications. **Journal of Interactive Marketing**, [*s. l.*], v. 12, n. 1, p. 17-30, 1998. DOI: 10.1002/(SICI)1520-6653(199824)12:1&lt;17::AID-DIR3&gt;3.0.CO;2-K. Disponível em: https://doi.org/10.1002/(SICI)1520-6653(199824)12:1%3C17::AID-DIR3%3E3.0.CO;2-K. Acesso em: 18 out. 2026.

BRASIL. Lei nº 8.212, de 24 de julho de 1991. Dispõe sobre a organização da Seguridade Social, institui Plano de Custeio, e dá outras providências. Brasília, DF: Presidência da República, 1991. Disponível em: https://www.planalto.gov.br/ccivil_03/leis/l8212cons.htm. Acesso em: 18 out. 2026.

BRASIL. Lei Complementar nº 123, de 14 de dezembro de 2006. Institui o Estatuto Nacional da Microempresa e da Empresa de Pequeno Porte [...]. Brasília, DF: Presidência da República, 2006. Disponível em: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp123.htm. Acesso em: 18 out. 2026.

BRASIL. Lei Complementar nº 155, de 27 de outubro de 2016. Altera a Lei Complementar nº 123, de 14 de dezembro de 2006, para reorganizar e simplificar a metodologia de apuração do imposto devido por optantes pelo Simples Nacional [...]. Brasília, DF: Presidência da República, 2016. Disponível em: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp155.htm. Acesso em: 18 out. 2026.

BRASIL. Lei nº 14.902, de 27 de junho de 2024. Institui o Programa Mobilidade Verde e Inovação (Programa Mover); altera o Decreto-Lei nº 1.804, de 3 de setembro de 1980 [...]. Brasília, DF: Presidência da República, 2024. Disponível em: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/lei/l14902.htm. Acesso em: 18 out. 2026.

BRASIL. Ministério da Saúde. Portaria nº 188, de 3 de fevereiro de 2020. Declara Emergência em Saúde Pública de importância Nacional (ESPIN) em decorrência da Infecção Humana pelo novo Coronavírus (2019-nCoV). **Diário Oficial da União**: seção 1, Brasília, DF, n. 24-A, p. 1, 4 fev. 2020. Disponível em: https://bvsms.saude.gov.br/bvs/saudelegis/gm/2020/prt0188_04_02_2020.html. Acesso em: 18 out. 2026.

BRASIL. Ministério da Saúde. Portaria GM/MS nº 913, de 22 de abril de 2022. Declara o encerramento da Emergência em Saúde Pública de Importância Nacional (ESPIN) em decorrência da infecção humana pelo novo coronavírus (2019-nCoV) [...]. **Diário Oficial da União**: seção 1, Brasília, DF, ed. 75-E, p. 1, 22 abr. 2022. Disponível em: https://www.in.gov.br/en/web/dou/-/portaria-gm/ms-n-913-de-22-de-abril-de-2022-394545491. Acesso em: 18 out. 2026.

BRASIL. Ministério do Desenvolvimento, Indústria, Comércio e Serviços. **Vendas de pequenas empresas pela internet crescem 1.200% desde a pandemia, mostra painel do MDIC**. Brasília, DF: MDIC, 24 jun. 2025. Disponível em: https://web.archive.org/web/20250724114021/https://www.gov.br/mdic/pt-br/assuntos/noticias/2025/junho/vendas-de-pequenas-empresas-pela-internet-crescem-1-200-desde-a-pandemia-mostra-painel-do-mdic. Acesso em: 18 out. 2026.

BRASIL. Receita Federal. **Programa Remessa Conforme**: o que é? Como funciona? Brasília, DF: RFB, [2026]. Disponível em: https://www.gov.br/receitafederal/pt-br/assuntos/aduana-e-comercio-exterior/manuais/remessas-postal-e-expressa/programa-remessa-conforme-o-que-e-como-funciona. Acesso em: 18 out. 2026.

GOMES, André Luiz. Vendas dos pequenos negócios no comércio eletrônico crescem 76% em três anos. **Agência Sebrae de Notícias**, [*s. l.*], 3 jul. 2025. Disponível em: https://agenciasebrae.com.br/economia-e-politica/vendas-dos-pequenos-negocios-no-comercio-eletronico-crescem-76-em-tres-anos/. Acesso em: 18 out. 2026.

GUPTA, Sunil; LEHMANN, Donald R.; STUART, Jennifer Ames. Valuing customers. **Journal of Marketing Research**, [*s. l.*], v. 41, n. 1, p. 7-18, 2004. DOI: 10.1509/jmkr.41.1.7.25084. Disponível em: https://doi.org/10.1509/jmkr.41.1.7.25084. Acesso em: 18 out. 2026.

IBGE. **Índice Nacional de Preços ao Consumidor Amplo**: tabela 1737. Rio de Janeiro: IBGE, 2026a. Disponível em: https://sidra.ibge.gov.br/tabela/1737. Acesso em: 18 out. 2026.

IBGE. **Pesquisa Anual de Comércio**: tabelas 9349, 10645 e 10656. Rio de Janeiro: IBGE, 2026b. Disponível em: https://sidra.ibge.gov.br/tabela/9349, https://sidra.ibge.gov.br/tabela/10645 e https://sidra.ibge.gov.br/tabela/10656. Acesso em: 18 out. 2026.

IBGE. **Pesquisa Mensal de Comércio**: metadados (população-alvo). Rio de Janeiro: IBGE, 2026c. Disponível em: https://servicodados.ibge.gov.br/api/v2/metadados/MC/2026/1. Acesso em: 18 out. 2026.

IBGE. **Pesquisa Mensal de Comércio**: tabelas 8880 e 8882 (2022 = 100). Rio de Janeiro: IBGE, 2026d. Disponível em: https://sidra.ibge.gov.br/tabela/8880 e https://sidra.ibge.gov.br/tabela/8882. Acesso em: 18 out. 2026.

INSTITUTO DE PESQUISA ECONÔMICA APLICADA. **Ipeadata**: salário mínimo vigente (série MTE12_SALMIN12). Brasília, DF: Ipea, 2026. Disponível em: http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='MTE12_SALMIN12'). Acesso em: 18 out. 2026.

JOVCHELEVICH, Roberta. Sebrae lança mapeamento inédito de marketplaces na maior feira de e-commerce da América Latina. **Agência Sebrae de Notícias**, [*s. l.*], 2 ago. 2024. Disponível em: https://agenciasebrae.com.br/inovacao-e-tecnologia/sebrae-lanca-mapeamento-inedito-de-marketplaces-na-maior-feira-de-e-commerce-da-america-latina/. Acesso em: 18 out. 2026.

MERCADO LIVRE. **Quanto custa vender um produto?** [*S. l.*]: Mercado Livre, [2026]. Disponível em: https://www.mercadolivre.com.br/ajuda/quanto-custa-vender-um-produto_1338. Acesso em: 18 out. 2026. Versões históricas consultadas no Internet Archive (https://web.archive.org/), cópias de 26 jun. 2018, 4 jan. 2019, 1 nov. 2019, 30 jul. 2020, 12 out. 2020, 16 fev. 2021, 24 abr. 2021, 3 fev. 2022, 28 set. 2022, 27 mar. 2023 e 17 jan. 2024.

NUVEMSHOP. **Planos e preços**. [*S. l.*]: Nuvemshop, [2026]. Disponível em: https://www.nuvemshop.com.br/planos-e-precos. Acesso em: 18 out. 2026.

OLIVEIRA, Kelly. Pix: novo sistema de pagamento instantâneo entra em funcionamento. **Agência Brasil**, Brasília, DF, 16 nov. 2020. Disponível em: https://agenciabrasil.ebc.com.br/economia/noticia/2020-11/pix-novo-sistema-de-pagamento-instantaneo-entra-em-funcionamento. Acesso em: 18 out. 2026.

ORGANIZAÇÃO PAN-AMERICANA DA SAÚDE. **OMS afirma que COVID-19 é agora caracterizada como pandemia**. [*S. l.*]: OPAS, 11 mar. 2020. Disponível em: https://www.paho.org/pt/news/11-3-2020-who-characterizes-covid-19-pandemic. Acesso em: 18 out. 2026.

SEBRAE. Vendas online representam mais da metade do faturamento de 30% dos MEI. **Agência Sebrae de Notícias**, [*s. l.*], 14 jul. 2021. Disponível em: https://agenciasebrae.com.br/inovacao-e-tecnologia/vendas-online-representam-mais-da-metade-do-faturamento-de-30-dos-mei/. Acesso em: 18 out. 2026.

SHOPEE. **Como funciona a Política de Comissão para vendedores da Shopee?** Centro de Educação do Vendedor. [*S. l.*]: Shopee, 1 mar. 2026a. Atualizado em: 1 out. 2026. Disponível em: https://seller.shopee.com.br/edu/article/18483/como-funciona-a-politica-de-comissao-para-vendedores-shopee. Acesso em: 18 out. 2026.

SHOPEE. **Confira a Política de Comissão para vendedores CNPJ e CPF**. Centro de Educação do Vendedor. [*S. l.*]: Shopee, 18 set. 2026b. Atualizado em: 1 out. 2026. Disponível em: https://seller.shopee.com.br/edu/article/26839/Comissao-para-vendedores-CNPJ-e-CPF-em-2026. Acesso em: 18 out. 2026.

TIKTOK. **TikTok Shop chega ao Brasil e inaugura a era da Compra por Descoberta**. [*S. l.*]: TikTok, 8 maio 2025. Disponível em: https://newsroom.tiktok.com/pt-br/tiktok-shop-chega-ao-brasil. Acesso em: 18 out. 2026.
