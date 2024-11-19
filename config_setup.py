import json
import getpass

def main():
    config = {}

    # Prompt for osTicket credentials
    config['username'] = input("Please enter your osTicket username: ")
    config['password'] = getpass.getpass("Please enter your osTicket password: ")

    # Prompt for osTicket base URL
    config['base_url'] = input("Please enter the osTicket base URL (e.g., http://tshoot2.networkinglab.local/scp): ")

    # Prompt for the number of sections
    num_sections = int(input("Enter the number of sections the labs will run during the semester: "))

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    selected_days = []

    print("Select the days for the sections (e.g., 2, 4 for Tuesday and Thursday):")
    for i, day in enumerate(days_of_week, start=1):
        print(f"{i}. {day}")

    while True:
        day_indices = input("Enter the numbers corresponding to the days: ").split(",")
        try:
            selected_days = [days_of_week[int(index.strip()) - 1] for index in day_indices if index.strip().isdigit()]
            if not selected_days:
                raise ValueError("No valid days selected.")
            break
        except (ValueError, IndexError) as e:
            print(f"Invalid input: {e}. Please enter valid numbers corresponding to the days.")

    config["sections"] = {}
    for i, day in enumerate(selected_days, start=1):
        config["sections"][f"Section {i}"] = {"day": day, "subsections": 1}

    print("Do any of these days have multiple sections? (y/n)")
    multiple_sections = input().strip().lower()

    if multiple_sections == 'y':
        while True:
            print("Select the day that has multiple sections:")
            for i, day in enumerate(selected_days, start=1):
                print(f"{i}. {day}")

            try:
                day_index = int(input("Enter the number corresponding to the day: ").strip()) - 1
                selected_day = selected_days[day_index]

                num_subsections = int(input(f"Enter the number of sections for {selected_day}: "))
                for i in range(1, num_subsections + 1):
                    config["sections"][f"Section {len(config['sections']) + 1}"] = {"day": selected_day, "subsections": i}
                break
            except (ValueError, IndexError) as e:
                print(f"Invalid input: {e}. Please enter a valid number corresponding to the day and subsections.")

    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)

    print("Configuration file created successfully!")

if __name__ == "__main__":
    main()