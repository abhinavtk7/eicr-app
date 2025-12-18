import time
from doctr.models import ocr_predictor
from eicr_package.extractor import EICRSupplyExtractor
from eicr_package.eicr_parser import get_eicr_info
from eicr_package.eicr_boards import EICRProcessor
import fitz
import json

def process_eicr_pdf(pdf_path):
    """Internal logic to process the PDF using the package."""
    start_time = time.time()
    # Load model (cached if possible, but here we load per call as per your snippet)
    ocr_model = ocr_predictor(pretrained=True)

    eicr_main_record = get_eicr_info(pdf_path, ocr_model)
    # output_name = eicr_main_record["Report Number"]["value"]

    page_num = _get_supply_char_page_no(pdf_path)
    extractor = EICRSupplyExtractor(template_path="./eicr_package/template.png")
    supply_characteristics, particulars_of_installation = extractor.extract(
        pdf_path,
        page_number=page_num
    )

    processor = EICRProcessor()
    boards_data = processor.process_pdf(pdf_path)

    merged = {
        "eicr_main_record": eicr_main_record,
        "supply_characteristics": supply_characteristics,
        "particulars_of_installation": particulars_of_installation,
        **boards_data
    }
    end_time = time.time()
    elapsed = end_time - start_time

    # Print to console (visible in the notebook output log)
    print(f"Total Extraction Time: {elapsed:.2f} seconds")

    merged_json = json.dumps(merged, indent=2, ensure_ascii=False)
    # with open(merged, "w", encoding="utf-8") as f:
    #     json.dump(merged, f, indent=2, ensure_ascii=False)
    return merged_json

def _get_supply_char_page_no(pdf_path):
    doc = fitz.open(pdf_path)
    s1 = "DETAILS OF THE COMPANY"
    s2 = "SUPPLY CHARACTERISTICS AND EARTHING ARRANGEMENTS"
    s3 = "PARTICULARS OF INSTALLATION"
    for i in range(doc.page_count):
        text = doc.load_page(i).get_text("text")
        if s1 in text and s2 in text and s3 in text:
            target_page_index = i
            break
    return target_page_index