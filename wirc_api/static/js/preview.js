var selectedRPiCamera = "camera-a";
var selectedRPiCameraName = "Camera-A";

function setCameraId(cameraId, cameraName) {
  selectedRPiCamera = cameraId;
  selectedRPiCameraName = cameraName;
}

function toggleSettings() {
  if (byId('settingsBasicId').hidden) {
    byId('settingsMoreId').hidden = true;
    byId('settingsBasicId').hidden = false;
    byId("buttonSettingsId").classList.add('is-inverted');
  } else {
    hideSettings()
  }
}

function toggleSettingsMore() {
  if (byId('settingsMoreId').hidden) {
    byId('settingsMoreId').hidden = false;
    byId("buttonSettingsMoreId").classList.add('is-inverted');
  } else {
    hideSettingsMore()
  }
}

function hideSettings() {
  byId('settingsMoreId').hidden = true;
  byId('settingsBasicId').hidden = true;
  byId("buttonSettingsId").classList.remove('is-inverted');
  byId("buttonSettingsMoreId").classList.remove('is-inverted');
}

function hideSettingsMore() {
  byId('settingsMoreId').hidden = true;
  byId("buttonSettingsMoreId").classList.remove('is-inverted');
}

// function aaa() {

// }

// function aaa() {

// }

function cameraModeOnChange() {
  let selectedValue =
    byId('cameraModeId').options[byId('cameraModeId').selectedIndex].value;
  if (selectedValue == 'record') {
    startVideoClicked()
  } else {
    stopVideoClicked()
  }
  if (selectedValue == 'rec_on_trigger') {
    byId('buttonTriggerId').hidden = false;
    // startVideoClicked()
  } else {
    byId('buttonTriggerId').hidden = true;
    // stopVideoClicked()
  }
}

function videoSingleClicked() {
  videoSingle()
}

function startVideoClicked() {
  startVideo()
}

function stopVideoClicked() {
  stopVideo()
}

function showStatusClicked() {
  // showStatus();
  alert('Not implemented...')
}

function setDetectorTimeClicked() {
  // setDetectorTime();
  alert('Not implemented...')
}

function exposureTimeOnChange() {
  let selectedValue =
    byId('exposureTimeId').options[byId('exposureTimeId').selectedIndex].value
  setExposureTime(selectedValue)
}

function analogueGainOnChange() {
  let selectedValue =
    byId('analogueGainId').options[byId('analogueGainId').selectedIndex].value
  setAnalogueGain(selectedValue)
}

function refreshPreviewStream() {
  let image = byId('mjpegStreamId');
  image.src = 'preview/stream.mjpeg' + '?rpi_camera=' + selectedRPiCamera;
  image.src += '&dummy=' + Math.random(); // To avoid cache.
  byId('previewTitleId').textContent = selectedRPiCameraName;
}

// Functions used to updates fields based on response contents.
function updateStatus(status) {
  byId('detectorTimeId').innerHTML = status.detectorTime
}

function updateExposureTime(cam0ExposureTime, cam1ExposureTime) {
  let exposureTime = ""
  if (selectedRPiCamera == 'camera-a') {
    exposureTime = cam0ExposureTime
  }
  else if (selectedRPiCamera == 'camera-b') {
    exposureTime = cam1ExposureTime
  }
  if (exposureTime == 0) {
    byId('exposureTimeId').value = 'auto'
  } else {
    byId('exposureTimeId').value = exposureTime
  }
}

function updateAnalogueGain(cam0AnalogueGain, cam1AnalogueGain) {
  let analogueGain = ""
  if (selectedRPiCamera == 'camera-a') {
    analogueGain = cam0AnalogueGain
  }
  else if (selectedRPiCamera == 'camera-b') {
    analogueGain = cam1AnalogueGain
  }
  if (analogueGain == 0) {
    byId('analogueGainId').value = 'auto'
  } else {
    byId('analogueGainId').value = analogueGain
  }
}

function updateLogTable(logRows) {
  htmlTableRows = ''
  for (rowIndex in logRows) {
    htmlTableRows += '<tr><td>'
    htmlTableRows += logRows[rowIndex]
    htmlTableRows += '</tr></td>'
  }
  byId('previewLogTableId').innerHTML = htmlTableRows
}
