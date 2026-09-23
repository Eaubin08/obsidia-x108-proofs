args = argv();
if numel(args) < 2
  error("Usage: run_ut_dfmc_window.m <window_id> <param_file>");
endif

window_id = args{1};
param_file = args{2};
addpath(genpath(getenv("FGI_GSRX_ROOT")), "-end");
addpath(genpath(getenv("FGI_GSRX_SHIMS")), "-begin");

log_dir = "/work/hackathons/nativebuilder-gps-defense/fgi_gsrx_runtime/logs";
result_dir = "/work/hackathons/nativebuilder-gps-defense/fgi_gsrx_runtime/results";
mkdir(log_dir);
mkdir(result_dir);

report = struct();
report.window_id = window_id;
report.param_file = param_file;
report.octave_version = version();
report.status = "STARTED";
report.gsrx_resolution = which("gsrx");

try
  settings = readSettings(param_file);
  report.parameters_loaded = true;
  report.ms_to_process = settings.sys.msToProcess;
  report.ms_to_skip = settings.sys.msToSkip;
  report.pct_enabled = settings.sys.PCTenabled;
  report.parallel_channel_tracking = settings.sys.parallelChannelTracking;
  report.rf_file = settings.gpsl1.rfFileName;
  report.data_type = settings.gpsl1.dataType;
  report.output_mat = settings.sys.dataFileOut;
  [out_parent, ~, ~] = fileparts(settings.sys.dataFileOut);
  mkdir(out_parent);

  tic;
  gsrx(param_file);
  report.elapsed_seconds = toc;
  report.status = "GSRX_COMPLETED";
  if exist(settings.sys.dataFileOut, "file")
    report.output_mat_exists = true;
    info = dir(settings.sys.dataFileOut);
    report.output_mat_bytes = info.bytes;
  else
    report.output_mat_exists = false;
  endif
catch err
  report.status = "GSRX_FAILED";
  report.error_identifier = err.identifier;
  report.error_message = err.message;
  if isfield(err, "stack")
    report.error_stack = err.stack;
  endif
end_try_catch

fid = fopen(fullfile(result_dir, strcat("window_", window_id, "_result.json")), "w");
fprintf(fid, "%s\n", jsonencode(report));
fclose(fid);
disp(report.status);
if isfield(report, "error_message")
  disp(report.error_message);
endif

if strcmp(report.status, "GSRX_FAILED")
  exit(2);
endif
