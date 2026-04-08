from textwrap import wrap
import time
from typing import Optional

import pandas as pd
import requests
import streamlit as st


EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
DEFAULT_HEADERS = {"User-Agent": "sequence-fetcher-streamlit/1.0"}
REQUEST_TIMEOUT = 30

LANGUAGE_BUTTONS = {"pl": "PL", "en": "EN"}

TRANSLATIONS = {
    "pl": {
        "hero_title": "Sequence Fetcher",
        "hero_body": "Wyszukaj rekordy genu w NCBI po nazwie organizmu i nazwie genu, a następnie pobierz sekwencje genomowe, promotora, mRNA oraz odpowiadające im sekwencje białkowe w formacie multi-FASTA.",
        "sidebar_language": "Język / Language",
        "settings": "Ustawienia",
        "ncbi_email": "Email do NCBI",
        "ncbi_email_help": "Opcjonalne, ale zalecane przez NCBI przy częstszych zapytaniach.",
        "ncbi_email_placeholder": "twoj.email@instytucja.pl",
        "ncbi_api_key": "NCBI API key",
        "ncbi_api_key_help": "Opcjonalne. Przyspiesza limity zapytań dla większych pobrań.",
        "max_gene_hits": "Maksymalna liczba rekordów genu",
        "promoter_length": "Długość promotora (nt)",
        "promoter_length_help": "Ile nukleotydów upstream od początku genu pobrać jako sekwencję promotora.",
        "max_mrna_per_gene": "Maksymalna liczba mRNA na gen",
        "max_proteins_per_gene": "Maksymalna liczba białek na gen",
        "organism_name": "Nazwa organizmu",
        "gene_name": "Nazwa genu",
        "search_records": "Wyszukaj rekordy",
        "searching_records": "Pobieram dopasowane rekordy genu z NCBI...",
        "provide_both": "Podaj zarówno nazwę organizmu, jak i nazwę genu.",
        "http_error": "NCBI zwróciło błąd HTTP: {error}",
        "connection_error": "Nie udało się połączyć z NCBI: {error}",
        "matched_gene_records": "Dopasowane rekordy genu",
        "sort_by": "Sortuj wyniki wg",
        "sort_relevance": "Trafność",
        "sort_genomic_nt": "Długość genomowa nt",
        "sort_mrna_nt": "Długość mRNA nt",
        "sort_aa": "Długość aa",
        "sort_symbol": "Symbol",
        "sort_organism": "Organizm",
        "descending": "Malejąco",
        "gene_hits": "Gene hits",
        "organism": "Organizm",
        "gene": "Gen",
        "col_include": "Uwzględnij",
        "col_gene_id": "GeneID",
        "col_symbol": "Symbol",
        "col_description": "Opis",
        "col_organism": "Organizm",
        "col_taxid": "TaxID",
        "col_genomic_nt": "Długość genomowa nt",
        "col_mrna_accession": "Accession mRNA",
        "col_mrna_nt": "Długość mRNA nt",
        "col_protein_accession": "Accession białka",
        "col_aa": "Długość aa",
        "col_genomic_locations": "Liczba lokalizacji genomowych",
        "on_off": "On/Off",
        "on_off_help": "Odznaczone rekordy są pomijane przy generowaniu multi-FASTA.",
        "active_records": "Aktywne rekordy: {count}",
        "inactive_records": "Wyłączone rekordy: {count}",
        "generate_genomic": "Generuj multi-FASTA genomowe",
        "generate_promoter": "Generuj multi-FASTA promotora",
        "generate_mrna": "Generuj multi-FASTA mRNA",
        "generate_protein": "Generuj multi-FASTA białkowe",
        "fetching_genomic": "Pobieram sekwencje genomowe...",
        "fetching_promoter": "Pobieram sekwencje promotora...",
        "fetching_mrna": "Pobieram sekwencje mRNA...",
        "fetching_protein": "Pobieram sekwencje białkowe...",
        "no_genomic": "Nie znaleziono sekwencji genomowych dla wybranych rekordów.",
        "no_promoter": "Nie znaleziono sekwencji promotora dla wybranych rekordów.",
        "genomic_unavailable_mrna_protein_ok": "Dla wybranych rekordów brakuje lokalizacji genomowych, ale nadal możesz pobrać sekwencje mRNA i białkowe.",
        "promoter_requires_genomic": "Sekwencje promotora wymagają dostępnych lokalizacji genomowych.",
        "no_mrna": "Nie znaleziono sekwencji mRNA dla wybranych rekordów.",
        "no_protein": "Nie znaleziono sekwencji białkowych dla wybranych rekordów.",
        "genomic_http_error": "NCBI zwróciło błąd HTTP przy pobieraniu sekwencji genomowych: {error}",
        "promoter_http_error": "NCBI zwróciło błąd HTTP przy pobieraniu sekwencji promotora: {error}",
        "mrna_http_error": "NCBI zwróciło błąd HTTP przy pobieraniu sekwencji mRNA: {error}",
        "protein_http_error": "NCBI zwróciło błąd HTTP przy pobieraniu sekwencji białkowych: {error}",
        "genomic_fetch_error": "Nie udało się pobrać sekwencji genomowych: {error}",
        "promoter_fetch_error": "Nie udało się pobrać sekwencji promotora: {error}",
        "mrna_fetch_error": "Nie udało się pobrać sekwencji mRNA: {error}",
        "protein_fetch_error": "Nie udało się pobrać sekwencji białkowych: {error}",
        "enable_one": "Włącz co najmniej jeden rekord w tabeli, żeby wygenerować multi-FASTA.",
        "genomic_section": "Multi-FASTA genomowe",
        "promoter_section": "Multi-FASTA promotora",
        "mrna_section": "Multi-FASTA mRNA",
        "protein_section": "Multi-FASTA białkowe",
        "download_genomic": "Pobierz multi-FASTA genomowe",
        "download_promoter": "Pobierz multi-FASTA promotora",
        "download_mrna": "Pobierz multi-FASTA mRNA",
        "download_protein": "Pobierz multi-FASTA białkowe",
        "preview_genomic": "Podgląd sekwencji genomowych",
        "preview_promoter": "Podgląd sekwencji promotora",
        "preview_mrna": "Podgląd sekwencji mRNA",
        "preview_protein": "Podgląd sekwencji białkowych",
        "no_matches": "Nie znaleziono dopasowanych rekordów genu dla podanego zapytania.",
        "caption": "Źródło danych: NCBI Entrez E-utilities. Sekwencje genomowe są wycinane na podstawie lokalizacji genu w rekordzie Gene, sekwencje promotora są przybliżonym upstream region względem orientacji genu, sekwencje mRNA pochodzą z powiązanych rekordów RefSeq RNA, a sekwencje białkowe z rekordów powiązanych z genem.",
    },
    "en": {
        "hero_title": "Sequence Fetcher",
        "hero_body": "Search NCBI gene records by organism and gene name, then retrieve genomic, promoter, mRNA, and corresponding protein sequences in multi-FASTA format.",
        "sidebar_language": "Language / Język",
        "settings": "Settings",
        "ncbi_email": "NCBI email",
        "ncbi_email_help": "Optional, but recommended by NCBI for more frequent queries.",
        "ncbi_email_placeholder": "your.email@institution.org",
        "ncbi_api_key": "NCBI API key",
        "ncbi_api_key_help": "Optional. Increases rate limits for larger downloads.",
        "max_gene_hits": "Maximum number of gene records",
        "promoter_length": "Promoter length (nt)",
        "promoter_length_help": "How many upstream nucleotides from the gene start to retrieve as promoter sequence.",
        "max_mrna_per_gene": "Maximum number of mRNA records per gene",
        "max_proteins_per_gene": "Maximum number of protein records per gene",
        "organism_name": "Organism name",
        "gene_name": "Gene name",
        "search_records": "Search records",
        "searching_records": "Fetching matching gene records from NCBI...",
        "provide_both": "Provide both the organism name and the gene name.",
        "http_error": "NCBI returned an HTTP error: {error}",
        "connection_error": "Could not connect to NCBI: {error}",
        "matched_gene_records": "Matched gene records",
        "sort_by": "Sort results by",
        "sort_relevance": "Relevance",
        "sort_genomic_nt": "Genomic length nt",
        "sort_mrna_nt": "mRNA length nt",
        "sort_aa": "AA length",
        "sort_symbol": "Symbol",
        "sort_organism": "Organism",
        "descending": "Descending",
        "gene_hits": "Gene hits",
        "organism": "Organism",
        "gene": "Gene",
        "col_include": "Include",
        "col_gene_id": "GeneID",
        "col_symbol": "Symbol",
        "col_description": "Description",
        "col_organism": "Organism",
        "col_taxid": "TaxID",
        "col_genomic_nt": "Genomic length nt",
        "col_mrna_accession": "mRNA accession",
        "col_mrna_nt": "mRNA length nt",
        "col_protein_accession": "Protein accession",
        "col_aa": "AA length",
        "col_genomic_locations": "Genomic locations",
        "on_off": "On/Off",
        "on_off_help": "Unchecked records are ignored when generating multi-FASTA.",
        "active_records": "Active records: {count}",
        "inactive_records": "Disabled records: {count}",
        "generate_genomic": "Generate genomic multi-FASTA",
        "generate_promoter": "Generate promoter multi-FASTA",
        "generate_mrna": "Generate mRNA multi-FASTA",
        "generate_protein": "Generate protein multi-FASTA",
        "fetching_genomic": "Fetching genomic sequences...",
        "fetching_promoter": "Fetching promoter sequences...",
        "fetching_mrna": "Fetching mRNA sequences...",
        "fetching_protein": "Fetching protein sequences...",
        "no_genomic": "No genomic sequences were found for the selected records.",
        "no_promoter": "No promoter sequences were found for the selected records.",
        "genomic_unavailable_mrna_protein_ok": "No genomic locations are available for the selected records, but you can still download mRNA and protein sequences.",
        "promoter_requires_genomic": "Promoter sequences require available genomic locations.",
        "no_mrna": "No mRNA sequences were found for the selected records.",
        "no_protein": "No protein sequences were found for the selected records.",
        "genomic_http_error": "NCBI returned an HTTP error while fetching genomic sequences: {error}",
        "promoter_http_error": "NCBI returned an HTTP error while fetching promoter sequences: {error}",
        "mrna_http_error": "NCBI returned an HTTP error while fetching mRNA sequences: {error}",
        "protein_http_error": "NCBI returned an HTTP error while fetching protein sequences: {error}",
        "genomic_fetch_error": "Could not fetch genomic sequences: {error}",
        "promoter_fetch_error": "Could not fetch promoter sequences: {error}",
        "mrna_fetch_error": "Could not fetch mRNA sequences: {error}",
        "protein_fetch_error": "Could not fetch protein sequences: {error}",
        "enable_one": "Enable at least one record in the table to generate multi-FASTA.",
        "genomic_section": "Genomic multi-FASTA",
        "promoter_section": "Promoter multi-FASTA",
        "mrna_section": "mRNA multi-FASTA",
        "protein_section": "Protein multi-FASTA",
        "download_genomic": "Download genomic multi-FASTA",
        "download_promoter": "Download promoter multi-FASTA",
        "download_mrna": "Download mRNA multi-FASTA",
        "download_protein": "Download protein multi-FASTA",
        "preview_genomic": "Genomic sequence preview",
        "preview_promoter": "Promoter sequence preview",
        "preview_mrna": "mRNA sequence preview",
        "preview_protein": "Protein sequence preview",
        "no_matches": "No matching gene records were found for the given query.",
        "caption": "Data source: NCBI Entrez E-utilities. Genomic sequences are extracted from gene coordinates in the Gene record, promoter sequences are an approximate upstream region relative to gene orientation, mRNA sequences come from linked RefSeq RNA records, and protein sequences come from records linked to the gene.",
    },
}


st.set_page_config(
    page_title="Sequence Fetcher",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "language" not in st.session_state:
    st.session_state["language"] = "pl"


def t(key: str, **kwargs) -> str:
    language = st.session_state.get("language", "pl")
    template = TRANSLATIONS.get(language, TRANSLATIONS["pl"]).get(key, key)
    return template.format(**kwargs) if kwargs else template


def set_language(language_code: str) -> None:
    st.session_state["language"] = language_code


def build_ncbi_params(email: str, api_key: str) -> dict:
    params = {"tool": "sequence-fetcher-streamlit"}
    if email:
        params["email"] = email.strip()
    if api_key:
        params["api_key"] = api_key.strip()
    return params


def ncbi_get(endpoint: str, params: dict, response_mode: str = "json"):
    last_error = None
    for attempt in range(3):
        response = requests.get(
            f"{EUTILS_BASE}/{endpoint}",
            params=params,
            headers=DEFAULT_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code not in {429, 500, 502, 503, 504}:
            response.raise_for_status()
            if response_mode == "text":
                return response.text
            return response.json()

        last_error = requests.HTTPError(
            f"{response.status_code} error for {response.url}",
            response=response,
        )
        if attempt < 2:
            time.sleep(1.5 * (attempt + 1))

    raise last_error


def run_gene_search(query: str, email: str, api_key: str, max_records: int):
    search_params = {
        "db": "gene",
        "term": query,
        "retmode": "json",
        "retmax": max_records,
        **build_ncbi_params(email, api_key),
    }
    search_result = ncbi_get("esearch.fcgi", search_params)
    return search_result.get("esearchresult", {}).get("idlist", [])


def normalize_text(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def calculate_nucleotide_length(genomic_info: list[dict]) -> Optional[int]:
    segment_lengths = []
    for location in genomic_info or []:
        start = location.get("chrstart")
        stop = location.get("chrstop")
        if start is None or stop is None:
            continue
        segment_lengths.append(abs(int(stop) - int(start)) + 1)
    return sum(segment_lengths) if segment_lengths else None


@st.cache_data(show_spinner=False)
def fetch_primary_protein_info(gene_id: str, email: str, api_key: str) -> dict:
    protein_ids = fetch_linked_ids(
        gene_id=gene_id,
        target_db="protein",
        preferred_link_name="gene_protein_refseq",
        fallback_link_name="gene_protein",
        email=email,
        api_key=api_key,
    )
    if not protein_ids:
        return {"length": None, "accession": None}

    summary_result = ncbi_get(
        "esummary.fcgi",
        {
            "db": "protein",
            "id": protein_ids[0],
            "retmode": "json",
            **build_ncbi_params(email, api_key),
        },
    )
    summary_item = summary_result.get("result", {}).get(str(protein_ids[0]), {})
    protein_length = summary_item.get("slen")
    return {
        "length": int(protein_length) if protein_length is not None else None,
        "accession": summary_item.get("accessionversion") or summary_item.get("caption"),
    }


@st.cache_data(show_spinner=False)
def fetch_primary_mrna_info(gene_id: str, email: str, api_key: str) -> dict:
    mrna_ids, link_source = fetch_linked_ids_with_source(
        gene_id=gene_id,
        target_db="nuccore",
        preferred_link_name="gene_nuccore_refseqrna",
        fallback_link_name="gene_nuccore",
        email=email,
        api_key=api_key,
    )
    if not mrna_ids:
        return {"length": None, "accession": None}

    if link_source == "gene_nuccore_refseqrna":
        summary_result = fetch_nuccore_summaries((str(mrna_ids[0]),), email=email, api_key=api_key)
        summary_item = summary_result.get(str(mrna_ids[0]), {})
        mrna_length = summary_item.get("slen")
        return {
            "length": int(mrna_length) if mrna_length is not None else None,
            "accession": summary_item.get("accessionversion") or summary_item.get("caption"),
        }

    for index in range(0, len(mrna_ids), 100):
        chunk_ids = tuple(str(mrna_id) for mrna_id in mrna_ids[index:index + 100])
        summary_result = fetch_nuccore_summaries(chunk_ids, email=email, api_key=api_key)
        for mrna_id in chunk_ids:
            item = summary_result.get(str(mrna_id), {})
            biomol = (item.get("biomol") or "").lower()
            moltype = (item.get("moltype") or "").lower()
            accession = (item.get("accessionversion") or "").upper()
            if biomol == "mrna" or moltype in {"mrna", "rna"} or accession.startswith(("NM_", "XM_", "XR_", "NR_")):
                mrna_length = item.get("slen")
                return {
                    "length": int(mrna_length) if mrna_length is not None else None,
                    "accession": item.get("accessionversion") or item.get("caption"),
                }

    return {"length": None, "accession": None}


@st.cache_data(show_spinner=False)
def search_gene_records(gene_name: str, organism_name: str, email: str, api_key: str, max_records: int):
    gene_name = gene_name.strip()
    organism_name = organism_name.strip()

    exact_query = f'{gene_name}[Gene Name] AND "{organism_name}"[Organism]'
    broad_query = f'{gene_name}[All Fields] AND "{organism_name}"[Organism]'

    exact_ids = run_gene_search(exact_query, email=email, api_key=api_key, max_records=max_records)
    broad_ids = run_gene_search(broad_query, email=email, api_key=api_key, max_records=max_records * 3)

    gene_ids = []
    for gene_id in exact_ids + broad_ids:
        if gene_id not in gene_ids:
            gene_ids.append(gene_id)

    if not gene_ids:
        return []

    summary_params = {
        "db": "gene",
        "id": ",".join(gene_ids),
        "retmode": "json",
        **build_ncbi_params(email, api_key),
    }
    summary_result = ncbi_get("esummary.fcgi", summary_params)

    records = []
    result_block = summary_result.get("result", {})
    for uid in result_block.get("uids", []):
        item = result_block.get(uid, {})
        organism = item.get("organism", {}) or {}
        genomic_info = item.get("genomicinfo", []) or []
        nucleotide_length = calculate_nucleotide_length(genomic_info)
        mrna_info = fetch_primary_mrna_info(uid, email=email, api_key=api_key)
        protein_info = fetch_primary_protein_info(uid, email=email, api_key=api_key)
        records.append(
            {
                "gene_id": uid,
                "symbol": item.get("name", ""),
                "description": item.get("description", ""),
                "other_aliases": item.get("otheraliases", ""),
                "nomenclature_symbol": item.get("nomenclaturesymbol", ""),
                "nomenclature_name": item.get("nomenclaturename", ""),
                "organism": organism.get("scientificname", ""),
                "taxid": organism.get("taxid", ""),
                "chromosome": item.get("chromosome", ""),
                "map_location": item.get("maplocation", ""),
                "genomicinfo": genomic_info,
                "genomic_count": len(genomic_info),
                "nucleotide_length": nucleotide_length,
                "mrna_length": mrna_info.get("length"),
                "mrna_accession": mrna_info.get("accession"),
                "protein_length": protein_info.get("length"),
                "protein_accession": protein_info.get("accession"),
            }
        )

    gene_name_lower = normalize_text(gene_name)
    organism_lower = normalize_text(organism_name)

    def sort_key(record: dict):
        symbol_text = normalize_text(record["symbol"])
        description_text = normalize_text(record["description"])
        alias_text = normalize_text(record["other_aliases"])
        nomenclature_symbol_text = normalize_text(record["nomenclature_symbol"])
        nomenclature_name_text = normalize_text(record["nomenclature_name"])
        organism_text = normalize_text(record["organism"])

        symbol_exact = symbol_text == gene_name_lower
        nomenclature_symbol_exact = nomenclature_symbol_text == gene_name_lower
        alias_exact = gene_name_lower in {alias.strip() for alias in alias_text.split(",") if alias.strip()}
        description_contains = gene_name_lower in description_text
        alias_contains = gene_name_lower in alias_text
        nomenclature_name_contains = gene_name_lower in nomenclature_name_text
        symbol_contains = gene_name_lower in symbol_text
        organism_exact = organism_text == organism_lower
        organism_prefix = organism_text.startswith(organism_lower)
        has_genomic_info = record["genomic_count"] > 0
        return (
            not symbol_exact,
            not nomenclature_symbol_exact,
            not alias_exact,
            not description_contains,
            not alias_contains,
            not nomenclature_name_contains,
            not symbol_contains,
            not organism_exact,
            not organism_prefix,
            not has_genomic_info,
            record["organism"],
            record["gene_id"],
        )

    return sorted(records, key=sort_key)[:max_records]


def format_fasta(header: str, sequence: str, width: int = 70) -> str:
    clean_sequence = "".join(sequence.split())
    wrapped = "\n".join(wrap(clean_sequence, width))
    return f">{header}\n{wrapped}" if wrapped else f">{header}"


def extract_sequence_from_fasta(fasta_text: str) -> str:
    return "".join(line.strip() for line in fasta_text.splitlines() if line and not line.startswith(">"))


def parse_fasta_records(fasta_text: str) -> list[tuple[str, str]]:
    records = []
    header = None
    sequence_lines = []

    for raw_line in fasta_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header is not None:
                records.append((header, "".join(sequence_lines)))
            header = line[1:]
            sequence_lines = []
        else:
            sequence_lines.append(line)

    if header is not None:
        records.append((header, "".join(sequence_lines)))

    return records


def build_genomic_locus_label(record: dict) -> str:
    loci = []
    for index, location in enumerate(record.get("genomicinfo", []) or [], start=1):
        accession = location.get("chraccver")
        start = location.get("chrstart")
        stop = location.get("chrstop")
        if accession is None or start is None or stop is None:
            continue

        start = int(start)
        stop = int(stop)
        seq_start = min(start, stop) + 1
        seq_stop = max(start, stop) + 1
        strand = "+" if start <= stop else "-"
        loci.append(f"{accession}:{seq_start}-{seq_stop}:{strand}:seg{index}")

    return ",".join(loci) if loci else "unknown"


@st.cache_data(show_spinner=False)
def fetch_nuccore_summaries(nuccore_ids: tuple[str, ...], email: str, api_key: str) -> dict:
    if not nuccore_ids:
        return {}

    combined_result = {"uids": []}
    for index in range(0, len(nuccore_ids), 100):
        chunk_ids = nuccore_ids[index:index + 100]
        summary_result = ncbi_get(
            "esummary.fcgi",
            {
                "db": "nuccore",
                "id": ",".join(chunk_ids),
                "retmode": "json",
                **build_ncbi_params(email, api_key),
            },
        )
        result_block = summary_result.get("result", {})
        combined_result["uids"].extend(result_block.get("uids", []))
        for uid in result_block.get("uids", []):
            combined_result[uid] = result_block.get(uid, {})

    return combined_result


@st.cache_data(show_spinner=False)
def fetch_nuccore_length(nuccore_id: str, email: str, api_key: str) -> Optional[int]:
    summary_result = fetch_nuccore_summaries((str(nuccore_id),), email=email, api_key=api_key)
    summary_uid_list = summary_result.get("uids", [])
    summary_item = summary_result.get(str(nuccore_id), {})
    if not summary_item and summary_uid_list:
        summary_item = summary_result.get(str(summary_uid_list[0]), {})
    sequence_length = summary_item.get("slen")
    return int(sequence_length) if sequence_length is not None else None


def fetch_genomic_multifasta(records: list[dict], email: str, api_key: str):
    entries = []
    for record in records:
        genomic_info = record.get("genomicinfo", []) or []
        for index, location in enumerate(genomic_info, start=1):
            accession = location.get("chraccver")
            start = location.get("chrstart")
            stop = location.get("chrstop")
            if accession is None or start is None or stop is None:
                continue

            start = int(start)
            stop = int(stop)
            seq_start = min(start, stop) + 1
            seq_stop = max(start, stop) + 1
            strand = 1 if start <= stop else 2

            fasta_text = ncbi_get(
                "efetch.fcgi",
                {
                    "db": "nuccore",
                    "id": accession,
                    "rettype": "fasta",
                    "retmode": "text",
                    "seq_start": seq_start,
                    "seq_stop": seq_stop,
                    "strand": strand,
                    **build_ncbi_params(email, api_key),
                },
                response_mode="text",
            )
            sequence = extract_sequence_from_fasta(fasta_text)
            if not sequence:
                continue

            header = (
                f"{record['symbol']}|gene_id={record['gene_id']}|organism={record['organism']}|"
                f"sequence_type=genomic|accession={accession}|segment={index}|range={seq_start}-{seq_stop}|strand={'+' if strand == 1 else '-'}"
            )
            entries.append(format_fasta(header, sequence))

    return "\n".join(entries)


def fetch_promoter_multifasta(records: list[dict], email: str, api_key: str, promoter_length: int):
    entries = []
    requested_length = max(1, int(promoter_length))
    for record in records:
        genomic_info = record.get("genomicinfo", []) or []
        for index, location in enumerate(genomic_info, start=1):
            accession = location.get("chraccver")
            start = location.get("chrstart")
            stop = location.get("chrstop")
            if accession is None or start is None or stop is None:
                continue

            start = int(start)
            stop = int(stop)
            sequence_length = fetch_nuccore_length(str(accession), email=email, api_key=api_key)
            if not sequence_length:
                continue

            if start <= stop:
                gene_start = min(start, stop) + 1
                promoter_start = max(1, gene_start - requested_length)
                promoter_stop = gene_start - 1
                strand = 1
            else:
                gene_start = max(start, stop) + 1
                promoter_start = gene_start + 1
                promoter_stop = min(sequence_length, gene_start + requested_length)
                strand = 2

            if promoter_start > promoter_stop:
                continue

            fasta_text = ncbi_get(
                "efetch.fcgi",
                {
                    "db": "nuccore",
                    "id": accession,
                    "rettype": "fasta",
                    "retmode": "text",
                    "seq_start": promoter_start,
                    "seq_stop": promoter_stop,
                    "strand": strand,
                    **build_ncbi_params(email, api_key),
                },
                response_mode="text",
            )
            sequence = extract_sequence_from_fasta(fasta_text)
            if not sequence:
                continue

            header = (
                f"{record['symbol']}|gene_id={record['gene_id']}|organism={record['organism']}|"
                f"sequence_type=promoter|accession={accession}|segment={index}|"
                f"promoter_requested_nt={requested_length}|promoter_length_nt={len(sequence)}|"
                f"range={promoter_start}-{promoter_stop}|strand={'+' if strand == 1 else '-'}"
            )
            entries.append(format_fasta(header, sequence))

    return "\n".join(entries)


def fetch_mrna_multifasta(records: list[dict], email: str, api_key: str, max_mrna_per_gene: int):
    entries = []
    for record in records:
        mrna_ids, link_source = fetch_linked_ids_with_source(
            gene_id=record["gene_id"],
            target_db="nuccore",
            preferred_link_name="gene_nuccore_refseqrna",
            fallback_link_name="gene_nuccore",
            email=email,
            api_key=api_key,
        )
        if not mrna_ids:
            continue

        if link_source == "gene_nuccore_refseqrna":
            filtered_ids = [str(mrna_id) for mrna_id in mrna_ids[:max_mrna_per_gene]]
        else:
            filtered_ids = []
            for index in range(0, len(mrna_ids), 100):
                chunk_ids = tuple(str(mrna_id) for mrna_id in mrna_ids[index:index + 100])
                summary_result = fetch_nuccore_summaries(chunk_ids, email=email, api_key=api_key)
                for mrna_id in chunk_ids:
                    item = summary_result.get(str(mrna_id), {})
                    biomol = (item.get("biomol") or "").lower()
                    moltype = (item.get("moltype") or "").lower()
                    accession = (item.get("accessionversion") or "").upper()
                    if biomol == "mrna" or moltype in {"mrna", "rna"} or accession.startswith(("NM_", "XM_", "XR_", "NR_")):
                        filtered_ids.append(str(mrna_id))
                    if len(filtered_ids) >= max_mrna_per_gene:
                        break
                if len(filtered_ids) >= max_mrna_per_gene:
                    break

        if not filtered_ids:
            continue

        limited_ids = filtered_ids[:max_mrna_per_gene]
        limited_summary = fetch_nuccore_summaries(tuple(limited_ids), email=email, api_key=api_key)
        fasta_text = ncbi_get(
            "efetch.fcgi",
            {
                "db": "nuccore",
                "id": ",".join(limited_ids),
                "rettype": "fasta",
                "retmode": "text",
                **build_ncbi_params(email, api_key),
            },
            response_mode="text",
        ).strip()
        if not fasta_text:
            continue

        genomic_locus = build_genomic_locus_label(record)
        mrna_records = parse_fasta_records(fasta_text)
        for mrna_id, (_, sequence) in zip(limited_ids, mrna_records):
            summary_item = limited_summary.get(str(mrna_id), {})
            accession = summary_item.get("accessionversion") or summary_item.get("caption") or mrna_id
            mrna_title = summary_item.get("title", "")
            mrna_length = summary_item.get("slen")
            header = (
                f"{record['symbol']}|gene_id={record['gene_id']}|organism={record['organism']}|"
                f"sequence_type=mrna|mrna_accession={accession}|mrna_length_nt={mrna_length or len(sequence)}|"
                f"genomic_locus={genomic_locus}|mrna_title={mrna_title}"
            )
            entries.append(format_fasta(header, sequence))

    return "\n".join(entries)


def fetch_linked_ids(gene_id: str, target_db: str, preferred_link_name: str, fallback_link_name: str, email: str, api_key: str):
    ids, _ = fetch_linked_ids_with_source(
        gene_id=gene_id,
        target_db=target_db,
        preferred_link_name=preferred_link_name,
        fallback_link_name=fallback_link_name,
        email=email,
        api_key=api_key,
    )
    return ids


def fetch_linked_ids_with_source(gene_id: str, target_db: str, preferred_link_name: str, fallback_link_name: str, email: str, api_key: str):
    link_result = ncbi_get(
        "elink.fcgi",
        {
            "dbfrom": "gene",
            "db": target_db,
            "id": gene_id,
            "retmode": "json",
            **build_ncbi_params(email, api_key),
        },
    )
    linksets = link_result.get("linksets", [])
    if not linksets:
        return [], None

    link_blocks = linksets[0].get("linksetdbs", []) or []
    links_by_name = {block.get("linkname"): block.get("links", []) for block in link_blocks}
    if links_by_name.get(preferred_link_name):
        return links_by_name.get(preferred_link_name) or [], preferred_link_name
    if links_by_name.get(fallback_link_name):
        return links_by_name.get(fallback_link_name) or [], fallback_link_name
    return [], None


def fetch_protein_multifasta(records: list[dict], email: str, api_key: str, max_proteins_per_gene: int):
    entries = []
    for record in records:
        protein_ids = fetch_linked_ids(
            gene_id=record["gene_id"],
            target_db="protein",
            preferred_link_name="gene_protein_refseq",
            fallback_link_name="gene_protein",
            email=email,
            api_key=api_key,
        )
        if not protein_ids:
            continue

        limited_ids = protein_ids[:max_proteins_per_gene]
        protein_summary = ncbi_get(
            "esummary.fcgi",
            {
                "db": "protein",
                "id": ",".join(limited_ids),
                "retmode": "json",
                **build_ncbi_params(email, api_key),
            },
        )
        summary_result = protein_summary.get("result", {})
        fasta_text = ncbi_get(
            "efetch.fcgi",
            {
                "db": "protein",
                "id": ",".join(limited_ids),
                "rettype": "fasta",
                "retmode": "text",
                **build_ncbi_params(email, api_key),
            },
            response_mode="text",
        ).strip()
        if fasta_text:
            genomic_locus = build_genomic_locus_label(record)
            protein_records = parse_fasta_records(fasta_text)
            for protein_id, (_, sequence) in zip(limited_ids, protein_records):
                summary_item = summary_result.get(str(protein_id), {})
                accession = summary_item.get("accessionversion") or summary_item.get("caption") or protein_id
                protein_title = summary_item.get("title", "")
                protein_length = summary_item.get("slen")
                header = (
                    f"{record['symbol']}|gene_id={record['gene_id']}|organism={record['organism']}|"
                    f"protein_accession={accession}|protein_length_aa={protein_length or len(sequence)}|"
                    f"genomic_locus={genomic_locus}|protein_title={protein_title}"
                )
                entries.append(format_fasta(header, sequence))

    return "\n".join(entries)


st.markdown(
    f"""
    <style>
        .stApp {{
            background:
                radial-gradient(circle at top left, rgba(27, 144, 122, 0.12), transparent 28%),
                radial-gradient(circle at top right, rgba(230, 122, 35, 0.10), transparent 25%),
                linear-gradient(180deg, #f7f4ed 0%, #f4f7f3 100%);
        }}

        .hero {{
            padding: 1.6rem 1.8rem;
            border-radius: 24px;
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid rgba(19, 52, 59, 0.10);
            box-shadow: 0 18px 40px rgba(19, 52, 59, 0.08);
            margin-bottom: 1.25rem;
        }}

        .hero h1 {{
            margin: 0 0 0.35rem 0;
            color: #13343b;
            font-size: 2.3rem;
        }}

        .hero p {{
            margin: 0;
            color: #34565b;
            font-size: 1rem;
            max-width: 56rem;
        }}

        .metric-card {{
            padding: 1rem 1.1rem;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.80);
            border: 1px solid rgba(19, 52, 59, 0.08);
        }}
    </style>

    <div class="hero">
        <h1>{t("hero_title")}</h1>
        <p>{t("hero_body")}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(f"**{t('sidebar_language')}**")
    lang_col1, lang_col2 = st.columns(2)
    lang_col1.button(
        LANGUAGE_BUTTONS["pl"],
        key="lang_button_pl",
        use_container_width=True,
        type="primary" if st.session_state.get("language", "pl") == "pl" else "secondary",
        on_click=set_language,
        args=("pl",),
    )
    lang_col2.button(
        LANGUAGE_BUTTONS["en"],
        key="lang_button_en",
        use_container_width=True,
        type="primary" if st.session_state.get("language", "pl") == "en" else "secondary",
        on_click=set_language,
        args=("en",),
    )
    st.subheader(t("settings"))
    email = st.text_input(
        t("ncbi_email"),
        help=t("ncbi_email_help"),
        placeholder=t("ncbi_email_placeholder"),
    ).strip()
    api_key = st.text_input(
        t("ncbi_api_key"),
        type="password",
        help=t("ncbi_api_key_help"),
    ).strip()
    max_gene_hits = st.slider(t("max_gene_hits"), min_value=1, max_value=50, value=15)
    promoter_length = st.number_input(
        t("promoter_length"),
        min_value=1,
        value=500,
        step=50,
        help=t("promoter_length_help"),
    )
    max_mrna_per_gene = st.slider(t("max_mrna_per_gene"), min_value=1, max_value=20, value=5)
    max_proteins_per_gene = st.slider(t("max_proteins_per_gene"), min_value=1, max_value=20, value=5)

with st.form("sequence-search-form"):
    col1, col2 = st.columns(2)
    organism_name = col1.text_input(t("organism_name"), placeholder="Escherichia coli")
    gene_name = col2.text_input(t("gene_name"), placeholder="relA")
    submitted = st.form_submit_button(t("search_records"), use_container_width=True)

if submitted:
    if not organism_name.strip() or not gene_name.strip():
        st.error(t("provide_both"))
    else:
        try:
            st.session_state.pop("genomic_fasta", None)
            st.session_state.pop("promoter_fasta", None)
            st.session_state.pop("mrna_fasta", None)
            st.session_state.pop("protein_fasta", None)
            st.session_state.pop("record_selector_editor", None)
            with st.spinner(t("searching_records")):
                records = search_gene_records(
                    gene_name=gene_name,
                    organism_name=organism_name,
                    email=email,
                    api_key=api_key,
                    max_records=max_gene_hits,
                )
            st.session_state["sequence_records"] = records
            st.session_state["record_selection"] = {
                record["gene_id"]: index < min(5, len(records)) for index, record in enumerate(records)
            }
            st.session_state["sequence_search_context"] = {
                "gene_name": gene_name.strip(),
                "organism_name": organism_name.strip(),
            }
        except requests.HTTPError as exc:
            st.error(t("http_error", error=exc))
        except requests.RequestException as exc:
            st.error(t("connection_error", error=exc))

records = st.session_state.get("sequence_records", [])
search_context = st.session_state.get("sequence_search_context", {})

if records:
    st.markdown(f"### {t('matched_gene_records')}")
    record_selection = st.session_state.get("record_selection", {})
    sort_col1, sort_col2 = st.columns([2, 1])
    sort_by = sort_col1.selectbox(
        t("sort_by"),
        options=["relevance", "genomic_nt", "mrna_nt", "aa", "symbol", "organism"],
        format_func=lambda key: {
            "relevance": t("sort_relevance"),
            "genomic_nt": t("sort_genomic_nt"),
            "mrna_nt": t("sort_mrna_nt"),
            "aa": t("sort_aa"),
            "symbol": t("sort_symbol"),
            "organism": t("sort_organism"),
        }[key],
        index=0,
    )
    descending = sort_col2.checkbox(t("descending"), value=False if sort_by == "relevance" else True)

    sorted_records = list(records)
    if sort_by != "relevance":
        if sort_by == "genomic_nt":
            sorted_records = sorted(
                sorted_records,
                key=lambda record: (
                    record["nucleotide_length"] is None,
                    -(record["nucleotide_length"] or 0) if descending else (record["nucleotide_length"] or 0),
                ),
            )
        elif sort_by == "mrna_nt":
            sorted_records = sorted(
                sorted_records,
                key=lambda record: (
                    record["mrna_length"] is None,
                    -(record["mrna_length"] or 0) if descending else (record["mrna_length"] or 0),
                ),
            )
        elif sort_by == "aa":
            sorted_records = sorted(
                sorted_records,
                key=lambda record: (
                    record["protein_length"] is None,
                    -(record["protein_length"] or 0) if descending else (record["protein_length"] or 0),
                ),
            )
        else:
            sort_key_map = {
                "symbol": lambda record: normalize_text(record["symbol"]),
                "organism": lambda record: normalize_text(record["organism"]),
            }
            sorted_records = sorted(sorted_records, key=sort_key_map[sort_by], reverse=descending)

    include_column = t("col_include")
    gene_id_column = t("col_gene_id")
    symbol_column = t("col_symbol")
    description_column = t("col_description")
    organism_column = t("col_organism")
    taxid_column = t("col_taxid")
    genomic_nt_column = t("col_genomic_nt")
    mrna_accession_column = t("col_mrna_accession")
    mrna_nt_column = t("col_mrna_nt")
    protein_accession_column = t("col_protein_accession")
    aa_column = t("col_aa")
    genomic_locations_column = t("col_genomic_locations")

    preview_df = pd.DataFrame(
        [
            {
                include_column: record_selection.get(record["gene_id"], False),
                gene_id_column: record["gene_id"],
                symbol_column: record["symbol"],
                description_column: record["description"],
                organism_column: record["organism"],
                taxid_column: record["taxid"],
                genomic_nt_column: record["nucleotide_length"] if record["nucleotide_length"] is not None else "-",
                mrna_accession_column: record["mrna_accession"] if record.get("mrna_accession") else "-",
                mrna_nt_column: record["mrna_length"] if record["mrna_length"] is not None else "-",
                protein_accession_column: record["protein_accession"] if record.get("protein_accession") else "-",
                aa_column: record["protein_length"] if record["protein_length"] is not None else "-",
                genomic_locations_column: record["genomic_count"],
            }
            for record in sorted_records
        ]
    )

    stat_col1, stat_col2, stat_col3 = st.columns(3)
    stat_col1.markdown(f'<div class="metric-card"><strong>{t("gene_hits")}</strong><br>{len(records)}</div>', unsafe_allow_html=True)
    stat_col2.markdown(
        f'<div class="metric-card"><strong>{t("organism")}</strong><br>{search_context.get("organism_name", "")}</div>',
        unsafe_allow_html=True,
    )
    stat_col3.markdown(
        f'<div class="metric-card"><strong>{t("gene")}</strong><br>{search_context.get("gene_name", "")}</div>',
        unsafe_allow_html=True,
    )

    selector_df = st.data_editor(
        preview_df,
        key="record_selector_editor",
        use_container_width=True,
        hide_index=True,
        column_config={
            include_column: st.column_config.CheckboxColumn(
                t("on_off"),
                help=t("on_off_help"),
                default=False,
            ),
            genomic_nt_column: st.column_config.TextColumn(genomic_nt_column),
            mrna_accession_column: st.column_config.TextColumn(mrna_accession_column),
            mrna_nt_column: st.column_config.TextColumn(mrna_nt_column),
            protein_accession_column: st.column_config.TextColumn(protein_accession_column),
            aa_column: st.column_config.TextColumn(aa_column),
        },
        disabled=[gene_id_column, symbol_column, description_column, organism_column, taxid_column, genomic_nt_column, mrna_accession_column, mrna_nt_column, protein_accession_column, aa_column, genomic_locations_column],
    )

    selected_gene_ids = set(selector_df.loc[selector_df[include_column], gene_id_column].astype(str).tolist())
    st.session_state["record_selection"] = {
        str(row[gene_id_column]): bool(row[include_column]) for _, row in selector_df.iterrows()
    }
    selected_records = [record for record in sorted_records if record["gene_id"] in selected_gene_ids]
    selected_records_with_genomic = [record for record in selected_records if (record.get("genomicinfo") or [])]

    active_col, inactive_col = st.columns(2)
    active_col.caption(t("active_records", count=len(selected_records)))
    inactive_col.caption(t("inactive_records", count=len(records) - len(selected_records)))

    if selected_records:
        action_col1, action_col2, action_col3, action_col4 = st.columns(4)

        with action_col1:
            if st.button(t("generate_genomic"), use_container_width=True):
                try:
                    with st.spinner(t("fetching_genomic")):
                        genomic_fasta = fetch_genomic_multifasta(selected_records_with_genomic, email=email, api_key=api_key)
                    st.session_state["genomic_fasta"] = genomic_fasta
                    if not genomic_fasta:
                        st.info(t("no_genomic"))
                        if selected_records and not selected_records_with_genomic:
                            st.caption(t("genomic_unavailable_mrna_protein_ok"))
                except requests.HTTPError as exc:
                    st.error(t("genomic_http_error", error=exc))
                except requests.RequestException as exc:
                    st.error(t("genomic_fetch_error", error=exc))

        with action_col2:
            if st.button(t("generate_promoter"), use_container_width=True):
                try:
                    with st.spinner(t("fetching_promoter")):
                        promoter_fasta = fetch_promoter_multifasta(
                            selected_records_with_genomic,
                            email=email,
                            api_key=api_key,
                            promoter_length=int(promoter_length),
                        )
                    st.session_state["promoter_fasta"] = promoter_fasta
                    if not promoter_fasta:
                        st.info(t("no_promoter"))
                        if selected_records and not selected_records_with_genomic:
                            st.caption(t("promoter_requires_genomic"))
                            st.caption(t("genomic_unavailable_mrna_protein_ok"))
                except requests.HTTPError as exc:
                    st.error(t("promoter_http_error", error=exc))
                except requests.RequestException as exc:
                    st.error(t("promoter_fetch_error", error=exc))

        with action_col3:
            if st.button(t("generate_mrna"), use_container_width=True):
                try:
                    with st.spinner(t("fetching_mrna")):
                        mrna_fasta = fetch_mrna_multifasta(
                            selected_records,
                            email=email,
                            api_key=api_key,
                            max_mrna_per_gene=max_mrna_per_gene,
                        )
                    st.session_state["mrna_fasta"] = mrna_fasta
                    if not mrna_fasta:
                        st.info(t("no_mrna"))
                except requests.HTTPError as exc:
                    st.error(t("mrna_http_error", error=exc))
                except requests.RequestException as exc:
                    st.error(t("mrna_fetch_error", error=exc))

        with action_col4:
            if st.button(t("generate_protein"), use_container_width=True):
                try:
                    with st.spinner(t("fetching_protein")):
                        protein_fasta = fetch_protein_multifasta(
                            selected_records,
                            email=email,
                            api_key=api_key,
                            max_proteins_per_gene=max_proteins_per_gene,
                        )
                    st.session_state["protein_fasta"] = protein_fasta
                    if not protein_fasta:
                        st.info(t("no_protein"))
                except requests.HTTPError as exc:
                    st.error(t("protein_http_error", error=exc))
                except requests.RequestException as exc:
                    st.error(t("protein_fetch_error", error=exc))
    else:
        st.info(t("enable_one"))

    genomic_fasta = st.session_state.get("genomic_fasta", "")
    promoter_fasta = st.session_state.get("promoter_fasta", "")
    mrna_fasta = st.session_state.get("mrna_fasta", "")
    protein_fasta = st.session_state.get("protein_fasta", "")

    if genomic_fasta:
        st.markdown(f"### {t('genomic_section')}")
        st.download_button(
            t("download_genomic"),
            data=genomic_fasta,
            file_name=f"{search_context.get('organism_name', 'organism')}_{search_context.get('gene_name', 'gene')}_genomic.fasta".replace(" ", "_"),
            mime="text/plain",
            use_container_width=True,
        )
        st.text_area(t("preview_genomic"), genomic_fasta, height=260)

    if promoter_fasta:
        st.markdown(f"### {t('promoter_section')}")
        st.download_button(
            t("download_promoter"),
            data=promoter_fasta,
            file_name=f"{search_context.get('organism_name', 'organism')}_{search_context.get('gene_name', 'gene')}_promoter_{int(promoter_length)}nt.fasta".replace(" ", "_"),
            mime="text/plain",
            use_container_width=True,
        )
        st.text_area(t("preview_promoter"), promoter_fasta, height=260)

    if mrna_fasta:
        st.markdown(f"### {t('mrna_section')}")
        st.download_button(
            t("download_mrna"),
            data=mrna_fasta,
            file_name=f"{search_context.get('organism_name', 'organism')}_{search_context.get('gene_name', 'gene')}_mrna.fasta".replace(" ", "_"),
            mime="text/plain",
            use_container_width=True,
        )
        st.text_area(t("preview_mrna"), mrna_fasta, height=260)

    if protein_fasta:
        st.markdown(f"### {t('protein_section')}")
        st.download_button(
            t("download_protein"),
            data=protein_fasta,
            file_name=f"{search_context.get('organism_name', 'organism')}_{search_context.get('gene_name', 'gene')}_protein.fasta".replace(" ", "_"),
            mime="text/plain",
            use_container_width=True,
        )
        st.text_area(t("preview_protein"), protein_fasta, height=260)

elif submitted:
    st.warning(t("no_matches"))

st.caption(
    t("caption")
)