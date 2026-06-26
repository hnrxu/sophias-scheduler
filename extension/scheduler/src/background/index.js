let sessionToken = null;
let reloadToken = null;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'SESSION_TOKEN') {
        sessionToken = message.sessionToken;
        reloadToken = message.reloadToken;
        console.log("token received", sessionToken, reloadToken);
    }    
})