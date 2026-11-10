\ProvidesClass{polygon}
\LoadClass[11pt, a4paper, oneside]{article}

\RequirePackage[utf8]{inputenc}
\RequirePackage{olymp}
\RequirePackage{colortbl}
\RequirePackage{xcolor}
\RequirePackage{tabularx}
\RequirePackage{ifthen}
\RequirePackage{amsthm}
\RequirePackage{url}
% Permite quebra de linha dentro das células de exemplo — ver \LinhaExemplo.
\RequirePackage{seqsplit}

% ---------------------------------------------------------------
% Cabeçalho do problema
%
% Argumento vazio = não exibir: o gerador envia tempo e memória vazios quando
% a configuração manda ocultar os limites.
%
% O olymp.sty omite a linha de um limite só quando o argumento do `problem` é
% LITERALMENTE vazio: ele testa com \ifx&#4&, e uma macro que expande para
% vazio não passa nesse teste (sairia o rótulo sem valor). Por isso a escolha
% acontece aqui, antes de abrir o ambiente, e cada ramo abre o `problem` com o
% argumento já resolvido.
% ---------------------------------------------------------------

% Teste de vazio com \detokenize, robusto a qualquer conteúdo.
\newcommand{\pol@sevazio}[3]{%
    \if\relax\detokenize{#1}\relax
        \expandafter\@firstoftwo
    \else
        \expandafter\@secondoftwo
    \fi{#2}{#3}%
}

% #1 título, #2 tempo, #3 memória.
\newcommand{\pol@abre}[3]{%
    \pol@sevazio{#2}%
        {\pol@abrecomtempo{#1}{}{#3}}%
        {\pol@abrecomtempo{#1}{#2 second}{#3}}%
}

% #1 título, #2 texto do tempo (já resolvido), #3 memória.
\newcommand{\pol@abrecomtempo}[3]{%
    \pol@sevazio{#3}%
        {\begin{problem}{#1}{standard input}{standard output}{#2}{}}%
        {\begin{problem}{#1}{standard input}{standard output}{#2}{#3 megabytes}}%
}

\newenvironment{Problema}[4]{
    % #1 is label, #2 is title, #3 is time, #4 is memory
    \pol@abre{#2}{#3}{#4}
}{
    \end{problem}
}

\newenvironment{ProblemaAutor}[5]{
    % #1 is label, #2 is title, #3 is time, #4 is memory, #5 is author
    \pol@abre{#2}{#3}{#4}
    \textit{Author: #5}\par
}{
    \end{problem}
}

\newcommand{\Entrada}{
    \InputFile
}

\newcommand{\Saida}{
    \OutputFile
}

\newcommand{\Interacao}{
    \Interaction
}

\newcommand{\ExemploEntrada}{
    \Example
}

\newenvironment{Exemplo}{
    \setcounter{exemplocaso}{0}%
    \tabularx{\textwidth}{|X|X|}
    \hline
    \multicolumn{1}{|c|}{\bf\texttt{\InputFileName}} & \multicolumn{1}{c|}{\bf\texttt{\OutputFileName}} \\
    \hline
}{
    \hline
    \endtabularx
}

\newcommand{\Notas}{
    \Note
}

% ---------------------------------------------------------------
% Contrato de macros do gerador
%
% O gerador emite a mesma marcação para todos os formatos suportados; cabe a
% cada classe decidir a aparência. Estas três macros faltavam aqui, e a
% ausência era o débito D3: qualquer problema gerado com -lc polygon
% terminava em "Undefined control sequence".
% ---------------------------------------------------------------
\newcounter{exemplocaso}

% Separa os casos de teste por uma régua horizontal, preservando a aparência
% original do formato. O \hrule vai dentro de \noalign porque é assim que o
% próprio \hline é implementado — usar \hline aqui dispararia
% "Misplaced \noalign".
\newcommand{\CasoExemplo}{%
	\noalign{%
		\ifnum\value{exemplocaso}>0\relax
			\hrule height \arrayrulewidth
		\fi
		\stepcounter{exemplocaso}%
	}%
}

% Sem zebrado neste formato: a separação por régua já distingue os casos.
% O \seqsplit permite quebra dentro da célula — ver a nota em maratona.cls.
\newcommand{\LinhaExemplo}[2]{%
	\texttt{\seqsplit{#1}} & \texttt{\seqsplit{#2}}\\%
}

% O formato Polygon não exibe nome de evento. A macro existe como no-op
% deliberado: o contrato exige que ela seja definida, não que produza saída.
\newcommand{\Evento}[1]{}

% ---------------------------------------------------------------
% Tutorial — ver a nota equivalente em maratona.cls.
% ---------------------------------------------------------------
\newcommand{\NomeTutorial}{Tutorial}

\newenvironment{Tutorial}[2]{%
	\title{\NomeTutorial: #1}%
	\author{#2}%
	\date{}%
	\maketitle%
}{}
