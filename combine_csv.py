import pandas as pd
import os

csv_files_path = "./city_csv_data"

file_list = []

# change to 2020/2021 dependednt on which ones merged
# could change to have it do for both depending... dont judge done quick pls
for file in os.listdir(csv_files_path):
    if file[-8:] == "2021.csv":
        file_list.append(pd.read_csv(csv_files_path + '/' + file))

merged = pd.concat(file_list, ignore_index=True)

# alter name for year
merged.to_csv('city_data-2021.csv', index=False)
