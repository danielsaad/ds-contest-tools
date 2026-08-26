\ProvidesClass{polygon}
\LoadClass[11pt, a4paper, oneside]{article}

\RequirePackage[utf8]{inputenc}
\RequirePackage{olymp}
\RequirePackage{colortbl}
\RequirePackage{xcolor}
\RequirePackage{tabularx}
\RequirePackage{ifthen}

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
