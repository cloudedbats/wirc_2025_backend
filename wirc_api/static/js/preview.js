var selectedRPiCamera = "cam0";
var selectedRPiCameraName = "Camera-A (cam0)";

// // Used for the main tabs in the settings tile.
// function hideShowSettingsTabs(tabName) {
//     byId("tabSettingsBasicId").classList.remove("is-active");
//     byId("tabSettingsMoreId").classList.remove("is-active");
//     byId("tabSettingsSchedulerId").classList.remove("is-active");
//     hideDivision(byId("divSettingsBasicId"))
//     hideDivision(byId("divSettingsMoreId"))
//     hideDivision(byId("divSettingsSchedulerId"))

//     if (tabName == "basic") {
//         byId("tabSettingsBasicId").classList.add("is-active");
//         showDivision(byId("divSettingsBasicId"))
//     } else if (tabName == "more") {
//         byId("tabSettingsMoreId").classList.add("is-active");
//         showDivision(byId("divSettingsMoreId"))
//     } else if (tabName == "scheduler") {
//         byId("tabSettingsSchedulerId").classList.add("is-active");
//         showDivision(byId("divSettingsSchedulerId"))
//     };
// };

function previewToggleSettings() {
  if (byId('previewSettingsId').classList.contains('is-hidden')) {
    byId('previewBodyId').classList.add('is-hidden')
    byId('previewSettingsId').classList.remove('is-hidden')
    byId('previewSettingsTextId').textContent = 'Hide settings'
  } else {
    byId('previewSettingsId').classList.add('is-hidden')
    byId('previewBodyId').classList.remove('is-hidden')
    byId('previewSettingsTextId').textContent = 'Show settings'
  }
}

function captureImageClicked() {
  captureImage()
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

function rpiCameraSelectOnChange() {
  let selectedValue =
    byId('rpiCameraSelectId').options[byId('rpiCameraSelectId').selectedIndex].value
  let selectedName =
    byId('rpiCameraSelectId').options[byId('rpiCameraSelectId').selectedIndex].text
  // Save to global.
  selectedRPiCamera = selectedValue
  selectedRPiCameraName = selectedName
  refreshPreviewStream()
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
  if (selectedRPiCamera == 'cam0') {
    exposureTime = cam0ExposureTime
  }
  else if (selectedRPiCamera == 'cam1') {
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
  if (selectedRPiCamera == 'cam0') {
    analogueGain = cam0AnalogueGain
  }
  else if (selectedRPiCamera == 'cam1') {
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
