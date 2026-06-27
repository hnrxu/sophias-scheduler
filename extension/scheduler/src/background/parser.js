export const parseSection = (item) => {
    // title
    const fullText = item.title.instances[0].text
    const dashIdx = fullText.indexOf(' - ')
    const courseCode = fullText.substring(0, dashIdx) // ex ACAM_V 100 - 001
    const title = fullText.substring(dashIdx + 3) // ex Asian canadian media
    
    const lastDash = courseCode.lastIndexOf('-')
    const subjectAndNumber = courseCode.substring(0, lastDash)  // ex ACAM_V 100
    const section = courseCode.substring(lastDash + 1)           //  ex 001"

    const spaceParts = subjectAndNumber.split(' ')
    const subject = spaceParts[0]        // "ACAM_V"
    const courseNumber = spaceParts[1]   // "100"

    // subtitles/extra info
    const subtitleMap = {}
    for (const s of item.subtitles) {
        subtitleMap[s.label] = s
    }

    // for these instance fields, must check if its actually always only 1 instance
    const format = subtitleMap['Instructional Format']?.instances?.[0]?.text ?? null
    const status = subtitleMap['Section Status']?.instances?.[0]?.text ?? null
    const delivery = subtitleMap['Delivery Mode']?.instances?.[0]?.text ?? null

    const creditsRaw = subtitleMap['zCF - CT - Maximum Credits']?.value ?? null
    const credits = creditsRaw ? parseFloat(creditsRaw) : null

    const enrolledRaw = subtitleMap['zCF - CT - Enrolled/Capacity']?.value ?? null
    let enrolled = null, capacity = null
    if (enrolledRaw) {
        const match = enrolledRaw.match(/Enrolled\/Capacity:\s*(\d+)\/(\d+)/)
        if (match) { enrolled = parseInt(match[1]); capacity = parseInt(match[2]) }
    }

    const hasReservedSeats = 'zCF - EE - Includes Reserved Seats' in subtitleMap

    const waitlistRaw = subtitleMap['zCF - EE - Waitlisted / Waitlist Capacity']?.value ?? null
    let waitlisted = null, waitlistCapacity = null
    if (waitlistRaw) {
        const match = waitlistRaw.match(/Waitlisted\/Waitlist Capacity:\s*(\d+)\/(\d+)/)
        if (match) { waitlisted = parseInt(match[1]); waitlistCapacity = parseInt(match[2]) }
    }

    // detail fields
    const detailMap = {}
    for (const d of item.detailResultFields) {
        detailMap[d.label] = d
    }

    const notes = detailMap['Course Section Definition Public Notes']?.value ?? null

    const deadlinesRaw = detailMap['Drop and Withdrawal Deadlines']?.value ?? null
    let dropDeadline = null, withdrawalDeadline = null
    if (deadlinesRaw) {
        const clean = deadlinesRaw.replace('&#xa;', '\n')
        const dropMatch = clean.match(/Drop:\s*([\d/]+)/)
        const withMatch = clean.match(/Withdrawal:\s*([\d/]+)/)
        if (dropMatch) dropDeadline = dropMatch[1]
        if (withMatch) withdrawalDeadline = withMatch[1]
    }

    const reservedSeats = (detailMap['Reserved Seat Capacity']?.instances ?? [])
        .map(i => i.text)

    const clusteredSections = (detailMap['Clustered Course Sections']?.instances ?? [])
        .map(i => i.instanceId)

    // meetings 
    const meetingInstances = detailMap['Section Details']?.instances ?? []
    const meetings = meetingInstances.map(inst => {
        const parts = inst.text.split(' | ')
        const dateRange = parts.find(p => /\d{4}-\d{2}-\d{2}.*-.*\d{4}-\d{2}-\d{2}/.test(p))
        const timeRange = parts.find(p => /\d+:\d+.*-.*\d+:\d+/.test(p))
        const days = parts.find(p => /^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)/.test(p))
        const floor = parts.find(p => p.startsWith('Floor:'))
        const room = parts.find(p => p.startsWith('Room:'))
        const campus = parts.find(p => p.startsWith('UBC'))
        const building = parts.find(p => /\(([A-Z]+)\)$/.test(p))
        const [startTime, endTime] = timeRange.split(' - ')
        const [startDate, endDate] = dateRange.split(' - ')
        return {
            campus: campus ?? null,
            building: building ?? null,
            floor: floor?.replace('Floor: ', '') ?? null,
            room: room?.replace('Room: ', '') ?? null,
            days: days ?? null,
            startTime, endTime, startDate, endDate
        }
    })

    return {
        courseCode,
        subject,
        courseNumber,
        section,
        title,
        format,
        status,
        delivery,
        credits,
        enrolled,
        capacity,
        hasReservedSeats,
        waitlisted,
        waitlistCapacity,
        notes,
        dropDeadline,
        withdrawalDeadline,
        reservedSeats,
        clusteredSections,
        meetings
    }
}