function radec_patch_set(ra, dec, fov)
n = size(ra);
for i = 1:n(1)
    radec_patch(ra(i), dec(i), fov);
end