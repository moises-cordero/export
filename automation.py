from time import sleep
import html_tables
import spreadsheet
import pdf_generator


if __name__ == '__main__':
    option = 0
    while option not in ["1", "2"]:
        print("\nChoose an option:")
        print("1. Export to the spreadsheet")
        print("2. Create the final document")
        option = input("\nOption: ")
        print()
        if option == "1":
            tabs, data = html_tables.extract_data()
            spreadsheet.populate_data(tabs, data)
        elif option == "2":
            data = spreadsheet.read()
            pdf_generator.create(data)
        else:
            print("\nInvalid option")
            sleep(1)
