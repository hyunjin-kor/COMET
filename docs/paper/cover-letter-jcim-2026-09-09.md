# Unsent cover-letter draft (JCIM Application Note)

Provisional destination: Journal of Chemical Information and Modeling, Application Note. Author identity, institutional permission, the software availability route, the commercial-license contact, competing interests and the originality/exclusive-submission statements must be confirmed before this letter can be sent. No submission has been made. Companion manuscript: `application-note-2026-09-09.md`. Updated 2026-09-11 to match the current manuscript.

Dear Editor,

Please consider our Application Note, "COMET: Software for Traceable Catalyst Manufacturing-Cost Screening with Reproducible Sensitivity Analysis," for publication in the Journal of Chemical Information and Modeling.

COMET is desktop and browser software for catalysis researchers who need a manufacturing-cost estimate for a literature catalyst and want to know how far that estimate can be trusted. It adopts the published Step Method and is checked against the method paper's three reference cases from their stated inputs, matching the platinum-on-carbon case to the cent. What the software adds is traceability and sensitivity analysis: every price carries its source, quote date and reliability grade on one of two price bases, spot quotes or fixed monthly averages; every preparation step is labelled as priced, substituted or left uncosted; thermal and electrode costs stay on their own functional units; environmental figures state their coverage; and a bundled library of 116 candidates in 30 reaction families can be examined with weighting sensitivity, historical repricing, leave-one-out tests and score sensitivity tests. All analyses run from committed inputs with recorded checksums.

We believe the note fits the journal's scope for software that supports chemical decision-making, alongside recent Application Notes such as NEXTorch (a Bayesian-optimization toolkit for chemical sciences and engineering), ProcessOptimizer and AI4Green. The software is publicly available on GitHub and archived with a Zenodo DOI [availability route to be confirmed by the authors before sending], ships a Windows installer and a browser mode served from source (the backend tests and the user-interface build run on Linux in continuous integration; the complete browser mode has been exercised on Windows), carries more than 900 automated tests, and can be tested by reviewers without registration.

The note separates what is checked from what is not. The implementation reproduces the method's reference cases, and its estimates fall inside the band of agreement the method paper reports against the market prices printed beside those cases; public trade statistics place the library's estimates in the corresponding market band over time. No public observation has matched a candidate's composition, grade, order size, date and cost boundary closely enough to compute an empirical error for a new formulation, and the note says so. We present the software as a way to make the assumptions behind a screening decision inspectable, not as a source of factory prices.

The manuscript is 4,994 word-equivalents including three figures under the journal's counting rule. It is not under consideration elsewhere. [The authors will confirm the exclusive-submission, originality, funding and competing-interest statements before sending.]

Sincerely,

[Corresponding author, affiliation and contact to be supplied]
