\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{icpc}[2026/11/08 Classe LaTeX no visual do caderno da Maratona SBC (PT-BR)]

% Implementa o contrato de macros do ds-contest-tools (docs/spec-formatos-pdf.md §5).
% O gerador emite sempre a mesma marcacao; esta classe decide a aparencia.
%
% Referencia visual: caderno da Maratona SBC de Programacao 2026, primeira
% fase, paginas dos problemas (docs/plano-formato-icpc-sbc.md §2). Capa,
% cabecalho com logos e rodape ficam de fora. As medidas citadas em bp foram
% tiradas desse PDF; as constantes abaixo foram calibradas contra elas.

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

\LoadClass[a4paper, 11pt]{article}

% Codificacao OT1 (padrao), como na referencia: Computer Modern Type 1, sem
% depender do cm-super (DEC-3).
\RequirePackage[utf8]{inputenc}
\RequirePackage[brazil]{babel}
% Texto de 73,70 a 521,58 bp (2,6 cm de cada lado). O topo do texto fica em
% 72 bp; a altura reproduz as quebras de pagina da referencia (CA-14).
\RequirePackage[a4paper, hmargin=2.6cm, top=2.54cm, textheight=710.14pt]{geometry}
\RequirePackage{amsmath, amssymb, amsthm}
\RequirePackage{graphicx}
\RequirePackage{url}
\RequirePackage{seqsplit}
\RequirePackage{ifthen}

% Cabecalho e rodape estao fora do escopo (DEC-5).
\pagestyle{empty}

\setlength{\parindent}{0pt}
% Rigido: na referencia, o espaco entre paragrafos nao encolhe nem nas
% paginas comprimidas.
\setlength{\parskip}{5pt}

% Marcadores de lista em CMSY (Type 1). O padrao do LaTeX tira o
% \textbullet e o \textperiodcentered da codificacao TS1, que sem o cm-super
% sai como fonte bitmap (Type 3). Mesmo glifo, mesma posicao do texto.
\renewcommand{\labelitemi}{\ensuremath{\bullet}}
\renewcommand{\labelitemiv}{\ensuremath{\cdot}}

% ---------------------------------------------------------------------------
% Rotulos
%
% Sobrescreva no .tex para trocar de idioma:
%     \renewcommand{\NomeEntrada}{Input}
% ---------------------------------------------------------------------------
\newcommand{\NomeProblema}{Problema}
\newcommand{\NomeEntrada}{Entrada}
\newcommand{\NomeSaida}{Saída}
\newcommand{\NomeInteracao}{Interação}
\newcommand{\NomeNotas}{Notas}
\newcommand{\NomeExemploEntrada}{Exemplo de entrada}
\newcommand{\NomeExemploSaida}{Exemplo de saída}
\newcommand{\NomeTutorial}{Tutorial}
\newcommand{\NomeAutor}{Autor}
\newcommand{\NomeLimiteTempo}{Limite de tempo}
\newcommand{\NomeLimiteMemoria}{Limite de memória}

% Teste de vazio com \detokenize (DEC-7). Um \ifx compararia so os dois
% primeiros tokens: um autor "LLUIS Vidal" passaria por vazio.
\newcommand{\icpc@sevazio}[3]{%
    \if\relax\detokenize{#1}\relax
        \expandafter\@firstoftwo
    \else
        \expandafter\@secondoftwo
    \fi{#2}{#3}%
}

% ---------------------------------------------------------------------------
% Cabecalho do problema e do tutorial
%
% Titulo centralizado em \LARGE\sffamily (CMSS17), com dois espacos de cada
% lado do travessao: "Problema A  --  Titulo". Abaixo dele, cada item opcional
% (tempo, memoria, autor) ocupa uma linha propria e so aparece com valor
% (argumento vazio = nao exibir, DEC-9 e DEC-10). Cada item leva consigo o
% espaco que o separa do anterior.
%
% Na referencia, a linha-base do titulo acompanha a altura do proprio titulo
% (um acento mais alto desce a pagina toda), e a do primeiro paragrafo fica
% 30,87 pt abaixo dela. Para reproduzir isso, o \vspace* insere no topo uma
% regua invisivel (que o topo da pagina nao descarta), e o \nointerlineskip
% faz o titulo encostar no espaco acima sem entrelinha: a linha-base fica em
% \topskip + \icpc@topo + \parskip + altura do titulo.
% ---------------------------------------------------------------------------
\newlength{\icpc@topo}
\setlength{\icpc@topo}{-9.24pt}
\newlength{\icpc@depoistitulo}
\setlength{\icpc@depoistitulo}{12.27pt}

\newcommand{\icpc@item}[2]{% #1 decide se aparece; #2 e o texto
    \icpc@sevazio{#1}{}{{\centering\small\setlength{\parskip}{2pt}#2\par}}%
}

% #1 titulo ja montado, #2 tempo, #3 memoria, #4 autor.
\newcommand{\icpc@cabecalho}[4]{%
    \clearpage
    \vspace*{\icpc@topo}%
    \nointerlineskip
    {\centering\LARGE\sffamily #1\par}%
    \icpc@item{#2}{\NomeLimiteTempo: #2~s}%
    \icpc@item{#3}{\NomeLimiteMemoria: #3~MB}%
    \icpc@item{#4}{\itshape\NomeAutor: #4}%
    \vspace{\icpc@depoistitulo}%
}

% #1 rotulo, #2 titulo. Sem rotulo, so o titulo.
\newcommand{\icpc@titulo}[2]{%
    \icpc@sevazio{#1}{#2}{\NomeProblema\ #1\ \ --\ \ #2}%
}

\newenvironment{Problema}[4]{%
    \icpc@cabecalho{\icpc@titulo{#1}{#2}}{#3}{#4}{}%
    \ignorespaces
}{\par}

\newenvironment{ProblemaAutor}[5]{%
    \icpc@cabecalho{\icpc@titulo{#1}{#2}}{#3}{#4}{#5}%
    \ignorespaces
}{\par}

% Cabecalho e rodape estao fora do escopo. A macro existe porque o contrato
% exige que esteja definida, nao que produza saida (DEC-5).
\newcommand{\Evento}[1]{}

% ---------------------------------------------------------------------------
% Secoes
%
% \large\bfseries (CMBX12), sem numero. Na referencia: da linha-base anterior
% a do titulo da secao, 25 pt (6 pt + \parskip + 14 pt de entrelinha); do
% titulo ao texto, 22,6 pt (4 pt + \parskip + 13,6 pt). O espaco antes e um
% \addvspace: depois de uma lista, funde com o \topsep (9 pt) em vez de
% somar, e da os 28 pt medidos. So ele encolhe nas paginas comprimidas.
% ---------------------------------------------------------------------------
\newcommand{\icpc@secao}[1]{%
    \@startsection{subsection}{2}{\z@}{-6pt \@minus -3pt}{4pt}%
        {\normalfont\large\bfseries}*{#1}%
}

\newcommand{\Entrada}{\icpc@secao{\NomeEntrada}}
\newcommand{\Saida}{\icpc@secao{\NomeSaida}}
\newcommand{\Interacao}{\icpc@secao{\NomeInteracao}}
\newcommand{\Notas}{\icpc@secao{\NomeNotas}}

% A referencia nao tem titulo de secao para os exemplos: a tabela vem logo
% depois do texto da saida. No-op deliberado.
\newcommand{\ExemploEntrada}{}

% ---------------------------------------------------------------------------
% Exemplos: uma tabela por caso
%
% O gerador emite um modelo de LINHAS DE TABELA:
%
%     \begin{Exemplo}\CasoExemplo
%     \LinhaExemplo{entrada linha 1}{saida linha 1}
%     \LinhaExemplo{entrada linha 2}{}
%     \CasoExemplo
%     ...
%     \end{Exemplo}
%
% A referencia mostra, para cada caso, uma tabela de duas colunas com a
% entrada e a saida INDEPENDENTES: uma linha longa da entrada que quebra nao
% empurra a saida para baixo. Por isso as colunas sao acumuladas ao longo do
% caso e a tabela sai quando o caso termina, em \CasoExemplo (que fecha o
% anterior) e em \end{Exemplo} (que fecha o ultimo). Mesma tecnica do
% atcoder.cls (DEC-4).
%
% Linhas vazias sao ADIADAS: o gerador preenche com vazio o lado mais curto
% do par, e emitir esse preenchimento deixaria linhas em branco no fim da
% coluna. Adiando, uma linha vazia so aparece se houver conteudo depois dela.
% ---------------------------------------------------------------------------
\newcounter{icpc@caso}
\newcounter{icpc@pendentradas}
\newcounter{icpc@pendsaidas}
\newif\ificpc@temcaso

\newcommand{\icpc@entrada}{}
\newcommand{\icpc@saida}{}

% Largura de cada coluna. Na tabular padrao do LaTeX, as reguas verticais nao
% ocupam largura (ficam centradas na divisa); medida na referencia, a coluna
% tem 0,5\textwidth - 2\tabcolsep - \arrayrulewidth, e a tabela comeca na
% margem esquerda.
\newlength{\icpc@coluna}
% Espaco antes da primeira tabela e entre tabelas. Somam-se ao \parskip, ao
% \lineskip e a profundidade da linha anterior, como na referencia.
\newlength{\icpc@antesprimeira}
\setlength{\icpc@antesprimeira}{12pt}
\newlength{\icpc@entretabelas}
\setlength{\icpc@entretabelas}{8pt}
% Folga entre o rotulo e a primeira linha de dados (12 pt + ela = 18,29 pt
% entre as linhas-base) e entre a ultima linha e a regua inferior.
\newlength{\icpc@folgarotulo}
\setlength{\icpc@folgarotulo}{6.29pt}
\newlength{\icpc@folgafim}
\setlength{\icpc@folgafim}{2.42pt}

% Uma linha de dado. O \strut fixa o passo de 12 pt e da altura a linha vazia;
% o \seqsplit permite quebrar dentro da coluna, ja que o gerador troca os
% espacos por "~" para preserva-los.
\newcommand{\icpc@linhadado}[1]{\strut\seqsplit{#1}}

\newcommand{\icpc@reinicia}{%
    \gdef\icpc@entrada{}\gdef\icpc@saida{}%
    \setcounter{icpc@pendentradas}{0}\setcounter{icpc@pendsaidas}{0}%
}

% As linhas de uma coluna sao paragrafos da celula p{}. O \par vai ENTRE as
% linhas, nunca depois da ultima: a celula termina com o \@finalstrut do
% LaTeX, que em modo vertical abriria uma linha vazia a mais.
% #1 acumulador, #2 linha ja montada.
\newcommand{\icpc@acrescenta}[2]{%
    \ifx#1\@empty\else\g@addto@macro#1{\par}\fi
    \g@addto@macro#1{#2}%
}

% #1 acumulador, #2 contador de vazias pendentes, #3 linha.
\newcommand{\icpc@empilha}[3]{%
    \icpc@sevazio{#3}%
        {\stepcounter{#2}}%
        {\whiledo{\value{#2}>0}%
            {\icpc@acrescenta#1{\strut}\addtocounter{#2}{-1}}%
         \icpc@acrescenta#1{\icpc@linhadado{#3}}}%
}

% Os escapes do gerador, redefinidos so dentro da celula, para usar os glifos
% ASCII da propria CMTT10 (DEC-3). Em OT1, \textless sairia em CMMI10, a barra
% invertida e as chaves em CMSY10, \_ viraria uma regua, e \$ viria da
% codificacao TS1, que sem o cm-super sai como fonte bitmap (Type 3).
\newcommand{\icpc@escapes}{%
    \def\${\char`\$}%
    \def\textless{\char`\<}%
    \def\textgreater{\char`\>}%
    \def\textbackslash{\char`\\}%
    \def\{{\char`\{}%
    \def\}{\char`\}}%
    \def\_{\char`\_}%
    \def\textasciicircum{\char`\^}%
}

% A folga final vai numa regua invisivel presa a ULTIMA linha da celula, e
% nao num \\[...] no fim da linha da tabela: numa celula p{} de varias
% linhas, o \\[...] e medido a partir da primeira linha e nao teria efeito.
\newcommand{\icpc@celula}[1]{%
    \ttfamily\icpc@escapes#1%
    \vrule\@width\z@\@depth\dimexpr\dp\@arstrutbox + \icpc@folgafim\relax
}

% A tabela e uma caixa dentro de um paragrafo, como na referencia: o espaco
% antes dela soma \parskip, \lineskip e a profundidade da linha anterior. A
% tabular nunca se divide entre paginas: o caso inteiro vai para a seguinte.
\newcommand{\icpc@tabela}{%
    \par
    \ifnum\value{icpc@caso}=\@ne
        \addvspace{\icpc@antesprimeira}%
    \else
        \addvspace{\icpc@entretabelas}%
    \fi
    \setlength{\icpc@coluna}{\dimexpr 0.5\textwidth - 2\tabcolsep - \arrayrulewidth\relax}%
    \noindent
    {\small
     \begin{tabular}{|p{\icpc@coluna}|p{\icpc@coluna}|}
         \hline
         \textbf{\NomeExemploEntrada\ \theicpc@caso} &
         \textbf{\NomeExemploSaida\ \theicpc@caso} \\[\icpc@folgarotulo]
         \icpc@celula{\icpc@entrada} & \icpc@celula{\icpc@saida} \\
         \hline
     \end{tabular}\par}%
}

\newcommand{\icpc@descarrega}{%
    \ificpc@temcaso \icpc@tabela \fi
}

\newcommand{\CasoExemplo}{%
    \icpc@descarrega
    \stepcounter{icpc@caso}%
    \icpc@reinicia
    \global\icpc@temcasotrue
    \ignorespaces
}

\newcommand{\LinhaExemplo}[2]{%
    \icpc@empilha{\icpc@entrada}{icpc@pendentradas}{#1}%
    \icpc@empilha{\icpc@saida}{icpc@pendsaidas}{#2}%
    \ignorespaces
}

% \begin{Exemplo}\end{Exemplo} sem casos nao emite nada.
\newenvironment{Exemplo}{%
    \setcounter{icpc@caso}{0}%
    \global\icpc@temcasofalse
    \icpc@reinicia
    \ignorespaces
}{%
    \icpc@descarrega
    \global\icpc@temcasofalse
}

% ---------------------------------------------------------------------------
% Tutorial (editorial do problema)
%
% O gerador emite \begin{Tutorial}{titulo}{autor} + \input + \end{Tutorial}.
% Mesmo cabecalho do enunciado; linha de autor so com autor nao vazio.
% ---------------------------------------------------------------------------
\newenvironment{Tutorial}[2]{%
    \icpc@cabecalho{\NomeTutorial: #1}{}{}{#2}%
    \ignorespaces
}{\par}
