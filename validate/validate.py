import argparse
import pandas as pd
import re

def normalize_address(address):
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

def compare_data(parcelFile, masterFile):
    parcelData = pd.read_csv(parcelFile)
    masterData = pd.read_csv(masterFile)

    parcelData['Normalized Address'] = parcelData['Property Address'].apply(normalize_address)
    masterData['Normalized Address'] = masterData['Lake Address'].apply(normalize_address)

    matching_entries = parcelData[parcelData['Normalized Address'].isin(masterData['Normalized Address'])]
    not_matching_entries = parcelData[~parcelData['Normalized Address'].isin(masterData['Normalized Address'])]

    if not matching_entries.empty:
        print("Matching entries found:")
        print(matching_entries)
    else:
        print("No matching entries found.")

    matching_entries.to_csv('matching_entries.csv', index=False)
    not_matching_entries.to_csv('not_matching_entries.csv', index=False)

def main():
    parser = argparse.ArgumentParser(description="Compare PLA membership information from two CSV files.")
    parser.add_argument("parcel", help="Path to the parcel-based CSV file")
    parser.add_argument("master", help="Path to the master member CSV file")

    args = parser.parse_args()
    compare_data(args.parcel, args.master)

if __name__ == "__main__":
    main()