import argparse
from pathlib import Path

import pandas as pd
import re

PROPERTY_COLUMN_NAME = 'Normalized Property Address'
MAILING_COLUMN_NAME = 'Normalized Mailing Address'
NAME_COLUMN_NAME = 'Normalized Name'

# Normalizes an address by converting it to lowercase and converting common street suffixes to their full names.
def normalize_address(address: str) -> str:
    address = str(address).strip().lower()
    address = re.sub(r'\b(st|street)\b', 'street', address)
    address = re.sub(r'\b(rd|road)\b', 'road', address)
    address = re.sub(r'\b(ave|avenue)\b', 'avenue', address)
    address = re.sub(r'\b(blvd|boulevard)\b', 'boulevard', address)
    address = re.sub(r'\b(dr|drive)\b', 'drive', address)
    address = re.sub(r'\b(ln|lane)\b', 'lane', address)
    address = re.sub(r'\b(ct|court)\b', 'court', address)
    address = re.sub(r'[^\w\s]', '', address)  # Remove punctuation
    return address

# Normalizes a single column that contains a name in the format "Last, First {Middle}" into "First Last"
def normalize_single_column_name(name: str) -> str:
    parts = str(name).split(',')
    last_name = parts[0].strip().lower()
    first_name = parts[1].strip().lower() if len(parts) > 1 else ''
    return f"{first_name} {last_name}"

# Normalizes two columns that contain first and last names into "First Last"
def normalize_dual_column_name(first_name: str, last_name: str) -> str:
    return f"{str(first_name).strip().lower()} {str(last_name).strip().lower()}"

# Compares two CSV files and outputs a CSV file with the entries that are in the parcel file but not in the master file.
def compare_data(parcelFile: Path, masterFile: Path):
    parcel_data = pd.read_csv(parcelFile)
    master_data = pd.read_csv(masterFile)

    # First, normalize the addresses and names in both data sets.
    property_column_name = 'Normalized Property Address'
    mailing_column_name = 'Normalized Mailing Address'
    name_column_name = 'Normalized Name'

    parcel_data[property_column_name] = parcel_data['Property Address'].apply(normalize_address)
    master_data[property_column_name] = master_data['Lake Address'].apply(normalize_address)
    parcel_data[name_column_name] = parcel_data['Owner Name'].apply(normalize_single_column_name)
    master_data[name_column_name] = master_data.apply(lambda row: normalize_dual_column_name(row['First Name'], row['Last Name']), axis=1)
    parcel_data[mailing_column_name] = parcel_data['Owner Address'].apply(normalize_address)
    master_data[mailing_column_name] = master_data['Mailing Address'].apply(normalize_address)

    # Next, find entries between the two data sets matching by property address, identifying entries that are in the
    # parcel data but not in the master data.
    matching_entries_by_property_addr = parcel_data[parcel_data[property_column_name].isin(master_data[property_column_name])]

    # Dump entries that didn't match by parcel address to a CSV file.
    entries_not_in_master = parcel_data[~parcel_data[property_column_name].isin(master_data[property_column_name])]
    sanitize_and_output_to_csv(entries_not_in_master, 'entries_with_parcel_address_not_in_master.csv')

    # Next, find entries between the two data sets matching by mailing address.
    matching_entries_by_mailing_addr = matching_entries_by_property_addr[matching_entries_by_property_addr[mailing_column_name].isin(master_data[mailing_column_name])]

    # Dump entries that didn't match by name to a CSV file.
    entries_not_matching_mailing_addr = matching_entries_by_property_addr[~matching_entries_by_property_addr[mailing_column_name].isin(master_data[mailing_column_name])]
    sanitize_and_output_to_csv(entries_not_matching_mailing_addr, 'entries_with_mailing_addr_not_matching_master.csv')

# Sanitize the data of the temporary normalization columns and output to a CSV file.
def sanitize_and_output_to_csv(data: pd.DataFrame, output_file: Path):
    output_data = data.drop(columns=[PROPERTY_COLUMN_NAME, MAILING_COLUMN_NAME, NAME_COLUMN_NAME])
    output_data = output_data.to_csv(output_file, index=False)

def main():
    parser = argparse.ArgumentParser(description="Compare PLA membership information from two CSV files.")
    parser.add_argument("parcel", help="Path to the parcel-based CSV file")
    parser.add_argument("master", help="Path to the master member CSV file")

    args = parser.parse_args()
    compare_data(args.parcel, args.master)

if __name__ == "__main__":
    main()