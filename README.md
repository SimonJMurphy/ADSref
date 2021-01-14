# ADSref

ADSref is a tool for converting ADS private libraries (.bib files) into pdf publication lists.
It uses the python interface to the ADS API to gather paper titles and other metadata, including all-important citations.


### Setup

Two .bib files are required. One for first-author publications and one for co-authored publications.
These are readily downloaded from ADS private libraries. The cite keys must be the original ADS bibcodes.
For convenience, call them first\_author.bib and co\_author.bib.

You'll also need to follow the [Getting Started](https://ads.readthedocs.io/en/latest/#getting-started) page of the [ADS Python package](https://ads.readthedocs.io/en/latest/).

Finally, download publications.tex from this repo, which does all the latex formatting.

### Running ADSref

Running
```
python ADSref.py
```
will parse your .bib files and gather publication metadata from ADS, generating latex files in the process.
It will instruct you to run pdflatex on publications.tex when finished, which generates the pdf publication list.