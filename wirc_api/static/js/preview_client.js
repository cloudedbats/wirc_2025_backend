async function setExposureTime (exposureTimeMicroSec) {
  if (exposureTimeMicroSec == 'auto') {
    exposureTimeMicroSec = 0
  }
  try {
    let urlString =
      'cameras/exposure-time?time_us=' + parseInt(exposureTimeMicroSec)
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

async function captureImage () {
  try {
    let urlString = '/cameras/save-jpeg/'
    let params = {}
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR captureImage: ' + err)
    console.log(err)
  }
}

async function videoSingle () {
  try {
    let urlString = '/cameras/record-video/'
    let params = {}
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR videoSingle: ' + err)
    console.log(err)
  }
}

async function startVideo () {
  try {
    let urlString = '/cameras/start-video/'
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

async function stopVideo () {
  try {
    let urlString = '/cameras/stop-video/'
    let params = {}
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR stopVideo: ' + err)
    console.log(err)
  }
}

async function setDetectorTime () {
  try {
    let posixTimeMs = new Date().getTime()
    // let urlString = "/preview/setTime/?posixtime=" + posixTimeMs;
    let urlString = '/preview/set-time/?posixtime=' + posixTimeMs
    await fetch(urlString)
  } catch (err) {
    alert('ERROR setDetectorTime: ' + err)
    console.log(err)
  }
}

async function previewStatus () {
  try {
    let urlString = '/preview/preview-status/'
    await fetch(urlString)
  } catch (err) {
    alert('ERROR previewStatus: ' + err)
    console.log(err)
  }
}

let waitTextNr = 0

function startWebsocket (wsUrl) {
  // let ws = new WebSocket("ws://localhost:8082/ws");
  let ws = new WebSocket(wsUrl)
  ws.onmessage = function (event) {
    let dataJson = JSON.parse(event.data)
    if ('status' in dataJson === true) {
      updateStatus(dataJson.status)
    }
    if ('logRows' in dataJson === true) {
      updateLogTable(dataJson.logRows)
    }
  }
  ws.onclose = function (event) {
    // Try to reconnect in 5th seconds. Will continue...
    ws = null
    let waitText = 'Disconnected...'
    if (waitTextNr == 0) {
      waitText = 'Disconnected...'
    } else if (waitTextNr == 1) {
      waitText = 'Disconnected.'
    } else if (waitTextNr == 2) {
      waitText = 'Disconnected..'
    }
    waitTextNr += 1
    if (waitTextNr >= 3) {
      waitTextNr = 0
    }

    let statusWhenDisconnected = {
      detectorTime: 'Disconnected',
      locationStatus: waitText
    }
    updateStatus(statusWhenDisconnected)

    setTimeout(function () {
      startWebsocket(wsUrl)
    }, 5000)
  }
  ws.onerror = function (event) {
    // alert("DEBUG: WebSocket error.")
  }
}
