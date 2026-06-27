console.log('content script running')

window.addEventListener('__schedulerReady', (event) => {
  const { sessionToken, reloadToken } = event.detail

  console.log('token from pageContext:', sessionToken)

  if (sessionToken) {
    chrome.runtime.sendMessage({
      type: 'SESSION_TOKEN',
      sessionToken,
      reloadToken
    })
  }
})

const script = document.createElement('script')
script.src = chrome.runtime.getURL('src/contentScript/pageContext.js')
script.onload = () => script.remove() // attach remove to run only after this script is done
document.documentElement.appendChild(script)