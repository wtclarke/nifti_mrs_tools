"""Useful constants for use in mrs_tools functionality"""

# Gyromagnetic ratio in MHz/tesla
# From https://en.wikipedia.org/wiki/Gyromagnetic_ratio
# except for 1H https://physics.nist.gov/cgi-bin/cuu/Value?gammappbar
GYRO_MAG_RATIO = {
    '1H': 42.576,
    '2H': 6.536,
    '13C': 10.7084,
    '31P': 17.235}
