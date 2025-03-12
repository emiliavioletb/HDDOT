function [layout_fname] = LUMO_findLayout(task)

% Assigns relevant layout name given task.
task= string(task);
if (task == 'resting') | (task == 'imt')
    layout_fname='frontal';
elseif task == 'visual'
    layout_fname='visual';
elseif task == 'motor'
    layout_fname='motor';
elseif task == 'mmn'
    layout_fname='auditory';
end
