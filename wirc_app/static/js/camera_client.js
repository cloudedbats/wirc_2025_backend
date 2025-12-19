async function cameraCommand(cameraId, command) {
    fetch("/camera/command?" + new URLSearchParams({
        selectedCamera: selectedCamera,
        command: command,
    }), { method: "POST" })
        .then(function (response) {
            if (response.ok) {
                return response.json();
            } else {
                return Promise.reject(response);
            }
        })
        .then(function (json) {
            if (json.command == "createAndDownloadReport") {
                reportSrc = "/administration/downloads/report?";
                reportSrc += "sourceId=";
                reportSrc += json.sourceId;
                reportSrc += "&nightId=";
                reportSrc += json.nightId;
                // Create temporary element.
                let hidden_a = document.createElement('a');
                hidden_a.setAttribute('href', reportSrc);
                hidden_a.setAttribute('download', json.report_name);
                document.body.appendChild(hidden_a);
                hidden_a.click();
                document.body.removeChild(hidden_a);
            }
        })
        .catch(function (err) {
            console.warn("Error in javascript fetch: ", err);
        })
};



async function cameraOn(selectedRPiCamera) {
  try {
    let urlString = '/cameras/camera-on/' + '?rpi_camera=' + selectedRPiCamera
    let params = {}
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR startVideo: ' + err)
    console.log(err)
  }
}

async function cameraOff(selectedRPiCamera) {
  try {
    let urlString = '/cameras/camera-off/' + '?rpi_camera=' + selectedRPiCamera
    let params = {}
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR startVideo: ' + err)
    console.log(err)
  }
}

async function cameraRecordOn(selectedRPiCamera) {
  try {
    let urlString = '/cameras/record-on/' + '?rpi_camera=' + selectedRPiCamera
    let params = {}
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR startVideo: ' + err)
    console.log(err)
  }
}

async function cameraRecordOff(selectedRPiCamera) {
  try {
    let urlString = '/cameras/record-off/' + '?rpi_camera=' + selectedRPiCamera
    let params = {}
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR startVideo: ' + err)
    console.log(err)
  }
}

async function recordTrigger(selectedRPiCamera) {
  try {
    let urlString = '/cameras/record-trigger/' + '?rpi_camera=' + selectedRPiCamera
    let params = {}
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR startVideo: ' + err)
    console.log(err)
  }
}

async function setExposureTime(exposureTimeMicroSec) {
  if (exposureTimeMicroSec == 'auto') {
    exposureTimeMicroSec = 0;
  }
  try {
    let urlString =
      'cameras/exposure-time?time_us=' + parseInt(exposureTimeMicroSec) + '&rpi_camera=' + selectedRPiCamera
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

async function setAnalogueGain(analogueGain) {
  if (analogueGain == 'auto') {
    analogueGain = 0
  }
  try {
    let urlString =
      'cameras/analogue-gain?analogue_gain=' + parseInt(analogueGain) + '&rpi_camera=' + selectedRPiCamera
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
