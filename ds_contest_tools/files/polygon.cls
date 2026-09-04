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

\newenvironment{Problema}[4]{
    % #1 is label, #2 is title, #3 is time, #4 is memory
    \begin{problem}{#2}{standard input}{standard output}{#3 second}{#4 megabytes}
}{
    \end{problem}
}

\newenvironment{ProblemaAutor}[5]{
    % #1 is label, #2 is title, #3 is time, #4 is memory, #5 is author
    \begin{problem}{#2}{standard input}{standard output}{#3 second}{#4 megabytes}
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
