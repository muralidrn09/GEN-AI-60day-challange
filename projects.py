import csv
import random

import faker

# Initialize Faker for generating fake data
fake = faker.Faker()

# Define CSV filename
filename = "sample_records.csv"

# Define field names
fields = ["ID", "Name", "Age", "Country", "Salary"]

# Generate 100 random records
records = []
for i in range(1, 101):
    record = {
        "ID": i,
        "Name": fake.name(),
        "Age": random.randint(22, 60),
        "Country": fake.country(),
        "Salary": round(random.uniform(30000, 120000), 2),
    }
    records.append(record)

# Write records to CSV
with open(filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()
    writer.writerows(records)

print(f"✅ Successfully written {len(records)} records to '{filename}'")
