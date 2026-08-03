args = argv();
if numel(args) < 3
  error("Usage: derive_nav_from_window_mat.m <mat_file> <param_file> <out_json>");
endif

mat_file = args{1};
param_file = args{2};
out_json = args{3};
addpath(genpath(getenv("FGI_GSRX_ROOT")), "-end");
addpath(genpath(getenv("FGI_GSRX_SHIMS")), "-begin");

report = struct();
report.mat_file = mat_file;
report.param_file = param_file;
report.status = "STARTED";
report.octave_version = version();

try
  loaded = load(mat_file);
  settings = readSettings(param_file);
  if isfield(loaded, "settings")
    settings_from_file = loaded.settings;
    settings_from_file.sys = settings.sys;
    settings = settings_from_file;
  endif

  acqData = loaded.acqData;
  trackData = loaded.trackData;
  if isfield(loaded, "ephData")
    ephData = loaded.ephData;
  else
    ephData = [];
  endif

  report.loaded_acqData = true;
  report.loaded_trackData = true;
  report.ms_to_process = settings.sys.msToProcess;
  report.ms_to_skip = settings.sys.msToSkip;

  obsData = generateObservations(trackData, settings);
  [obsData, ephData] = doFrameDecoding(obsData, trackData, settings);
  [obsData, satData, navData] = doNavigation(obsData, settings, ephData);

  report.nav_epochs = numel(navData);
  report.nav_valid_epochs = 0;
  report.status_counts = struct();
  report.first_valid_pvt = struct();
  report.last_valid_pvt = struct();

  for i = 1:numel(navData)
    if isfield(navData{i}, "Pos") && isfield(navData{i}.Pos, "bValid") && navData{i}.Pos.bValid == 1
      report.nav_valid_epochs = report.nav_valid_epochs + 1;
      current = struct();
      current.epoch_index = i;
      current.xyz = navData{i}.Pos.xyz;
      current.lla = navData{i}.Pos.LLA;
      current.dop = navData{i}.Pos.dop;
      current.nr_sats = navData{i}.Pos.nrSats;
      current.fom = navData{i}.Pos.fom;
      if isfield(navData{i}, "Vel")
        current.velocity_xyz = navData{i}.Vel.xyz;
      endif
      if report.nav_valid_epochs == 1
        report.first_valid_pvt = current;
      endif
      report.last_valid_pvt = current;
    endif
  endfor

  if isfield(ephData, "gpsl1")
    report.ephemeris_prns_ok = [];
    eph = ephData.gpsl1;
    names = fieldnames(eph);
    for i = 1:numel(names)
      name = names{i};
      if strncmp(name, "PRN", 3)
        report.ephemeris_prns_ok(end + 1) = str2num(name(4:end));
      endif
    endfor
  endif

  report.status = "NAV_DERIVED";
catch err
  report.status = "NAV_DERIVE_FAILED";
  report.error_identifier = err.identifier;
  report.error_message = err.message;
  if isfield(err, "stack")
    report.error_stack = err.stack;
  endif
end_try_catch

[out_parent, ~, ~] = fileparts(out_json);
mkdir(out_parent);
fid = fopen(out_json, "w");
fprintf(fid, "%s\n", jsonencode(report));
fclose(fid);
disp(report.status);
if strcmp(report.status, "NAV_DERIVE_FAILED")
  exit(2);
endif
