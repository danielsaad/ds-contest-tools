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
\RequirePackage{amssymb,amsmath,wrapfig}
% amsthm depois de amsmath (exigência do pacote). Usado pelo ambiente Tutorial.
\RequirePackage{amsthm}
\RequirePackage{url}
% Permite quebra de linha dentro das células de exemplo — ver \LinhaExemplo.
\RequirePackage{seqsplit}
\RequirePackage{xcolor,colortbl}
\RequirePackage{xcolor}
\RequirePackage{ifthen}
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
	pdftitle={IV Maratona de Programação do IFB \today},
	pdfauthor={},
	pdfsubject={Caderno de problemas da IV Maratona de Programação do IFB }, 
	pdfkeywords={maratona, programação, IFB}
}



\DeclareGraphicsExtensions{png}

\lhead{DS Contest Tools}
\pagestyle{fancy}

% Capa
\newenvironment{Maratona}[3]
{
	\begin{titlepage}
		\begin{center}
			
			\vspace{1cm}
			\Large{\textbf{#1}} \\
			\vspace{1cm}
			{\textbf{Caderno de Problemas}} \\
			\vspace{1cm}
			\begin{small}
				\textsl{#2}
			\end{small} \\
			\begin{figure}[htp]
				\begin{center}
					\includegraphics[scale=1]{logos/logo-maratona.png}
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
		\Large{\ifthenelse{\equal{#1}{}}{\textbf{{#2}}}{\textbf{Problema {#1} \\ {#2} }}}{\\\footnotesize \textbf{Limite de tempo: {#3}s}}{\\\footnotesize \textbf{Limite de memória: {#4}MB}}
	\end{center}
}

\newcounter{problemAutor}
\newenvironment{ProblemaAutor}[5]{
	\stepcounter{problemAutor}
	\newpage
	\begin{center}
		\Large{\ifthenelse{\equal{#1}{}}{\textbf{{#2}}}{\textbf{Problema {#1} \\ {#2} }}}{\\\footnotesize \textbf{Limite de tempo: {#3}s}}{\\\footnotesize \textbf{Limite de memória: {#4}MB\\}}{
			\footnotesize Autor: {#5}
		}
	\end{center}
}


% Código-fonte
\newcommand{\codigofonte}[1]{Nome do arquivo fonte: {#1}}

% ---------------------------------------------------------------
% Rótulos das seções do enunciado
%
% Para trocar de idioma, sobrescreva no .tex antes de \begin{document}:
%     \renewcommand{\NomeEntrada}{Input}
%     \renewcommand{\NomeSaida}{Output}
%
% Mesma separação rótulo/formatação adotada pelo olymp.sty (\kw@Input +
% \createsection), mas sem "@" no nome, para permitir \renewcommand
% direto no .tex sem precisar de \makeatletter.
% ---------------------------------------------------------------
\newcommand{\NomeEntrada}{Entrada}
\newcommand{\NomeSaida}{Saída}
\newcommand{\NomeInteracao}{Interação}
\newcommand{\NomeNotas}{Notas}
\newcommand{\NomeExemplo}{Exemplo}
\newcommand{\NomeTutorial}{Tutorial}

% Formatação comum a todas as seções do enunciado.
% Altere aqui para mudar espaçamento ou tipografia de todas de uma vez.
\newcommand{\SecaoEnunciado}[1]{
	\bigskip
	\begin{large}
		\textbf{#1} \\
	\end{large}
}

% Entrada
\newcommand{\Entrada}{\SecaoEnunciado{\NomeEntrada}}

% Saida
\newcommand{\Saida}{\SecaoEnunciado{\NomeSaida}}

\newcommand{\Interacao}{\SecaoEnunciado{\NomeInteracao}}

\newcommand{\Notas}{\SecaoEnunciado{\NomeNotas}}

% ---------------------------------------------------------------
% Cabeçalho do evento
%
% O gerador emite \Evento{...}; a classe decide onde ele aparece.
% ---------------------------------------------------------------
\newcommand{\Evento}[1]{\lhead{#1}}

% ---------------------------------------------------------------
% Exemplos
%
% O gerador emite apenas a estrutura lógica:
%
%     \begin{Exemplo}
%     \CasoExemplo                  <- inicia um caso de teste
%     \LinhaExemplo{entrada}{saida} <- uma linha do caso
%     \LinhaExemplo{entrada}{}
%     \CasoExemplo
%     ...
%     \end{Exemplo}
%
% Fonte, zebrado e alinhamento são decididos aqui, não no gerador.
% ---------------------------------------------------------------
\newcounter{exemplocaso}

% O \noalign é necessário: \stepcounter é inexpansível e, sem ele, abriria
% a primeira célula da linha, fazendo o \rowcolor de \LinhaExemplo cair no
% meio da célula (erro "Misplaced \noalign").
\newcommand{\CasoExemplo}{\noalign{\stepcounter{exemplocaso}}}

% O \seqsplit permite quebra em qualquer posição dentro da célula.
%
% Sem ele o conteúdo transborda em vez de quebrar: o gerador converte todo
% espaço em "~" (espaço inquebrável) para preservar espaços consecutivos, e o
% "~" proíbe a quebra que a coluna X do tabularx faria naturalmente.
% Preservar o espaço é decisão de conteúdo (fica no gerador); permitir a
% quebra é decisão de apresentação e mora aqui.
\newcommand{\LinhaExemplo}[2]{%
	\ifodd\value{exemplocaso}\else\rowcolor{gray!20}\fi%
	\texttt{\seqsplit{#1}} & \texttt{\seqsplit{#2}}\\%
}

\newenvironment{Exemplo}
{

	\setcounter{exemplocaso}{0}%
	\tabularx{\textwidth}{XX}
	%    {@{\extracolsep{\fill}}|l|l|}
	%    {|l|l@{\extracolsep{\fill}|}}
	\hline
	\NomeEntrada & \NomeSaida \\\hline
}
{
	\hline
	\endtabularx
}

% Exemplo de Entrada
\newenvironment{ExemploEntrada}
{\SecaoEnunciado{\NomeExemplo}}
{
}

% ---------------------------------------------------------------
% Tutorial (editorial do problema)
%
% O gerador emite apenas:
%
%     \begin{Tutorial}{<título do problema>}{<autor>}
%     \input{statement/tutorial}
%     \end{Tutorial}
%
% Corpo da fonte, pacotes, numeração de página e layout do título são
% decididos aqui. Antes viviam num preâmbulo montado em Python.
%
% Nota de layout: o tutorial passa a usar as margens desta classe, e não as
% do pacote fullpage que o gerador carregava. É deliberado — o objetivo de
% usar a mesma classe é que enunciado e tutorial tenham identidade visual
% coerente.
% ---------------------------------------------------------------
\newenvironment{Tutorial}[2]{%
	\title{\NomeTutorial: #1}%
	\author{#2}%
	\date{}%
	\maketitle%
}{}

