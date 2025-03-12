function dataQuality(fpath, task)

    % This function runs the DOTHUB data quality check which outputs several
    % figures and a .txt file.

    % Load the Lumo data
    addpath(genpath(fpath));
    fprintf('\n INFO: Loading Lumo data \n')
    [pathstr, participant, ~] = fileparts(fpath);

    files=[]; files=dir([fpath,'/hddot/*.lufr']);
    
    for kk=1:length(files)
        if contains(files(kk).name,task)
            data=LumoData([fpath,'/hddot/',files(kk).name]);
            [pathstr,~,~] = fileparts([fpath,'/hddot/',files(kk).name]);
        end
    end

    nirsFileName = strcat(pathstr, '/', participant, '_', task, 'qualityCheck_nirsfile');
    nirs = data.write_NIRS(nirsFileName,'sd_style','flat');
    dod = hmrIntensity2OD(nirs.d);
    nWavs = length(nirs.SD3D.Lambda);
    fs=data.data.chn_fps;
    
    % Clean data
    SD3D = enPruneChannels(nirs.d,nirs.SD3D,fs,ones(size(nirs.t)),[0 1e11],12,[0 100],0); %(d,SD,tInc,dRange,SNRthresh,SDrange,reset) 
    tmp = reshape(SD3D.MeasListAct,[],nWavs);
    tmp2 = ~any(tmp'==0)';
    SD3D.MeasListAct = repmat(tmp2,nWavs,1);
    
    % Run data quality check 
    DOTHUB_dataQualityCheck(nirsFileName);
end