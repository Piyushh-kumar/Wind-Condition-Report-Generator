from grid_generator import generate_grid

points = generate_grid(
    18.5204,
    73.8567
)

print(
    len(points)
)

print(
    points[:5]
)