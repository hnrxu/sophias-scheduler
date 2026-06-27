import './Popup.css'

export const Popup = () => {
    const startScrape = () => {
        chrome.runtime.sendMessage({ type: 'START_SCRAPE' })
    }

    return (
        <div className="container">
            <div className="header">
                <div className="icon-box">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
                    </svg>
                </div>
                <div>
                    <div className="title">Sophia's Scheduler</div>
                    <div className="subtitle">UBC Course Tool</div>
                </div>
            </div>

            <div className="divider" />

            <div className="status">
                <div className="status-dot" />
                <span>Connected to Workday</span>
            </div>

            <button onClick={startScrape}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                Scrape sections
            </button>

            <p className="hint">Scrapes all UBC sections and saves to database. Takes a few minutes.</p>
        </div>
    )
}

export default Popup