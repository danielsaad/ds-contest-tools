\ProvidesPackage{maratona}
\LoadClass[12pt]{article}

% remove page numbers
\pagenumbering{gobble}

\RequirePackage{fancyhdr}

\RequirePackage{tabularx,colortbl}

%\RequirePackage{arial}
\RequirePackage{ifpdf}
\RequirePackage[T1]{fontenc}
\RequirePackage[utf8]{inputenc}
\RequirePackage[portuguese]{babel}
\RequirePackage{graphics}
\RequirePackage{graphicx}
\RequirePackage{amssymb, wrapfig}
\RequirePackage{xcolor,colortbl}
\RequirePackage{xcolor}
\oddsidemargin 0cm
\evensidemargin -2cm
\topmargin -1cm
\textwidth 16cm
\textheight 23cm

\ifpdf
  \RequirePackage[pdftex]{hyperref}
\else
  \RequirePackage[hypertex]{hyperref}
\fi


\newcommand{\var}[1]{\ensuremath{{#1}}}


\hypersetup{
  letterpaper,
  colorlinks=true,
  linkcolor=blue,
  urlcolor=blue,
  pdfpagemode=none,
  pdftitle={II Maratona de Programação do IFB \today},
  pdfauthor={},
  pdfsubject={Caderno de questões da II Maratona de Programação do IFB }, 
  pdfkeywords={maratona, programação, IFB}
}



\DeclareGraphicsExtensions{png}

\lhead{II Maratona de Programação do IFB}
\pagestyle{fancy}

% Capa
\newenvironment{Maratona}[3]
{
	\begin{titlepage}
	    \begin{center}

        \vspace{1cm}
	      \Large{\textbf{#1}} \\
	    \vspace{1cm}
        {\textbf{Maratona}} \\
	    \vspace{1cm}
	    \begin{small}
        \textsl{#2}
        \end{small} \\
        \begin{figure}[htp]
              	\begin{center}
              		\includegraphics[scale=0.35]{logos/logo-maratona.png}
              	\end{center}
        \end{figure}
        {(Este caderno contém {#3} problemas)} \\
	    \vspace{1cm}
}
{
	\vfill
        \begin{small}
        {QNM 40, Área Especial nº 01,
        	Taguatinga/DF, 72146-000 , 
        	Brasil } \\
		{Telefone (61) 2103-2200 \\http://www.ifb.edu.br/taguatinga} \\
        \end{small}
	    \end{center}
	\end{titlepage}
}

\newcommand{\Organizacao}[2]{
	{\small \vfill
		\begin{center}
			
			\textbf{Comissão Organizadora:} \\
			{#1} \\
			\bigskip
			\textbf{Apoio:}\\
			{#2}
		\end{center}
	}
	\vfill
}


% Problema
\newcounter{problem}
\newenvironment{Problema}[4]{
    \stepcounter{problem}
    \newpage
	\begin{center}
		\Large{\textbf{Problema {#1} \\ {#2} }}{\\[.2cm]\footnotesize \textbf{Limite de tempo: {#3}s\\}}{
			\footnotesize Autor: {#4}
		}
	\end{center}
}

% Código-fonte
\newcommand{\codigofonte}[1]{Nome do arquivo fonte: {#1}}

% Entrada
\newcommand{\Entrada}{
    \bigskip
    \begin{large}
    \textbf{Entrada} \\
    \end{large}
}

% Saida
\newcommand{\Saida}{
    \bigskip
    \begin{large}
    \textbf{Saída} \\
    \end{large}
}

% Exemplo
\newenvironment{Exemplo}
{
	
    \tabularx{\textwidth}{XX}
%    {@{\extracolsep{\fill}}|l|l|}
%    {|l|l@{\extracolsep{\fill}|}}
	\hline
    Entrada & Saída \\\hline 
}
{
    \hline
    \endtabularx
}

% Exemplo de Entrada
\newenvironment{ExemploEntrada}
{
    \bigskip
    \begin{large}
    \textbf{Exemplo} \\
    \end{large}
}
{
}

% Sample Output

