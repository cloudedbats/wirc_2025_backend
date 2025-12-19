var previewFps = 1;

function previewModeOnChange() {
  let selectedValue =
    byId('previewModeId').options[byId('previewModeId').selectedIndex].value;
  if (selectedValue == 'preview_on') {
    previewFps = 100
    refreshPreviewStream()
  }
  else if (selectedValue == 'preview_off') {
    previewFps = 0
    refreshPreviewStream()
  }
  else if (selectedValue == 'preview_10_fps') {
    previewFps = 10
    refreshPreviewStream()
  }
  else if (selectedValue == 'preview_5_fps') {
    previewFps = 5
    refreshPreviewStream()
  }
  else if (selectedValue == 'preview_2_fps') {
    previewFps = 2
    refreshPreviewStream()
  }
  else if (selectedValue == 'preview_1_fps') {
    previewFps = 1
    refreshPreviewStream()
  } else {
    alert("Invalid value for previewModeOnChange: " + selectedValue + ".")
  }

}

function refreshPreviewStream() {
  let image = byId('mjpegStreamId');
  image.src = 'preview/stream.mjpeg' + '?rpi_camera=' + selectedRPiCamera;
  image.src += '&fps=' + previewFps;
  image.src += '&dummy=' + Math.random(); // To avoid cache.
  byId('cameraTitleId').textContent = selectedRPiCameraName;
}

