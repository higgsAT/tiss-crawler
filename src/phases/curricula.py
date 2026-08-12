import logging
from src import http_client
from src import parser
from src import storage

def fetch_all_curricula(
    page_source: str,
    output_dir: str,
    semester: str,
    lang: str
) -> dict:
    """
    Process a page source which contains information about curricula. Returns None upon failure.

    Returns a dict with following formatting (faculty, curricula_name, curricula_url):
    {
        '37047':
            ('Architektur', '033 243', 'Bachelorstudium Architektur', '/curriculum/public/curriculum.xhtml?key=37047', 'de'),
        '41934':
            ('Architektur', '066 443', 'Masterstudium Architektur', '/curriculum/public/curriculum.xhtml?key=41934', 'de'),
        '42323':
            ('Architektur', '066 444', 'Masterstudium Building Sciences and Environment', '/curriculum/public/curriculum.xhtml?key=42323', 'de'),
            .
            .
            .
    }
    """
    log = logging.getLogger(__name__)
    log.info(f"processing curricula page source")

    # save the page source to the disk under:
    # output/
    #   study_programs/
    #     study_programs__<semester>.html
    curricula_dir_write = f"{output_dir}study_programs/"
    filename = f"study_programs__{lang}__{semester}.html"
    storage.write_to_disk(page_source, curricula_dir_write, filename)

    # extract all possible curricula from the page source
    return parser.extract_curricula(page_source, lang)
