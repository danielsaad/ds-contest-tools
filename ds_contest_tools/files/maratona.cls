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
\RequirePackage{amsthm}
\RequirePackage{url}
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
\RequirePackage{lastpage}


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

\newcommand{\TextoPagina}[2]{Página #1 de #2}

\newif\ifmar@numerar
\newcommand{\mar@total}{\pageref*{LastPage}}
\newcommand{\mar@rodape}{\ifmar@numerar\TextoPagina{\thepage}{\mar@total}\fi}

\lhead{DS Contest Tools}
\cfoot{\mar@rodape}
\pagestyle{fancy}

% Página de título do tutorial (\maketitle).
\fancypagestyle{plain}{%
	\fancyhf{}%
	\cfoot{\mar@rodape}%
	\renewcommand{\headrulewidth}{0pt}%
}

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


\newcommand{\mar@sevazio}[3]{%
	\if\relax\detokenize{#1}\relax
		\expandafter\@firstoftwo
	\else
		\expandafter\@secondoftwo
	\fi{#2}{#3}%
}

% #1 é o valor que decide se o item aparece; #2 é o texto do item.
\newcommand{\mar@item}[2]{\mar@sevazio{#1}{}{{\\\footnotesize #2}}}

% #1 rótulo, #2 título, #3 tempo, #4 memória, #5 autor.
\newcommand{\mar@cabecalho}[5]{%
	\begin{center}
		\Large{\ifthenelse{\equal{#1}{}}{\textbf{{#2}}}{\textbf{Problema {#1} \\ {#2} }}}%
		\mar@item{#3}{\textbf{Limite de tempo: {#3}s}}%
		\mar@item{#4}{\textbf{Limite de memória: {#4}MB}}%
		\mar@item{#5}{Autor: {#5}}%
	\end{center}
}

\newcounter{problem}
\newenvironment{Problema}[4]{
	\stepcounter{problem}
	\newpage
	\mar@cabecalho{#1}{#2}{#3}{#4}{}
}

\newcounter{problemAutor}
\newenvironment{ProblemaAutor}[5]{
	\stepcounter{problemAutor}
	\newpage
	\mar@cabecalho{#1}{#2}{#3}{#4}{#5}
}


\newcommand{\codigofonte}[1]{Nome do arquivo fonte: {#1}}

\newcommand{\NomeEntrada}{Entrada}
\newcommand{\NomeSaida}{Saída}
\newcommand{\NomeInteracao}{Interação}
\newcommand{\NomeNotas}{Notas}
\newcommand{\NomeExemplo}{Exemplo}
\newcommand{\NomeTutorial}{Tutorial}

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

\newcommand{\Evento}[1]{\lhead{#1}}

% \thepage é redefinido sem \pagenumbering, que zeraria o contador.
\newcommand{\NumerarPaginas}{\mar@numerartrue\renewcommand{\thepage}{\arabic{page}}}

% Sem \Paginacao, o total vem do LastPage.
\newcommand{\Paginacao}[2]{\setcounter{page}{#1}\renewcommand{\mar@total}{#2}}

\newcounter{exemplocaso}

\newcommand{\CasoExemplo}{\noalign{\stepcounter{exemplocaso}}}

\newcommand{\LinhaExemplo}[2]{%
	\ifodd\value{exemplocaso}\else\rowcolor{gray!20}\fi%
	\texttt{\seqsplit{#1}} & \texttt{\seqsplit{#2}}\\%
}

\newenvironment{Exemplo}
{

	\setcounter{exemplocaso}{0}%
	\tabularx{\textwidth}{XX}
	\hline
	\NomeEntrada & \NomeSaida \\\hline
}
{
	\hline
	\endtabularx
}

\newenvironment{ExemploEntrada}
{\SecaoEnunciado{\NomeExemplo}}
{
}

\newenvironment{Tutorial}[2]{%
	\title{\NomeTutorial: #1}%
	\author{#2}%
	\date{}%
	\maketitle%
}{}

