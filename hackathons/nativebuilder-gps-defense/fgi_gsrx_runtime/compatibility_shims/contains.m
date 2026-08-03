function tf = contains(str, pattern)
% OCTAVE_COMPAT_SHIM: minimal MATLAB contains() compatibility for FGI-GSRx.
% Uses strfind only; no GNSS algorithm is changed.
  if iscell(str)
    tf = cellfun(@(item) local_contains_one(item, pattern), str);
  else
    tf = local_contains_one(str, pattern);
  endif
endfunction

function tf = local_contains_one(item, pattern)
  if iscell(pattern)
    tf = any(cellfun(@(pat) !isempty(strfind(item, pat)), pattern));
  else
    tf = !isempty(strfind(item, pattern));
  endif
endfunction
