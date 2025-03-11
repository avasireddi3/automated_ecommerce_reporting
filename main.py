from src.extract import generate_csv
from src.load_data import write_db,write_excel
from src.transform import filter_clean, split_tables_report
from src.report_generator import create_report
from src.send_email import send_mail

def main():
    generate_csv()
    data = filter_clean()
    write_db(data)
    write_excel(data)
    frames = []
    for frame in split_tables_report(data):
        frames.append(frame)
    create_report(frames)
    send_mail()

if __name__ == "__main__":
    main()
