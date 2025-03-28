# DCM data integration in SEIR-models

This repository contains the Python code supporting the paper "M. H. H. Schoot Uiterkamp, W. J. van Dijk, H. Heesterbeek, R. van der Hofstad, J. C. Kiefte-de Jong, N. Litvak (2025): Value of risk-contact data from digital contact monitoring apps in infectious disease modeling", available via https://arxiv.org/abs/2503.21228.

## Module description

- data_loader.py: Loads, filters, and prepares the COVID RADAR data and (reformatted CoronaMelder data.
- initialization.py: Calculates estimates of the effective reproduction number and number of infectious people.
- figures.py: Reproduces figures from the paper.

## Data

All data that is needed as input is publicly available.

Data from the Dutch National Institute for Public Health and the Environment (https://data.rivm.nl/covid-19/):
- Daily estimates of the number of infectious people (COVID-19_prevalentie.json).
- Daily estimates of the effective reproduction number (COVID-19_reproductiegetal.json and COVID-19_reproductiegetal_tm_03102021.json).

Data on (risk) contacts from digital contact monitoring apps:
- COVID RADAR app: https://lifesciences.datastations.nl/dataset.xhtml?persistentId=doi:10.17026/dans-zcd-m9dh.
- CoronaMelder app: https://github.com/minvws/nl-covid19-notification-app-statistics/tree/main.


## Reproduction of results

To reproduce the results in the paper, run figures.py. This calls "initialization.py" that calculates the estimates of the effective reprouction number and number of infectious people, and subsequently creates the figures of the paper.
