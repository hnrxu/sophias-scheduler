import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
    import.meta.env.VITE_SUPABASE_URL,
    import.meta.env.VITE_SUPABASE_ANON_KEY
)

export const upsertSections = async (sections) => {
    const rows = sections.map(s => ({
        instance_id: s.instanceId,
        course_code: s.courseCode,
        subject: s.subject,
        course_number: s.courseNumber,
        section: s.section,
        title: s.title,
        format: s.format,
        status: s.status,
        delivery: s.delivery,
        credits: s.credits,
        enrolled: s.enrolled,
        capacity: s.capacity,
        has_reserved_seats: s.hasReservedSeats,
        waitlisted: s.waitlisted,
        waitlist_capacity: s.waitlistCapacity,
        notes: s.notes,
        drop_deadline: s.dropDeadline,
        withdrawal_deadline: s.withdrawalDeadline,
        reserved_seats: s.reservedSeats,
        clustered_sections: s.clusteredSections,
        meetings: s.meetings

    }))

    const response = await supabase
                                .from("sections")
                                .upsert(rows, { onConflict: 'instance_id' })
    if (response.error) {
        console.log(response.error)
    }



}