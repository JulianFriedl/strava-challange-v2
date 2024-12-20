import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

primary_color = "#5b5ea6"   # Royal Purple
secondary_color = "#9c9ede"   # Lavender Fog
accent_color = "#c3c9e9"    # Accent
background_color = "#f9f9f9"   # Off-white

circle_radius = 0.3
extra_margin = 0.5

x_min, x_max = 3 - extra_margin, 7 + extra_margin
y_min, y_max = 2.2 - extra_margin, 6.6 + extra_margin

fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.set_aspect('equal')
# ax.set_facecolor(background_color)
ax.axis('off')

triangle1 = [(3, 3), (3, 5), (5, 3)]      # Left peak
triangle2 = [(3.5, 3), (5, 5.3), (6.5, 3)]  # Center peak
triangle3 = [(5, 3), (7, 5), (7, 3)]      # Right peak

left_triangle = patches.Polygon(triangle1, closed=True, color=primary_color)
right_triangle = patches.Polygon(triangle3, closed=True, color=primary_color)
center_triangle = patches.Polygon(triangle2, closed=True, color=primary_color)

ax.add_patch(left_triangle)
ax.add_patch(right_triangle)
ax.add_patch(center_triangle)

peak_positions = [(3, 5.5), (5, 6), (7, 5.5)]
for pos in peak_positions:
    peak_circle = patches.Circle(pos, circle_radius, color=accent_color)
    ax.add_patch(peak_circle)

line1 = patches.Rectangle((3, 2.5), 4, 0.2, color=secondary_color)
line2 = patches.Rectangle((3, 2.2), 4, 0.2, color=accent_color)
ax.add_patch(line1)
ax.add_patch(line2)

dpi = 100
pad_inches = 20 / dpi

fig.set_size_inches(512/dpi, 512/dpi)
fig.savefig("logo512.png", dpi=dpi, bbox_inches='tight', pad_inches=pad_inches, transparent=True)

fig.set_size_inches(192/dpi, 192/dpi)
fig.savefig("logo192.png", dpi=dpi, bbox_inches='tight', pad_inches=pad_inches, transparent=True)

fig.set_size_inches(6, 6)  # Size doesn't matter much for SVG
fig.savefig("logo.svg", format='svg', bbox_inches='tight', pad_inches=pad_inches, transparent=True)

img = Image.open("logo512.png")
img.save("favicon.ico", format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
