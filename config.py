PLACE_NAME = "Jeżyce, Poznań, Poland"
GRID_SIZE = 450


MONDAY_PROFILE = [
    28.44, 24.69, 24.04, 23.08, 22.5, 21.96, 22.32, 25.27, 28.61, 26.98,
    27.41, 26.78, 30.68, 28.69, 31.62, 28.23, 28.42, 32.76, 38.14, 40.36,
    38.14, 40.18, 35.66, 35.66
]

TUESDAY_PROFILE = [
    32.85, 30.7, 30.55, 31.61, 31.81, 29.2, 30.45, 32.91, 32.59, 33.46,
    33.25, 33.14, 31.18, 29.12, 27.94, 25.09, 28.01, 28.6, 34.02, 39.94,
    43.78, 45.77, 51.22, 47.21
]

HOURLY_TRAFFIC = [
    0.05, 0.05, 0.05, 0.05, 0.1, 0.3, # Noc (00-05)
    0.6, 1.0, 0.9, 0.8, 0.7, 0.7,     # Rano (06-11)
    0.8, 0.8, 0.9, 1.0, 0.9, 0.8,     # Popołudnie (12-17)
    0.7, 0.6, 0.5, 0.4, 0.2, 0.1      # Wieczór (18-23)
]


EMISSION_BASE = {
    'motorway': 25, 'trunk': 20,
    'primary': 18, 'primary_link': 15,
    'secondary': 14, 'secondary_link': 14,
    'tertiary': 8,
    'residential': 4, 'living_street': 2, 'service': 1
}

# Scalar zwiększony, aby 70% od aut było wyraźne w godzinach szczytu
TRAFFIC_EMISSION_SCALAR = 60.0
RATIO_BACKGROUND = 0.30
RATIO_TRAFFIC = 0.70

STEPS_PER_DAY = 288
DIFFUSION_RATE = 0.05
DECAY_RATE = 0.012