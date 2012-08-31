% Take in an array of ra/dec pairs, and display using radec_patch_set
function ra_dec_display(filename, fov_deg)
newplot;
fields=load(filename,'-ascii');
ra=fields(:,1);
dec=fields(:,2);
radec_patch_set(ra, dec, fov_deg*pi/180);
axis equal;