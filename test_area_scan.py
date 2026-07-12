from area_scan import scan_area

results = scan_area(
    18.5204,
    73.8567
)

print(
    "Total Points:",
    len(results)
)

best = max(
    results,
    key=lambda x: x["wind"]
)

print("\nBest Point:")
print(best)