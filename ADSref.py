import ads
ads.config.token = 'my token'
import numpy as np

# Filenames
## Enter the filename for first-author publications here:
first_author = "first_author.bib"
## Enter the filename for cd-authored publications here:
co_author = "co_author.bib"


# Function Declarations

def extract_bibcodes(filename):
    """Takes a .bib filename, looks for bibcodes on the first line of each entry, and parses into a list."""

    f = open(filename)
    full_list = f.readlines()

    bibcodes = []
    
    # drop yCat, arxiv, PhDT, and other non-refereed entries
    # Workaround, since I couldn't get the API to accept property:refereed or property=refereed to work when searching
    exclude = ['arXiv','tmp','yCat','PhDT','AAS','ASPC','BSRSL','conf','EPJWC','IAUFM','IAUGA','IAUS','hst','iue','jwst','spzr','prop']
    
    for line in full_list:
        if line[0] == "@":
            if not any(x in line for x in exclude):
                bibcodes.append(line.split("{")[1].replace(",\n",""))
    
    return bibcodes


def author_format(authors):
    if len(authors) == 1:
        a = authors[0]
    elif len(authors) == 2:
        a = authors[0] + " \& " + authors[1]
    else:
        a = authors[0] + ' et al.'
    return a


def journal_name(bibcode):
    return bibcode.split(".")[0][4:].replace("&","\&")


def adsurl(bibcode):
    return 'https://ui.adsabs.harvard.edu/abs/' + bibcode


def latex_title_greek(title):
    greek_dict = {"α":r"$\alpha$", "β":r"$\beta$", "γ":r"$\gamma$", "δ":r"$\delta$", "ϵ":r"$\epsilon$", "ζ":r"$\zeta$", "η":r"$\eta$", "ι":r"$\iota$", "θ":r"$\theta$", "κ":r"$\kappa$", "λ":r"$\lambda$", "μ":r"$\mu$", "ν":r"$\nu$", "ξ":r"$\xi$", "π":r"$\pi$", "ρ":r"$\rho$", "σ":r"$\sigma$", "τ":r"$\tau$", "φ":r"$\phi$", "χ":r"$\chi$", "ψ":r"$\psi$", "ω":r"$\omega$"}
    for key in greek_dict.keys():
        title = title.replace(key, greek_dict[key])
    title = title.replace("<SUB>⊙</SUB>",r"$_{\odot}$")
    title = title.replace("<SUB>max</SUB>",r"max")
    return title


def citation_formatter(cites):
    if cites is None:
        return ""
    elif cites == 0:
        return ""
    else:
        if cites < 10:
            return f"Cited: \\phantom" + "{1}" + f"{cites}"
        else:
            return f"Cited: {cites}"


def latex_strings(paper_list):
    output = []
    n = len(paper_list)
    for i,p in enumerate(paper_list):
        title = p.title[0]
        entry = "\\textbf{" + f"{n-i}" + "}. " + '\\' + 'href{' + adsurl(p.bibcode) + "}{" + f"{latex_title_greek(title)}" + "}" + "\\\\"
        entry += author_format(p.author)
        entry += f" ({p.year}) "
        entry += journal_name(p.bibcode)
        entry += f" {p.volume},"
        entry += f" {p.page[0]}."
        entry += ' \\hspace*{\\fill}' + citation_formatter(p.citation_count) + "\\vspace{1mm}" + "\\\\"
        output.append(entry)
    output[0] = "\\noindent " + output[0]
    return output


def export_latex(filename,latex_string_list):
    f = open(filename,"w")
    for line in latex_string_list:
        f.write(line+"\n")
    f.close()
    return "Saved."


# Parse bibcodes
print("Parsing bibcodes...")
bibcodes = extract_bibcodes(first_author)
co_bibcodes = extract_bibcodes(co_author)


# Search for papers and their attributes from bibcodes
print("Querying the ADS API for paper metadata... This may take a while if there are many entries...")
papers = [list(ads.SearchQuery(bibcode=bibcode, fl=['bibcode', 'title', 'author', 'year', 'volume', 'page', 'citation_count']))[0] for bibcode in bibcodes]
co_papers = [list(ads.SearchQuery(bibcode=bibcode, fl=['bibcode', 'title', 'author', 'year', 'volume', 'page', 'citation_count']))[0] for bibcode in co_bibcodes]


# Remove Errata
## Because Ew. And if anyone cares about the paper content they'll discover errata when they visit the ADS pages.
print("Dropping Errata, Corrigenda...")
for p in papers:
    if "Erratum" in p.title[0] or "Corrigendum" in p.title[0]:
        papers.remove(p)
for p in co_papers:
    if "Erratum" in p.title[0] or "Corrigendum" in p.title[0]:
        co_papers.remove(p)

## For personal use only: Allow papers to be downloaded.
download=True
# Download papers
if download == True:
    import os
    import wget
    print("Downloading papers...")
    for b in co_bibcodes:
        url = "https://ui.adsabs.harvard.edu/link_gateway/" + f"{b}" + "/PUB_PDF"
        # cmd = "wget ‐‐directory-prefix=papers/ " + url
        cmd = "echo " + url + " >> papers/co-paper_list.txt"
        print(cmd)
        os.system(cmd)

# Sum citations
first_author_cites = 0
co_author_cites = 0

for p in papers:
    if p.citation_count is not None:
        first_author_cites += p.citation_count
for p in co_papers:
    if p.citation_count is not None:
        co_author_cites += p.citation_count

# Compile LaTeX string
print("Compiling LaTeX strings...")
output = latex_strings(papers)
co_output = latex_strings(co_papers)

# Export to LaTeX
print("Exporting to LaTeX...")
export_latex("first_author.tex",output)
export_latex("co_author.tex",co_output)

print(f"\nThere are {len(papers)} first-author papers, and {len(co_papers)} co-authored papers.")
print(f"They have a total of {first_author_cites} and {co_author_cites} citations, respectively.")

print("\n\n.tex files prepared. Now run:\n")
print("\t pdflatex publications.tex\n\n\n")