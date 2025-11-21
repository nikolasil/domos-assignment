from services.processor import EmailProcessor

def main():
    processor = EmailProcessor()
    processor.run_once()

if __name__ == "__main__":
    main()
