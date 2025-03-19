import logging
from src.etl.extract import generate_csv
from src.etl.load_data import write_db,write_excel,write_big_query
from src.etl.transform import filter_clean
from src.reportGeneration.report_generator import create_report, split_tables_report
from src.reportGeneration.send_email import send_mail

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def main():
    generate_csv()
    data = filter_clean()
    logger.info("Cleaned and staged data")
    # write_db(data)
    write_big_query(data)
    logger.info("Updated database")
    write_excel(data)
    logger.info("Excel file generated")
    frames = []
    for frame in split_tables_report(data):
        frames.append(frame)
    create_report(frames)
    logger.info("PDF report generated")
    # send_mail()
    logger.info("E-mail sent")

if __name__ == "__main__":
    main()
