import { scrape } from './scraper.js'

let sessionToken = null;
let reloadToken = null;


chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'SESSION_TOKEN') {
        sessionToken = message.sessionToken;
        reloadToken = message.reloadToken;
        console.log("token received", sessionToken, reloadToken);

        scrape(sessionToken, reloadToken).then(sections => {console.log('total:', sections.size)})
    }    
})