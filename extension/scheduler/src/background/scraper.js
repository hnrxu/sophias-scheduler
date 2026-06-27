const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

const fetchWithRetry = async (url, options, retries = 3) => {
    for (let i = 0; i < retries; i++) {
        const response = await fetch(url, options)
        const data = await response.text()

        try {
            return JSON.parse(data) //already returns json 

        } catch (e) {
            console.log(`Request failed, attempt ${i + 1}/${retries}`, data.slice(0, 50))
            await sleep(1000) // try again if not valid json 
        }
    }
}

// gets subject codes before scraping 
const fetchSubjectCodes = async () => {
    const response = await fetch(
        "https://vancouver.calendar.ubc.ca/course-descriptions/courses-subject"
    );

    const html = await response.text();

    const matches = [...html.matchAll(/([A-Z_]+_V)\s+-/g)]
    console.log(matches)

    return [...new Set(matches.map(m => m[1]))];
};


// gets intiial search url w context id & total number of sections
const fetchInitial = async (sessionToken, reloadToken) => {
    const data = await fetchWithRetry(`https://wd10.myworkday.com/ubc/gateway.htmld?reloadToken=${reloadToken}&clientRequestID=${crypto.randomUUID()}`,
        {
            credentials: 'include',
            headers: {
                'session-secure-token': sessionToken,
                'x-workday-client': '2026.24.30'
            }
            
        }
    )

    const searchUri = data.body.endPoints.find(e => e.type === "Search").uri
    const searchUrl = `https://wd10.myworkday.com${searchUri}.htmld`
    const total = data.body.facetContainer.paginationCount.value

    return { searchUrl, total}
}



const searchSubject = async (sessionToken, searchUrl, subjectCode) => {

    const body = new URLSearchParams({
        q: subjectCode,
        sessionSecureToken: sessionToken,
        clientRequestID: crypto.randomUUID()
    })

    const data = await fetchWithRetry(searchUrl, 
        {
            method: 'POST',
            credentials: 'include',
            headers: { 
                        'session-secure-token': sessionToken,
                        'x-workday-client': '2026.24.30', 
                        'content-type': 'application/x-www-form-urlencoded' 
                    },
            body: body.toString()
        }
    )

    const sectionsItem = data.children.find(c => c.widget === 'facetSearchResultList')
    const initialBatch = sectionsItem?.listItems ?? []
    const subjectTotal = data.facetContainer.paginationCount.value

    console.log(`scraped ${initialBatch.length}/${subjectTotal}`)

    const paginationUri = data.endPoints.find(e => e.type === 'Pagination').uri
    const paginationUrl = `https://wd10.myworkday.com${paginationUri}`
    return { initialBatch, subjectTotal, paginationUrl }


}


const paginateSubject = async (sessionToken, paginationUrl, subjectTotal) => {

    const sections = []

    for (let offset = 50; offset < subjectTotal; offset += 50) {
        const data = await fetchWithRetry(`${paginationUrl}/${offset}.htmld?clientRequestID=${crypto.randomUUID()}`,
            {
                credentials: 'include',
                headers: {
                    'session-secure-token': sessionToken,
                    'x-workday-client': '2026.24.30'
                }    
            }
        )
     
        const sectionsItem = data.body.children.find(child => child.widget === 'facetSearchResultList')
        const itemBatch = sectionsItem?.listItems ?? []
        sections.push(...itemBatch)
        
        console.log(`scraped ${sections.length + 50}/${subjectTotal}`)

        await sleep(500) //prevent getting flagged as bot
        
    }

    return sections
}











/// TODO: MAKE INTO MAP INSTEAD OF ARRAY TO AVOID DUPLICATES

export const scrape = async (sessionToken, reloadToken) => {

    const subjectCodes = await fetchSubjectCodes()
    const allSections = new Map()

    const { searchUrl, total} = await fetchInitial(sessionToken, reloadToken)

    for (const subjectCode of subjectCodes) {
        const { initialBatch, subjectTotal, paginationUrl } = await searchSubject(sessionToken, searchUrl, subjectCode)
        const remainingBatch = await paginateSubject(sessionToken, paginationUrl, subjectTotal)
        const subjectSections = [...initialBatch, ...remainingBatch]
        console.log(`${subjectCode} finished: ${subjectSections.length}/${subjectTotal}`)

        for (const section of subjectSections) {
            const id = section.title.instances[0].instanceId
            if (!allSections.has(id)) {
                allSections.set(id, section)
            }
        }
        

    }

    console.log(`Scrape complete. scraped ${allSections.size}/${total}`)
    
    return allSections
}


    





