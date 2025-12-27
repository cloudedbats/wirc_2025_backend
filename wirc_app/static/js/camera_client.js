async function setCameraMode(cameraId, cameraMode) {
  try {
    let urlString = '/camera/camera-mode/';
    let params = {
      camera_id: cameraId,
      camera_mode: cameraMode,
    };
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR setCameraMode: ' + err);
    console.log(err);
  }
}

async function activateRecordTrigger(cameraId) {
  try {
    let urlString = '/camera/record-trigger/';
    let params = {
      cameraId: cameraId,
    };
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR activateRecordTrigger: ' + err);
    console.log(err);
  }
}

async function setExposureTime(cameraId, exposureTimeMicroSec) {
  if (exposureTimeMicroSec == 'auto') {
    exposureTimeMicroSec = 0;
  }
  try {
    let urlString =
      '/camera/exposure-time';
    let params = {
      cameraId: cameraId,
      exposureTimeMicroSec: parseInt(exposureTimeMicroSec),
    };
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR setExposureTime: ' + err)
    console.log(err)
  }
}

async function setAnalogueGain(cameraId, analogueGain) {
  if (analogueGain == 'auto') {
    analogueGain = 0;
  }
  try {
    let urlString =
      '/camera/analogue-gain'
    let params = {
      cameraId: cameraId,
      analogueGain: parseInt(analogueGain),
    };
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR setAnalogueGain: ' + err);
    console.log(err);
  }
}
