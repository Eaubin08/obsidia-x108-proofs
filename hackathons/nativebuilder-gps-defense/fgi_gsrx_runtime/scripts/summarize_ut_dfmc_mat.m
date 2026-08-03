args = argv();
if numel(args) < 2
  error("Usage: summarize_ut_dfmc_mat.m <mat_file> <out_json>");
endif

mat_file = args{1};
out_json = args{2};
addpath(genpath(getenv("FGI_GSRX_ROOT")), "-end");
addpath(genpath(getenv("FGI_GSRX_SHIMS")), "-begin");

report = struct();
report.mat_file = mat_file;
report.status = "STARTED";
report.octave_version = version();

try
  vars = whos("-file", mat_file);
  report.variables = {vars.name};
  report.has_acqData = any(strcmp(report.variables, "acqData"));
  report.has_trackData = any(strcmp(report.variables, "trackData"));
  report.has_obsData = any(strcmp(report.variables, "obsData"));
  report.has_ephData = any(strcmp(report.variables, "ephData"));
  report.has_satData = any(strcmp(report.variables, "satData"));
  report.has_navData = any(strcmp(report.variables, "navData"));
  report.has_statResults = any(strcmp(report.variables, "statResults"));

  load(mat_file);

  if exist("acqData", "var") && isfield(acqData, "gpsl1")
    acq = acqData.gpsl1;
    if isfield(acq, "sv")
      report.acquired_prns = acq.sv(find(acq.peakMetric > 0));
    endif
    if isfield(acq, "peakMetric")
      report.acquisition_peak_metric_max = max(acq.peakMetric);
    endif
  endif

  if exist("ephData", "var") && isfield(ephData, "gpsl1")
    eph = ephData.gpsl1;
    report.ephemeris_prns_ok = [];
    fields = fieldnames(eph);
    for i = 1:numel(fields)
      prn_name = fields{i};
      if strncmp(prn_name, "PRN", 3)
        report.ephemeris_prns_ok(end + 1) = str2num(prn_name(4:end));
      endif
    endfor
  endif

  if exist("navData", "var")
    report.nav_epochs = numel(navData);
    valid_count = 0;
    first_valid = struct();
    last_valid = struct();
    for i = 1:numel(navData)
      if isfield(navData{i}, "Pos") && isfield(navData{i}.Pos, "bValid") && navData{i}.Pos.bValid == 1
        valid_count = valid_count + 1;
        current = struct();
        current.epoch_index = i;
        current.xyz = navData{i}.Pos.xyz;
        current.lla = navData{i}.Pos.LLA;
        current.dop = navData{i}.Pos.dop;
        current.nr_sats = navData{i}.Pos.nrSats;
        if isfield(navData{i}, "Vel")
          current.velocity_xyz = navData{i}.Vel.xyz;
        endif
        if valid_count == 1
          first_valid = current;
        endif
        last_valid = current;
      endif
    endfor
    report.nav_valid_epochs = valid_count;
    report.first_valid_pvt = first_valid;
    report.last_valid_pvt = last_valid;
  endif

  if exist("statResults", "var")
    report.stat_hor = statResults.hor;
    report.stat_ver = statResults.ver;
    report.stat_dop = statResults.dop;
    report.stat_rms3d = statResults.RMS3D;
  endif

  report.status = "SUMMARY_COMPLETED";
catch err
  report.status = "SUMMARY_FAILED";
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
if strcmp(report.status, "SUMMARY_FAILED")
  exit(2);
endif
