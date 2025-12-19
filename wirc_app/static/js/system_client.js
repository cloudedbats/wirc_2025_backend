async function setDetectorTime() {
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
