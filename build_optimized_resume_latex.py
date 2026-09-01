r"""\documentclass[letterpaper]{article}
\usepackage[fontsize=11pt]{scrextend}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage[usenames,dvipsnames]{color}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage[T1]{fontenc}
\input{glyphtounicode}
\linespread{1.02}
\pagestyle{fancy}
\fancyhf{} % clear all header and footer fields
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
% Adjust margins for perfect flush 1-page fit
\addtolength{\oddsidemargin}{-0.6in}
\addtolength{\evensidemargin}{-0.6in}
\addtolength{\textwidth}{1.2in}
\addtolength{\topmargin}{-0.85in}
\addtolength{\textheight}{1.7in}
\urlstyle{same}
\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}
% Sections formatting -- plain bold uppercase instead of \scshape for max ATS safety
\titleformat{\section}{
  \vspace{-6pt}\bfseries\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]
% Ensure that generate pdf is machine readable/ATS parsable
\pdfgentounicode=1
%-------------------------
% Custom commands
\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}
\newcommand{\resumeSubheading}[4]{
  \vspace{0.5pt}\item
    \begin{tabular*}{\linewidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{2pt}
}
\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{\linewidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}
\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}, itemsep=3pt, parsep=0pt, topsep=0pt]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}[itemsep=1pt, parsep=0pt, topsep=2pt, partopsep=0pt]}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-2pt}}
%-------------------------------------------
%%%%%%  RESUME STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%
\begin{document}
\vspace*{-20pt}
\begin{center}
    \textbf{\Huge Shubham Bhati} \\ \vspace{2pt}
    \small Java Backend Engineer | Spring Boot | Microservices | Apache Kafka | Redis \\
    Noida, Uttar Pradesh, India | +91-6232133187 | \href{mailto:shubhambhati226@gmail.com}{shubhambhati226@gmail.com} \\
    \href{https://linkedin.com/in/bhatishubham}{linkedin.com/in/bhatishubham} | \href{https://github.com/Shubh2-0}{github.com/Shubh2-0} | \href{https://shubhambhati.is-a.dev/}{shubhambhati.is-a.dev}
\end{center}
\vspace{-6pt}
%-----------PROFESSIONAL SUMMARY-----------
\section{Professional Summary}
\small Java Backend Engineer with 3+ years of experience building high-throughput microservices and event-driven payment systems. Cut payment API latency by 35\% and built 3 production microservices from the ground up for onboarding, payments and notifications, including UPI payment integration via M2P. Skilled in Java 17/21, Spring Boot, Apache Kafka, Redis and secure data handling, delivering scalable REST APIs across fintech, enterprise SaaS and healthcare.
\vspace{2pt}
%-----------EXPERIENCE-----------
\section{Work Experience}
  \resumeSubHeadingListStart
    \resumeSubheading
      {MobilePe Fintech Private Limited}{Jun 2026 - Present}
      {Java Backend Engineer}{Noida, Uttar Pradesh, India}
      \resumeItemListStart
        \resumeItem{Architected 3 production microservices (\texttt{onboarding-service}, \texttt{payment-service} and \texttt{notification-service}) from the ground up, forming the platform's core onboarding, payment and notification infrastructure.}
        \resumeItem{Built UPI registration and wallet system via M2P, including a double-entry balance ledger and hold-then-settle float protection, ensuring accurate and reliable fund transfers in production.}
        \resumeItem{Built a secure KYC verification pipeline (Aadhaar, PAN and VCIP) with bank-grade encryption (AES-256-GCM) and blind indexing for fast lookups, strengthening fraud prevention during user onboarding.}
        \resumeItem{Cut payment API latency by 35\% by resolving production consumer lag and tuning Kafka consumer concurrency and connection pooling.}
      \resumeItemListEnd
    \resumeSubheading
      {AlignBits LLC}{Sep 2024 - May 2026}
      {Software Engineer (Promoted from Jr. Software Engineer)}{Dubai, UAE (Remote)}
      \resumeItemListStart
        \resumeItem{Built Spring Boot microservices with AWS SQS to process asynchronous transactions across 10 enterprise client pipelines.}
        \resumeItem{Cut manual debugging time by 30\% by integrating OpenAI API to automate validation and auto-correction of transformation scripts.}
        \resumeItem{Engineered an orchestration engine for message routing, payload transformation and split/merge workflows, improving pipeline reliability for enterprise integrations.}
        \resumeItem{Secured REST API endpoints across 5 microservices using JWT and OAuth 2.0.}
        \resumeItem{Sped up feature releases by containerizing microservices with Docker and setting up CI/CD pipelines with GitHub Actions.}
      \resumeItemListEnd
    \resumeSubheading
      {IHX Private Limited}{Jun 2023 - Aug 2024}
      {Associate Software Engineer}{Bengaluru, India}
      \resumeItemListStart
        \resumeItem{Processed healthcare claims daily by building backend payload transformation engines using Java 11 and MongoDB.}
        \resumeItem{Lowered response times by 40\% by fixing N+1 query loops, adding MySQL indexes and setting up Redis caching.}
        \resumeItem{Ensured data integrity across medical records by building validation pipelines with Spring Data JPA and custom exception handlers.}
      \resumeItemListEnd
  \resumeSubHeadingListEnd

%-----------SKILLS-----------
\section{Technical Skills}
 \begin{itemize}[leftmargin=0.15in, label={}, nosep]
    \item{
     \textbf{Languages \& Core}{: Java (8/11/17/21), Object-Oriented Programming (OOP), SOLID Principles, Design Patterns, Data Structures and Algorithms} \\
     \textbf{Frameworks \& Architecture}{: Spring Boot 3.4+, Spring Security, Spring MVC, Spring Data JPA, Microservices Architecture, Distributed Systems} \\
     \textbf{Databases \& Caching}{: PostgreSQL, MySQL, Redis, MongoDB, Hibernate ORM, Database Query Optimization} \\
     \textbf{APIs \& Messaging}{: RESTful APIs, Apache Kafka, M2P UPI Integration, AWS SQS, RabbitMQ, JWT Authentication, OAuth 2.0, OpenAPI (Swagger)} \\
     \textbf{DevOps \& Cloud}{: AWS (EC2, S3, RDS), Docker, Docker Compose, Git, CI/CD, GitHub Actions, Maven} \\
     \textbf{AI \& Automation}{: OpenAI API, Gemini API, Prompt Engineering, AI Integration}
    }
 \end{itemize}
%-----------EDUCATION-----------
\section{Education}
  \resumeSubHeadingListStart
    \resumeSubheading
      {Masai School}{2022 - 2023}
      {Software Engineering Program (Java Backend Specialization)}{Bengaluru, India}
    \resumeSubheading
      {Devi Ahilya Vishwavidyalaya}{2019 - 2022}
      {Bachelor of Commerce (B.Com)}{Indore, India}
  \resumeSubHeadingListEnd
\end{document}
"""
