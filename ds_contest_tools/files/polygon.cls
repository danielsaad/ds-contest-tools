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
\RequirePackage{seqsplit}

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

% #1 título, #2 texto do tempo, #3 memória.
% Arquivos de entrada e saída vão vazios: o cabeçalho não exibe essas linhas.
\newcommand{\pol@abrecomtempo}[3]{%
    \pol@sevazio{#3}%
        {\begin{problem}{#1}{}{}{#2}{}}%
        {\begin{problem}{#1}{}{}{#2}{#3 megabytes}}%
}

\def\ShortProblemTitle{}

\newcommand{\pol@titulo}[2]{\pol@sevazio{#1}{#2}{\kw@Problem\ #1. #2}}

\newenvironment{Problema}[4]{
    \pol@abre{\pol@titulo{#1}{#2}}{#3}{#4}
}{
    \end{problem}
}

\newenvironment{ProblemaAutor}[5]{
    % #1 is label, #2 is title, #3 is time, #4 is memory, #5 is author
    \pol@abre{\pol@titulo{#1}{#2}}{#3}{#4}
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
    \multicolumn{1}{|c|}{\bf\texttt{\kw@stdin}} & \multicolumn{1}{c|}{\bf\texttt{\kw@stdout}} \\
    \hline
}{
    \hline
    \endtabularx
}

\newcommand{\Notas}{
    \Note
}

\newcounter{exemplocaso}

\newcommand{\CasoExemplo}{%
	\noalign{%
		\ifnum\value{exemplocaso}>0\relax
			\hrule height \arrayrulewidth
		\fi
		\stepcounter{exemplocaso}%
	}%
}

\newcommand{\LinhaExemplo}[2]{%
	\texttt{\seqsplit{#1}} & \texttt{\seqsplit{#2}}\\%
}

\DeclareRobustCommand{\contestname}{\thecontestname\strut}
\newcommand{\Evento}[1]{\renewcommand{\thecontestname}{#1}}

\newcommand{\Paginacao}[2]{%
    \setcounter{page}{#1}%
    \gdef\lastpage@putlabel{%
        \immediate\write\@auxout{\string\newlabel{LastPage}{{}{#2}}}}%
}

\newcommand{\NomeTutorial}{Tutorial}

\newenvironment{Tutorial}[2]{%
	\title{\NomeTutorial: #1}%
	\author{#2}%
	\date{}%
	\maketitle%
}{}
