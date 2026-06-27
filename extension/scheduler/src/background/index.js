import { scrape } from './scraper.js'
import { upsertSections } from './supabase.js';

let sessionToken = null;
let reloadToken = null;


chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
    if (message.type === 'SESSION_TOKEN') {
        sessionToken = message.sessionToken;
        reloadToken = message.reloadToken;
        console.log("token received", sessionToken, reloadToken);
    }
    if (message.type === 'START_SCRAPE') {
        const sections = await scrape(sessionToken, reloadToken)
        console.log('total:', sections.length)
        await upsertSections(sections)
        console.log('data updated')

    }
         
})