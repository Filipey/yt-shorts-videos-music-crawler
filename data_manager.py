import os
import shutil

countries = [
    ("au", "Australia"),
    ("br", "Brazil"),
    ("ca", "Canada"),
    ("fr", "France"),
    ("de", "Germany"),
    ("in", "India"),
    ("jp", "Japan"),
    ("mx", "Mexico"),
    ("us", "United States"),
    ("kr", "South Korea"),
    ("ae", "United Arab Emirates"),
    ("gb", "United Kingdom"),
]

dataset_directory = "../dataset"

for file_name in os.listdir(dataset_directory):
    file_path = os.path.join(dataset_directory, file_name)

    if os.path.isfile(file_path) and file_name.endswith(".csv"):
        for country_code, country_name in countries:
            if f"-{country_code}-" in file_name:
                destination_path = os.path.join(
                    dataset_directory, country_name, file_name
                )

                shutil.move(file_path, destination_path)
                print(f"File {file_name} moved to {destination_path}")
                break
