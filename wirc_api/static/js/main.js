function byId (id) {
  return document.getElementById(id)
}

// Generic functions.
function hideDivision (divId) {
  if (divId != 'undefined') {
    divId.style.visibility = 'hidden'
    divId.style.overflow = 'hidden'
    divId.style.height = '0'
    divId.style.width = '0'
  }
}

function showDivision (divId) {
  if (divId != 'undefined') {
    divId.style.visibility = null
    divId.style.overflow = null
    divId.style.height = null
    divId.style.width = null
  }
}

function hideModules () {
  byId('modulePreviewId').classList.remove('is-inverted')
  // byId("moduleLiveId").classList.remove("is-inverted");
  // byId("moduleAnnotationsId").classList.remove("is-inverted");
  // byId("moduleAdminId").classList.remove("is-inverted");
  byId('heroBodyPreviewId').classList.add('is-hidden')
  // byId("heroBodyLiveId").classList.add("is-hidden");
  // byId("heroBodyAnnotationsId").classList.add("is-hidden");
  // byId("heroBodyAdminId").classList.add("is-hidden");
  byId('heroBodyAboutId').classList.add('is-hidden')
}

function activateModulePreview () {
  hideModules()
  byId('modulePreviewId').classList.add('is-inverted')
  byId('heroBodyPreviewId').classList.remove('is-hidden')
}

// function activateModuleLive() {
//     hideModules();
//     byId("moduleLiveId").classList.add("is-inverted");
//     byId("heroBodyLiveId").classList.remove("is-hidden");
// };

// function activateModuleAnnotations() {
//     hideModules()
//     byId("moduleAnnotationsId").classList.add("is-inverted");
//     byId("heroBodyAnnotationsId").classList.remove("is-hidden");
// };

// function activateModuleAdministration() {
//     hideModules()
//     byId("moduleAdminId").classList.add("is-inverted");
//     byId("heroBodyAdminId").classList.remove("is-hidden");
// };

function activateModuleAbout () {
  hideModules()
  // byId("moduleAdminId").classList.add("is-inverted");
  byId('heroBodyAboutId').classList.remove('is-hidden')
}

function fetchModulePreview () {
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
      byId('modulePreviewId').classList.remove('is-inverted')

      activateModulePreview()
    })
    .catch(function (err) {
      console.warn('Error in javascript fetch: ', err)
    })
}

function fetchModuleAbout () {
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
      console.warn('Error in javascript fetch: ', err)
    })
}

// Called from body onLoad.
function fetchModules () {
  setTimeout(fetchAllModules, 1000)
  setTimeout(loadWebsocket, 1500)
}

function fetchAllModules () {
  fetchModulePreview()
  // fetchModuleLive();
  // fetchModuleAnnotations();
  // fetchModuleAdministration();
  fetchModuleAbout()

  setTimeout(loadWebsocket, 2000)
}

function loadWebsocket () {
  // audioFeedbackSliders();

  var ws_url = window.location.protocol === 'https:' ? 'wss://' : 'ws://'
  ws_url += window.location.host // Note: Host includes port.
  ws_url += '/preview/websocket'
  startWebsocket(ws_url)
  // alert("Onload done...")
}
