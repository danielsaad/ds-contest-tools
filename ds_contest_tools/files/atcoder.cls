\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{atcoder}[2026/09/04 Classe LaTeX baseada no visual do AtCoder (PT-BR)]

% Implementa o contrato de macros do ds-contest-tools (docs/spec-formatos-pdf.md §5).
% O gerador emite sempre a mesma marcacao; esta classe decide a aparencia.

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

\LoadClass[11pt, a4paper]{article}

\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage{helvet}
\renewcommand{\familydefault}{\sfdefault}

\RequirePackage[left=2.2cm, right=2.2cm, top=2.2cm, bottom=2.2cm]{geometry}
\RequirePackage{xcolor}
\RequirePackage[most]{tcolorbox}
\RequirePackage{enumitem}
\RequirePackage{amsmath, amssymb, amsthm}
\RequirePackage{url}
\RequirePackage{needspace}
\RequirePackage{ifthen}

\pagestyle{empty}

\setlength{\parindent}{0pt}
\setlength{\parskip}{0.55em}
\linespread{1.08}

% -- Paleta -----------------------------------------------------------------
% Aproximada a partir da apresentacao do AtCoder.
\definecolor{atbg}{HTML}{F8F9FA}      % fundo dos blocos de exemplo
\definecolor{atborder}{HTML}{DEE2E6}  % borda dos blocos
\definecolor{atline}{HTML}{DEE2E6}    % reguas separadoras
\definecolor{attext}{HTML}{1A1A1A}    % corpo do texto
\definecolor{atlimits}{HTML}{A03B3B}  % linha de limites, em vermelho escuro

\color{attext}

\newtcolorbox{atcoderbox}{
    colback=atbg,
    colframe=atborder,
    boxrule=0.5pt,
    arc=1pt,
    boxsep=1pt,
    left=8pt, right=8pt, top=7pt, bottom=7pt,
    fontupper=\ttfamily\small,
    width=\linewidth,
    before skip=0.35em, after skip=0.6em
}

% \addvspace, e nao \vspace: funde com o espaco vertical ja acumulado em vez
% de somar. Sem isso, uma regua depois de uma lista ou de uma caixa abre um
% buraco de duas linhas.
\newcommand{\atcoderline}{%
    \par\addvspace{0.7em}%
    \noindent\textcolor{atline}{\rule{\linewidth}{0.8pt}}%
    \par\vspace{0.1em}%
}

\newcommand{\atcodersection}[1]{%
    \par\needspace{5\baselineskip}%
    \addvspace{0.35em}%
    {\Large\bfseries #1}\par\nobreak\vspace{0.3em}\nobreak
}

% ---------------------------------------------------------------------------
% Rotulos das secoes
%
% Sobrescreva no .tex para trocar de idioma:
%     \renewcommand{\NomeEntrada}{Input}
% ---------------------------------------------------------------------------
\newcommand{\NomeDescricao}{Descrição do Problema}
\newcommand{\NomeEntrada}{Entrada}
\newcommand{\NomeSaida}{Saída}
\newcommand{\NomeInteracao}{Interação}
\newcommand{\NomeNotas}{Notas}
\newcommand{\NomeExemploEntrada}{Exemplo de Entrada}
\newcommand{\NomeExemploSaida}{Exemplo de Saída}
\newcommand{\NomeTutorial}{Tutorial}
\newcommand{\NomeLimiteTempo}{Limite de Tempo}
\newcommand{\NomeLimiteMemoria}{Limite de Memória}

% ---------------------------------------------------------------------------
% Cabecalho do problema
%
% O gerador emite \begin{Problema}{rotulo}{titulo}{tempo}{memoria} ou
% \begin{ProblemaAutor}{...}{...}{...}{...}{autor}. O rotulo entra como
% prefixo do titulo ("A - Titulo"), como no AtCoder; o autor e recebido e
% deliberadamente nao exibido, porque a apresentacao de referencia nao o
% mostra.
% ---------------------------------------------------------------------------
\newcommand{\atc@autor}{}

% Linha de limites. Argumento vazio = não exibir: o gerador envia tempo e
% memória vazios quando a configuração manda ocultá-los. Sem nenhum dos dois,
% a linha some inteira, com o espaço que a acompanha; o separador " / " só
% aparece com os dois presentes.
\newcommand{\atc@limites}[2]{%
    \atc@sevazio{#1#2}{}{%
        {\small\textcolor{atlimits}{%
            \atc@sevazio{#1}{}{\NomeLimiteTempo: #1\ seg}%
            \atc@sevazio{#1}{}{\atc@sevazio{#2}{}{\ /\ }}%
            \atc@sevazio{#2}{}{\NomeLimiteMemoria: #2\ MiB}}}%
        \par\vspace{0.4em}}%
}

\newcommand{\atc@cabecalho}[4]{%
    {\LARGE\bfseries
        \ifthenelse{\equal{#1}{}}{#2}{#1\ -\ #2}%
    }\par
    \atcoderline
    \atc@limites{#3}{#4}%
    \atcodersection{\NomeDescricao}%
    \ignorespaces
}

\newenvironment{Problema}[4]{\atc@cabecalho{#1}{#2}{#3}{#4}}{}

\newenvironment{ProblemaAutor}[5]{%
    \renewcommand{\atc@autor}{#5}%
    \atc@cabecalho{#1}{#2}{#3}{#4}%
}{}

% O visual de referencia nao exibe nome de evento. A macro existe porque o
% contrato exige que esteja definida, nao que produza saida.
\newcommand{\Evento}[1]{}

\newcommand{\Paginacao}[2]{}

% -- Secoes do enunciado ----------------------------------------------------

\newcommand{\Entrada}{\atcoderline\atcodersection{\NomeEntrada}}
\newcommand{\Saida}{\atcoderline\atcodersection{\NomeSaida}}
\newcommand{\Interacao}{\atcoderline\atcodersection{\NomeInteracao}}
\newcommand{\Notas}{\atcoderline\atcodersection{\NomeNotas}}

\newcommand{\ExemploEntrada}{}

\newcounter{atcsample}
\newcounter{atc@pendentradas}
\newcounter{atc@pendsaidas}
\newif\ifatc@temcaso
\newif\ifatc@entradavazia
\newif\ifatc@saidavazia

\newcommand{\atc@entrada}{}
\newcommand{\atc@saida}{}

\newcommand{\atc@sevazio}[3]{\if\relax\detokenize{#1}\relax#2\else#3\fi}

\newcommand{\atc@reinicia}{%
    \gdef\atc@entrada{}\gdef\atc@saida{}%
    \setcounter{atc@pendentradas}{0}\setcounter{atc@pendsaidas}{0}%
    \global\atc@entradavaziatrue \global\atc@saidavaziatrue
}

\newcommand{\atc@empilhaentrada}[1]{%
    \atc@sevazio{#1}%
        {\stepcounter{atc@pendentradas}}%
        {\ifatc@entradavazia \global\atc@entradavaziafalse
         \else \g@addto@macro\atc@entrada{\\}\fi
         \whiledo{\value{atc@pendentradas}>0}%
            {\g@addto@macro\atc@entrada{\mbox{}\\}\addtocounter{atc@pendentradas}{-1}}%
         \g@addto@macro\atc@entrada{#1}}%
}

\newcommand{\atc@empilhasaida}[1]{%
    \atc@sevazio{#1}%
        {\stepcounter{atc@pendsaidas}}%
        {\ifatc@saidavazia \global\atc@saidavaziafalse
         \else \g@addto@macro\atc@saida{\\}\fi
         \whiledo{\value{atc@pendsaidas}>0}%
            {\g@addto@macro\atc@saida{\mbox{}\\}\addtocounter{atc@pendsaidas}{-1}}%
         \g@addto@macro\atc@saida{#1}}%
}

\newcommand{\atc@caixa}[1]{%
    \begin{atcoderbox}\raggedright\leavevmode#1\end{atcoderbox}%
}

\newcommand{\atc@descarrega}{%
    \ifatc@temcaso
        \atcoderline
        \atcodersection{\NomeExemploEntrada\ \theatcsample}%
        \atc@caixa{\atc@entrada}%
        \addvspace{0.5em}%
        \atcodersection{\NomeExemploSaida\ \theatcsample}%
        \atc@caixa{\atc@saida}%
    \fi
}

\newcommand{\CasoExemplo}{%
    \atc@descarrega
    \stepcounter{atcsample}%
    \atc@reinicia
    \global\atc@temcasotrue
    \ignorespaces
}

\newcommand{\LinhaExemplo}[2]{%
    \atc@empilhaentrada{#1}%
    \atc@empilhasaida{#2}%
    \ignorespaces
}

\newenvironment{Exemplo}{%
    \setcounter{atcsample}{0}%
    \global\atc@temcasofalse
    \atc@reinicia
    \ignorespaces
}{%
    \atc@descarrega
    \global\atc@temcasofalse
}

\newenvironment{Tutorial}[2]{%
    {\LARGE\bfseries \NomeTutorial: #1}\par
    \atcoderline
    {\small\textcolor{atlimits}{#2}}%
    \par\vspace{0.8em}%
    \ignorespaces
}{}

\newenvironment{formato}{%
    \par\vspace{0.2em}\begin{atcoderbox}%
}{%
    \end{atcoderbox}\par
}

\newlist{listarestricoes}{itemize}{1}
\setlist[listarestricoes]{leftmargin=1.6em, topsep=0.2em, itemsep=0.15em,
                          parsep=0pt, label=\textbullet}

\newcommand{\restricoes}{\atcodersection{Restrições}}
