var previewFps = 1;

function previewModeOnChange() {
  let selectedMode =
    byId('previewModeId').options[byId('previewModeId').selectedIndex].value;
  if (selectedMode == 'preview_on') {
    previewFps = 30 // Run on max speed.
    refreshPreviewStream()
  }
  else if (selectedMode == 'preview_off') {
    previewFps = 0
    refreshPreviewStream()
  }
  else if (selectedMode == 'preview_10_fps') {
    previewFps = 10
    refreshPreviewStream()
  }
  else if (selectedMode == 'preview_5_fps') {
    previewFps = 5
    refreshPreviewStream()
  }
  else if (selectedMode == 'preview_2_fps') {
    previewFps = 2
    refreshPreviewStream()
  }
  else if (selectedMode == 'preview_1_fps') {
    previewFps = 1
    refreshPreviewStream()
  } else {
    alert("Invalid value for previewModeOnChange: " + selectedMode + ".")
  }
}

function refreshPreviewStream() {
  let image = byId('mjpegStreamId');
  image.src = 'preview/stream.mjpeg' + '?rpi_camera=' + selectedCameraId;
  image.src += '&fps=' + previewFps;
  image.src += '&dummy=' + Math.random(); // To avoid cache.
  byId('cameraTitleId').textContent = selectedCameraName;
}

