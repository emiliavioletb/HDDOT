
% This function plots the point clouds and lets you manually select the
% cranial landmarks and source locations. 
% This should be done after mesh scaling (I use MeshLab for this).
% EB, March 2025

%% Load data
close all; clear; clc

addpath(genpath('~/Documents/MATLAB/Lumo')); % Add dependencies

datpath = '~/Documents/STUDIES/ONAC/'; % Add data path
addpath(genpath(datpath));

participant=input('Which participant? ', "s");
layout=input('Which layout? ', "s");

ptCloud = pcread([datpath, participant, '/', participant, '_', layout, '_scaled.ply']);
pgPointArray = ptCloud.Location;

%% Manually select sources (CC order) and enter into csv for SD dist calculation
% selection order: nasion, inion, Ar, Al, Cz, Src1A, Src1B, Src1C, Src2A...
fig = figure;
ptCloudMod = pointCloud(pgPointArray,'Color',ptCloud.Color,'Normal',ptCloud.Normal);
pcshow(ptCloudMod); hold on;
set(gcf,'color','black'); % Change to white if easier
set(gca,'color','black'); 
xlabel('X (mm)')
ylabel('Y (mm)')
zlabel('Z (mm)')
numTiles = 6; % Change to number of tiles 
hold off
dcm_obj = datacursormode(fig);
set(dcm_obj,'DisplayStyle','datatip','SnapToDataVertex','off','Enable','on');
numPts = 5 + 3*numTiles; % 5 (landmarks) + 3 * (numTiles)
csvPts = [];
for i = 1:numPts
    disp(['Click line to display data tip ', num2str(i), ' and then press "Enter"'])
    pause
    c_info = getCursorInfo(dcm_obj);
    csvPts = [csvPts ; c_info.Position];
end

filepath = strcat([datpath, participant, '/', participant, '_', layout, ...
    '_scaled_points.csv']);

Location = {'Nasion';'Inion';'Ar';'Al';'Cz'};
numPts = 3*numTiles;
for i = 1:numPts
    if rem(i-1,3) == 0
        srcName = 'A';
    elseif rem(i-1,3) == 1
        srcName = 'B';
    else
        srcName = 'C';
    end
    Location{i+5} = append('Src', num2str(floorDiv(i-1,3)+1), srcName);
end

X = csvPts(:,1);
Y = csvPts(:,2);
Z = csvPts(:,3);

exportTable = table(Location,X,Y,Z);
writetable(exportTable,filepath);

%% Plot the location points and manually check the order is correct 
% e.g. layout = 'frontal', task = 'resting'
plotPhotogrammetry(participant, layout, task)

%% Correct specific points (if necessary) 
points = ['~/Documents/STUDIES/ONAC/all_photogrammetry/', participant,'/', ...
    participant, '_', task, '_scaled_points.csv'];
oldPoints = readtable(points); % Read in the old points 

ptCloud = pcread(['/Users/emilia/Documents/STUDIES/ONAC/all_photogrammetry/', ...
    participant, '/', participant, '_', task, '_scaled.ply']);
pgPointArray = ptCloud.Location;

fig = figure;
ptCloudMod = pointCloud(pgPointArray,'Color',ptCloud.Color,'Normal',ptCloud.Normal);
pcshow(ptCloudMod);
hold on;
set(gcf,'color','black');
set(gca,'color','black');
xlabel('X (mm)')
ylabel('Y (mm)')
zlabel('Z (mm)')
dcm_obj = datacursormode(fig);
set(dcm_obj,'DisplayStyle','datatip','SnapToDataVertex','off','Enable','on');
csvPts = [];

numToFix = 3; % Change to the number of points that need fixing 
for i = 1:numToFix
    disp(['Click line to display data tip ', num2str(i), ' and then press "Enter"'])
    pause
    c_info = getCursorInfo(dcm_obj);
    csvPts = [csvPts ; c_info.Position];
end

disp(['Manually replace relevant old points in "oldPoints" with new points selected in "csvPoints" and ' ...
    'press any key to continue saving'])
pause;

% Over-write .csv 
filepath = strcat('~/Documents/STUDIES/ONAC/all_photogrammetry/', participant, '/', ...
    participant, '_', task, '_scaled_points.csv');
writetable(oldPoints,filepath);

%%
function plotPhotogrammetry(participant, layout, task)
    if exist(['~/Documents/STUDIES/ONAC/all_photogrammetry/', sprintf('/%s', name)], 'dir')
        csv=[]; csv=dir(['~/Documents/STUDIES/ONAC/all_photogrammetry/', sprintf('/%s', name), '/', name, '_', ...
            layout, '*_scaled_points.csv']);
        if ~isempty(csv)
            dat = '~/Documents/STUDIES/ONAC/DATA_FOR_PROCESSING/';
            data=LumoData([dat, '/hddot/', participant, '_', task, '.lufr']);
            nirsFileName = [dat, '/hddot/test_nirsfile'];
            nirs = data.write_NIRS(nirsFileName,'sd_style','flat'); 

            SD3DFileName = [dat, '/hddot/test.SD3D'];
            figure();
            [SD_POL, SD3DFileName] = DOTHUB_LUMOpolhemus2SD3D(['~/Documents/STUDIES/ONAC/all_photogrammetry/', name, '/', csv(1).name],0);
            close all
            load(SD3DFileName, '-mat');
            figure();
            for i = 1:size(SD3D.SrcPos,1)
                plot3(SD3D.SrcPos(i,1),SD3D.SrcPos(i,2),SD3D.SrcPos(i,3),'r.','MarkerSize',30);hold on;
                text(SD3D.SrcPos(i,1),SD3D.SrcPos(i,2)+3,SD3D.SrcPos(i,3),['S' num2str(i)],'Color','r');
            end
            for i = 1:size(SD3D.DetPos,1)
                plot3(SD3D.DetPos(i,1),SD3D.DetPos(i,2),SD3D.DetPos(i,3),'b.','MarkerSize',30);hold on;
                text(SD3D.DetPos(i,1),SD3D.DetPos(i,2)+3,SD3D.DetPos(i,3),['D' num2str(i)],'Color','b');
            end
            nirs.SD3D.Landmarks = SD_POL.Landmarks;
            plotmesh(nirs.SD3D.Landmarks,'g.','MarkerSize', 30);hold on;
            landmarkLabels = {'Nz','Iz','Ar','Al','Cz'};
            for i = 1:size(nirs.SD3D.Landmarks)
                text(nirs.SD3D.Landmarks(i,1),nirs.SD3D.Landmarks(i,2)+3,nirs.SD3D.Landmarks(i,3)+3,landmarkLabels{i});
            end
            axis equal
            titleName = strcat('Optode locations for ', sprintf('%s', name));
            xlabel('X (mm)');ylabel('Y (mm)');zlabel('Z (mm)');
            title(titleName, FontSize=15);drawnow
            fname = strcat('~/Documents/STUDIES/ONAC/preprocessing/Photogrammetry/P', sprintf('%s', name), '_optode_locations.fig');
            hgsave(fname);
            pause;
        end 
    end 
end 
