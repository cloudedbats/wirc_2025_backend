var selectedCameraId = 'camera-a';
var selectedCameraName = 'Camera-A';
var cameraStatusAll = {
  'camera-a': { 'camera_mode': 'camera-off' },
  'camera-b': { 'camera_mode': 'camera-off' },
  'camera-c': { 'camera_mode': 'camera-off' },
  'camera-d': { 'camera_mode': 'camera-off' },
  'camera-e': { 'camera_mode': 'camera-off' },
}

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

  cameraStatusAllUpdate()
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

function cameraStatusAllUpdate(cameraStatusAllJson = '') {
  if (cameraStatusAllJson != '') {
    cameraStatusAll = cameraStatusAllJson;
  }

  if (selectedCameraId in cameraStatusAll === true) {
    let mode = cameraStatusAll[selectedCameraId];
    // alert(JSON.stringify(cameraStatusAll))
    if ('camera_mode' in mode === true) {
      byId('cameraModeId').value = mode['camera_mode'];

      if (mode === 'record-on-trigger') {
        byId('buttonTriggerId').hidden = false;
      } else {
        byId('buttonTriggerId').hidden = true;
      }
    }
  }
}

function recordTriggerClicked() {
  activateRecordTrigger(selectedCameraId);
}

function cameraSettingsOnChange() {

}

function cameraSettingsUpdate() {

}

function exposureTimeOnChange() {
  let selectedValue =
    byId('exposureTimeId').options[byId('exposureTimeId').selectedIndex].value
  setExposureTime(selectedCameraId, selectedValue)
}

function cameraGainOnChange() {
  let selectedValue =
    byId('cameraGainId').options[byId('cameraGainId').selectedIndex].value
  setCameraGain(selectedCameraId, selectedValue)
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

function updateCameraGain(cam0CameraGain, cam1CameraGain) {
  let cameraGain = ''
  if (selectedCameraId == 'camera-a') {
    cameraGain = cam0CameraGain
  }
  else if (selectedCameraId == 'camera-b') {
    cameraGain = cam1CameraGain
  }
  if (cameraGain == 0) {
    byId('cameraGainId').value = 'auto'
  } else {
    byId('cameraGainId').value = cameraGain
  }
}
