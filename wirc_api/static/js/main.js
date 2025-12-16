// Generic function.
function byId(id) {
  return document.getElementById(id)
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
function hideModules() {
  byId('heroBodyPreviewId').hidden = true;
  byId('heroBodyAboutId').hidden = true;
}

function activateModulePreview() {
  hideModules()
  byId('heroBodyPreviewId').hidden = false;
}

function activateModuleAbout() {
  hideModules()
  byId('heroBodyAboutId').hidden = false;
}

function fetchModulePreview() {
  hideModules()
  fetch('/pages/preview', { method: 'GET' })
    .then(function (response) {
      if (response.ok) {
        return response.text()
      } else {
        return Promise.reject(response)
      }
    })
    .then(function (html) {
      byId('heroBodyPreviewId').innerHTML = html
      activateModulePreview()
    })
    .catch(function (err) {
      console.warn('Error in ModulePreview fetch: ', err)
    })
  // selectCamera(selectedRPiCamera, selectedRPiCameraName)
}

function fetchModuleAbout() {
  hideModules()
  fetch('/pages/about', { method: 'GET' })
    .then(function (response) {
      if (response.ok) {
        return response.text()
      } else {
        return Promise.reject(response)
      }
    })
    .then(function (html) {
      byId('heroBodyAboutId').innerHTML = html
    })
    .catch(function (err) {
      console.warn('Error in ModuleAbout fetch: ', err)
    })
}

// Called from body onLoad.
function fetchModules() {
  setTimeout(fetchAllModules, 500)
}

function fetchAllModules() {
  fetchModulePreview()
  fetchModuleAbout()
  activateModulePreview()
  setTimeout(loadWebsocket, 1000)
}

function loadWebsocket() {
  var ws_url = window.location.protocol === 'https:' ? 'wss://' : 'ws://'
  ws_url += window.location.host // Note: Host includes port.
  ws_url += '/preview/websocket'
  startWebsocket(ws_url)
}
