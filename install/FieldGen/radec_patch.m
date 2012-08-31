% Display a hexagonal patch at given ra, dec, with diameter fov
% all args are radians
function radec_patch(ra, dec, fov)
theta = 0:pi/3:2*pi;
pmaster = patch(fov/2*sin(theta),fov/2*cos(theta),ones(1,7),'r','Visible','off');
rotate(pmaster,[1,0,0],-180/pi*(pi/2 - dec),[0,0,0]);
rotate(pmaster,[0,0,1],180/pi*ra,[0,0,0]);
set(pmaster,'Visible','on','BackFaceLighting','unlit','FaceLighting','Phong',...
            'AmbientStrength',.3,'DiffuseStrength',.8,...
            'SpecularStrength',.9,'SpecularExponent',25);
