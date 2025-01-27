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

function previewToggleSettings () {
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

function captureImageClicked () {
  captureImage()
}

function videoSingleClicked () {
  videoSingle()
}

function startVideoClicked () {
  startVideo()
}

function stopVideoClicked () {
  stopVideo()
}

function showStatusClicked () {
  showStatus()
}

function setDetectorTimeClicked () {
  setDetectorTime()
}

function exposureTimeOnChange () {
  let selectedValue =
    byId('exposureTimeId').options[byId('exposureTimeId').selectedIndex].value
  setExposureTime(selectedValue)
}

// Functions used to updates fields based on response contents.
function updateStatus (status) {
  byId('detectorTimeId').innerHTML = status.detectorTime
}

function updateLogTable (logRows) {
  htmlTableRows = ''
  for (rowIndex in logRows) {
    htmlTableRows += '<tr><td>'
    htmlTableRows += logRows[rowIndex]
    htmlTableRows += '</tr></td>'
  }
  byId('previewLogTableId').innerHTML = htmlTableRows
}
