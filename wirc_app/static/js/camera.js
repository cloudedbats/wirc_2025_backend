var selectedCameraId = 'camera-a';
var selectedCameraName = 'Camera-A';

function setCameraId(cameraId, cameraName) {
  selectedCameraId = cameraId;
  selectedCameraName = cameraName;
}

function selectCamera(cameraId, cameraName) {
  setCameraId(cameraId, cameraName)
  byId('selectCamAId').classList.remove('is-inverted');
  byId('selectCamBId').classList.remove('is-inverted');
  byId('selectCamCId').classList.remove('is-inverted');
  byId('selectCamDId').classList.remove('is-inverted');
  byId('selectCamEId').classList.remove('is-inverted');
  if (cameraId == 'camera-a') {
    byId('selectCamAId').classList.add('is-inverted');
  }
  if (cameraId == 'camera-b') {
    byId('selectCamBId').classList.add('is-inverted');
  }
  if (cameraId == 'camera-c') {
    byId('selectCamCId').classList.add('is-inverted');
  }
  if (cameraId == 'camera-d') {
    byId('selectCamDId').classList.add('is-inverted');
  }
  if (cameraId == 'camera-e') {
    byId('selectCamEId').classList.add('is-inverted');
  }

  // TODO: For test.
  // byId('selectCamCId').disabled = true;
  // byId('selectCamDId').disabled = true;

  byId('cameraTitleId').textContent = selectedCameraName;

  previewModeUpdate();
}

function cameraModeOnChange() {
  let selectedMode =
    byId('cameraModeId').options[byId('cameraModeId').selectedIndex].value;
  if (selectedMode == 'camera-off') {
    byId('buttonTriggerId').hidden = true;
    setCameraMode(selectedCameraId, selectedMode);
  }
  else if (selectedMode == 'camera-on') {
    byId('buttonTriggerId').hidden = true;
    setCameraMode(selectedCameraId, selectedMode);
  }
  else if (selectedMode == 'record-on') {
    byId('buttonTriggerId').hidden = true;
    setCameraMode(selectedCameraId, selectedMode);
  }
  else if (selectedMode == 'record-on-trigger') {
    byId('buttonTriggerId').hidden = false;
    setCameraMode(selectedCameraId, selectedMode);
  } else {
    alert('Invalid value for cameraModeOnChange: ' + selectedMode + '.');
  }
}

function cameraModeUpdate(cameraModeJson) {
  if (selectedCameraId in cameraModeJson === true) {
    let mode = cameraModeJson.selectedCameraId;
    byId('cameraModeId').value = mode;
  }
  if (mode === 'record-on-trigger') {
    byId('buttonTriggerId').hidden = false;
  } else {
    byId('buttonTriggerId').hidden = true;
  }
}

function recordTriggerClicked() {
  activateRecordTrigger(selectedCameraId);
}

function cameraSettingsOnChange() {

}

function cameraSettingsUpdate() {

}







// #################################################

function exposureTimeOnChange() {
  let selectedValue =
    byId('exposureTimeId').options[byId('exposureTimeId').selectedIndex].value
  setExposureTime(selectedCameraId, selectedValue)
}

function analogueGainOnChange() {
  let selectedValue =
    byId('analogueGainId').options[byId('analogueGainId').selectedIndex].value
  setAnalogueGain(selectedCameraId, selectedValue)
}

// Functions used to updates fields based on response contents.
function updateExposureTime(cam0ExposureTime, cam1ExposureTime) {
  let exposureTime = ''
  if (selectedCameraId == 'camera-a') {
    exposureTime = cam0ExposureTime
  }
  else if (selectedCameraId == 'camera-b') {
    exposureTime = cam1ExposureTime
  }
  if (exposureTime == 0) {
    byId('exposureTimeId').value = 'auto'
  } else {
    byId('exposureTimeId').value = exposureTime
  }
}

function updateAnalogueGain(cam0AnalogueGain, cam1AnalogueGain) {
  let analogueGain = ''
  if (selectedCameraId == 'camera-a') {
    analogueGain = cam0AnalogueGain
  }
  else if (selectedCameraId == 'camera-b') {
    analogueGain = cam1AnalogueGain
  }
  if (analogueGain == 0) {
    byId('analogueGainId').value = 'auto'
  } else {
    byId('analogueGainId').value = analogueGain
  }
}
