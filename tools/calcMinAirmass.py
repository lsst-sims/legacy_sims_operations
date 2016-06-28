import numpy as np
import matplotlib.pyplot as plt

tele_lat = -29.666667

dec_min = np.max([tele_lat-90, -90])
dec_max = np.min([tele_lat+90, 90])
field_dec = np.arange(dec_min, dec_max, 0.25)

min_z = np.radians(np.abs(field_dec - tele_lat))
min_airmass = 1 / np.cos(min_z)

# Add expected airmass for +/- 1 & 2 hours around meridian
# cos z  =cos(min_z) * cos(ha_offset)
ha_offset = np.radians(15)
plus_1hr = np.arccos(np.cos(min_z) * np.cos(ha_offset))
ha_offset = np.radians(30)
plus_2hr = np.arccos(np.cos(min_z) * np.cos(ha_offset))

airmass_1hr = 1. / np.cos(plus_1hr)
airmass_2hr = 1. / np.cos(plus_2hr)

plt.plot(field_dec, min_airmass, 'k-', label='zenith')
plt.plot(field_dec, airmass_1hr, 'r:', label='+1hr')
plt.plot(field_dec, airmass_2hr, 'g:', label='+2hr')
plt.legend(loc='upper right', fancybox=True, fontsize='small')
plt.xlabel('Field Dec')
plt.ylabel('Min airmass')
plt.ylim(1, 3)
plt.grid(True)


plt.show()

