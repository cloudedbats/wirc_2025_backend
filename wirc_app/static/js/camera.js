var selectedRPiCamera = "camera-a";
var selectedRPiCameraName = "Camera-A";

function setCameraId(cameraId, cameraName) {
  selectedRPiCamera = cameraId;
  selectedRPiCameraName = cameraName;
}

function selectCamera(cameraId, cameraName) {
  setCameraId(cameraId, cameraName)
  byId("selectCamAId").classList.remove('is-inverted');
  byId("selectCamBId").classList.remove('is-inverted');
  byId("selectCamCId").classList.remove('is-inverted');
  byId("selectCamDId").classList.remove('is-inverted');
  if (cameraId == 'camera-a') {
    byId("selectCamAId").classList.add('is-inverted');
  }
  if (cameraId == 'camera-b') {
    byId("selectCamBId").classList.add('is-inverted');
  }
  if (cameraId == 'camera-c') {
    byId("selectCamCId").classList.add('is-inverted');
  }
  if (cameraId == 'camera-d') {
    byId("selectCamDId").disabled = true;
  }

  // TODO: For test.
  byId("selectCamCId").disabled = true;
  byId("selectCamDId").disabled = true;

  refreshPreviewStream()
}

function cameraModeOnChange() {
  let selectedValue =
    byId('cameraModeId').options[byId('cameraModeId').selectedIndex].value;
  if (selectedValue == 'camera_off') {
    byId('buttonTriggerId').hidden = true;
    cameraRecordOff()
    cameraOff()
  }
  else if (selectedValue == 'camera_on') {
    byId('buttonTriggerId').hidden = true;
    cameraRecordOff()
    cameraOn()
  }
  else if (selectedValue == 'record') {
    byId('buttonTriggerId').hidden = true;
    cameraOn()
    cameraRecordOn()
  }
  else if (selectedValue == 'rec_on_trigger') {
    cameraRecordOff()
    cameraOn()
    byId('buttonTriggerId').hidden = false;
  } else {
    alert("Invalid value for cameraModeOnChange: " + selectedValue + ".")
  }
}

function recordTriggerClicked() {
  recordTrigger()
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

// Functions used to updates fields based on response contents.
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
