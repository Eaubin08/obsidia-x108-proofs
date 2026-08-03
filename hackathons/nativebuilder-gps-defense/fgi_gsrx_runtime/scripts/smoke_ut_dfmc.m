addpath(genpath(getenv("FGI_GSRX_ROOT")), "-end");
addpath(genpath(getenv("FGI_GSRX_SHIMS")), "-begin");

param_file = "/opt/fgi-gsrx-runtime/compatibility_shims/default_param_FGI_UT_DFMC_GPSL1_headless.txt";
run_dir = "/work/hackathons/nativebuilder-gps-defense/fgi_gsrx_runtime/runs/smoke_pre60";
log_dir = "/work/hackathons/nativebuilder-gps-defense/fgi_gsrx_runtime/logs";
mkdir(run_dir);
mkdir(log_dir);

report = struct();
report.status = "STARTED";
report.param_file = param_file;
report.octave_version = version();
report.fgi_root = getenv("FGI_GSRX_ROOT");
report.gsrx_resolution = which("gsrx");

try
  settings = readSettings(param_file);
  report.parameters_loaded = true;
  report.enabled_signals = settings.sys.enabledSignals;
  report.ms_to_process = settings.sys.msToProcess;
  report.pct_enabled = settings.sys.PCTenabled;
  report.parallel_channel_tracking = settings.sys.parallelChannelTracking;
  report.plot_spectra = settings.sys.plotSpectra;
  report.plot_acquisition = settings.sys.plotAcquisition;
  report.plot_tracking = settings.sys.plotTracking;

  rf_file = settings.gpsl1.rfFileName;
  info = dir(rf_file);
  if isempty(info)
    error("RF file not found: %s", rf_file);
  endif
  report.rf_file = rf_file;
  report.rf_size_bytes = info.bytes;
  report.sample_size_bits = settings.gpsl1.sampleSize;
  report.complex_data = settings.gpsl1.complexData;
  report.iq_swap = settings.gpsl1.iqSwap;
  report.data_type = settings.gpsl1.dataType;
  report.samples_total = info.bytes / (settings.gpsl1.sampleSize / 8);

  fid = fopen(rf_file, "r");
  if fid < 0
    error("Unable to open RF file: %s", rf_file);
  endif
  sample_probe = readRfData(fid, settings.gpsl1.dataType, settings.gpsl1.complexData, settings.gpsl1.iqSwap, 0, 26000);
  fclose(fid);
  report.sample_probe_count = numel(sample_probe);
  report.sample_probe_min = min(sample_probe);
  report.sample_probe_max = max(sample_probe);
  report.sample_probe_mean = mean(sample_probe);

  acqData = doAcquisition(settings);
  report.acquisition_attempted = true;
  report.acquisition_fields = fieldnames(acqData.gpsl1);
  report.status = "SMOKE_ACQUISITION_COMPLETED";
  save("-mat7-binary", fullfile(run_dir, "smoke_acqData.mat"), "settings", "acqData", "report");
catch err
  report.status = "SMOKE_FAILED";
  report.error_identifier = err.identifier;
  report.error_message = err.message;
  if isfield(err, "stack")
    report.error_stack = err.stack;
  endif
end_try_catch

fid = fopen(fullfile(log_dir, "smoke_ut_dfmc_result.json"), "w");
if fid < 0
  error("Unable to write smoke result JSON");
endif
fprintf(fid, "%s\n", jsonencode(report));
fclose(fid);
disp(report.status);
if isfield(report, "error_message")
  disp(report.error_message);
endif

if strcmp(report.status, "SMOKE_FAILED")
  exit(2);
endif
