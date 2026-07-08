import csv
import io

fieldnames = ["A", "B"]
f = io.StringIO()
writer = csv.DictWriter(f, fieldnames=fieldnames)
writer.writeheader()
try:
    writer.writerow({"A": 1, "B": 2, "Seed": 3})
except Exception as e:
    print(f"Exception: {e}")
print(f.getvalue())
