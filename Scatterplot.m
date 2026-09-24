% 1. Load data from CSV (skipping comment header line 1)
opts = detectImportOptions('experiment_data.csv', 'NumHeaderLines', 1);
data = readtable('experiment_data.csv', opts);

% 2. Extract cam_p_m string coordinates and parse into X, Y (meters)
cam_str = data.cam_p_m;
num_rows = height(data);
cam_x = zeros(num_rows, 1);
cam_y = zeros(num_rows, 1);

for i = 1:num_rows
    coords = str2num(strrep(strrep(cam_str{i}, '(', ''), ')', '')); %#ok<ST2NM>
    cam_x(i) = coords(1); % X coordinate in meters
    cam_y(i) = coords(2); % Y coordinate in meters
end

% Extract distance (cm) and angle (degrees)
distance = data.dist_cm; 
angle_deg = data.theta_deg;   

% 3. Classify points based on angle and distance rules
labels = strings(num_rows, 1);

for i = 1:num_rows
    d = distance(i);
    a = angle_deg(i);
    
    if (a >= 40 && a <= 140)
        if (a > 120 || a < 60) && d < 5.0
            labels(i) = 'Circle';
        elseif (a > 100 || a < 80) && d < 5.5
            labels(i) = 'Circle';
        elseif (a >= 80 && a <= 100) && d < 6.0
            labels(i) = 'Circle';
        else
            labels(i) = 'Red_X'; % Outside distance limit
        end
    else
        labels(i) = 'Red_X';     % Outside [40, 140] angle range
    end
end

% 4. Open Figure and Get Axes Handle Explicitly
fig = figure('Name', '2D Scatter Plot', 'NumberTitle', 'off');
clf(fig);
ax = axes('Parent', fig); % Explicitly declare parent axis to prevent Parent Controller warnings
hold(ax, 'on');

% Fixed Square Center and Dimensions (in meters)
FIXED_X = 0.03; 
FIXED_Y = 0.12; 
sq_size_m = 0.095; % 9.5 cm = 0.095 m

% Draw the 9.5 cm x 9.5 cm Square centered at (FIXED_X, FIXED_Y)
sq_left = FIXED_X - (sq_size_m / 2);
sq_bottom = FIXED_Y - (sq_size_m / 2);

rectangle('Parent', ax, 'Position', [sq_left, sq_bottom, sq_size_m, sq_size_m], ...
          'FaceColor', [0.9, 0.9, 0.9, 0.5], ... % Translucent gray fill
          'EdgeColor', 'k', ...
          'LineWidth', 1.5, ...
          'LineStyle', '--');

% Mark Center Pose
h_center = plot(ax, FIXED_X, FIXED_Y, 'k+', 'MarkerSize', 10, 'LineWidth', 1.5, ...
                'DisplayName', 'Center (0.03, 0.12)');

% 5. Sector Setup with Reduced Left Angle
radius_m = 0.1523; % Radius set to touch furthest green point (~15.23 cm)
theta1_deg = 226;  % Left angle boundary
theta2_deg = 312;  % Right angle boundary

% Create arc points
sector_angles = deg2rad(linspace(theta1_deg, theta2_deg, 100));
sector_x = FIXED_X + radius_m * cos(sector_angles);
sector_y = FIXED_Y + radius_m * sin(sector_angles);

% Complete wedge polygon: Center -> Arc -> Center
wedge_x = [FIXED_X, sector_x, FIXED_X];
wedge_y = [FIXED_Y, sector_y, FIXED_Y];

% Fill translucent green sector and draw green border
h_sector = fill(ax, wedge_x, wedge_y, [0.8, 0.95, 0.8], 'EdgeColor', 'g', ...
                'LineWidth', 2, 'FaceAlpha', 0.4, ...
                'DisplayName', sprintf('Adjusted Sector (%d°, r = %.2f cm)', theta2_deg - theta1_deg, radius_m*100));

% 6. Plot Scatter Points
idx_circle = (labels == "Circle");
idx_x = (labels == "Red_X");

h_valid = [];
h_invalid = [];

% Plot Valid points ('o') in green
if any(idx_circle)
    h_valid = scatter(ax, cam_x(idx_circle), cam_y(idx_circle), 60, 'g', 'o', 'LineWidth', 1.5, ...
                      'DisplayName', 'Valid (o)');
end

% Plot Invalid points ('x') in red
if any(idx_x)
    h_invalid = scatter(ax, cam_x(idx_x), cam_y(idx_x), 60, 'r', 'x', 'LineWidth', 1.5, ...
                        'DisplayName', 'Invalid (Red x)');
end

% Plot Formatting
grid(ax, 'on');
axis(ax, 'equal'); 
xlabel(ax, 'X Coordinate (m)');
ylabel(ax, 'Y Coordinate (m)');
title(ax, '2D Scatter Plot with Reduced Left Angle Sector');

% 7. Safe Explicit Legend Call (passes handles directly to avoid ViewModel errors)
handles_to_show = [h_sector, h_valid, h_invalid, h_center];
% Remove any empty handles
handles_to_show = handles_to_show(isgraphics(handles_to_show)); 

legend(ax, handles_to_show, 'Location', 'northeast');

hold(ax, 'off');
drawnow;