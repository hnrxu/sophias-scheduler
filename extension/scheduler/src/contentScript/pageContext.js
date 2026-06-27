console.log('pageContext running')

const waitForToken = () => {
  const sessionToken = window.workday?.session?.sessionSecureToken

  console.log('checking token in pageContext:', sessionToken)

  if (sessionToken) {
    window.dispatchEvent(new CustomEvent('__schedulerReady', {
      detail: {
        sessionToken,
        reloadToken: new URL(window.location.href).searchParams.get('reloadToken')
      }
    }))
  } else {
    setTimeout(waitForToken, 500)
  }
}

waitForToken()