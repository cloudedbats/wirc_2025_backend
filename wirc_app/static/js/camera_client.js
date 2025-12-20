async function setCameraMode(cameraId, command) {
  try {
    let urlString = '/camera/camera-mode/'
    let params = {
        selectedCamera: cameraId,
        command: command,
    };
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR setCameraMode: ' + err)
    console.log(err)
  }
}

async function activateRecordTrigger(cameraId) {
  try {
    let urlString = '/camera/record-trigger/'
    let params = {
      selectedCamera: cameraId,
    }
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR activateRecordTrigger: ' + err)
    console.log(err)
  }
}

async function setExposureTime(cameraId, exposureTimeMicroSec) {
  if (exposureTimeMicroSec == 'auto') {
    exposureTimeMicroSec = 0;
  }
  try {
    let urlString =
      'camera/exposure-time?time_us=' + parseInt(exposureTimeMicroSec) + '&rpi_camera=' + cameraId
    let params = {}
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
    analogueGain = 0
  }
  try {
    let urlString =
      'camera/analogue-gain?analogue_gain=' + parseInt(analogueGain) + '&rpi_camera=' + cameraId
    let params = {}
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR setAnalogueGain: ' + err)
    console.log(err)
  }
}
