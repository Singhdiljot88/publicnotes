# Editorial data for the two newer series: UPSC 300 and Current Affairs 100.
# Each theme: (slug, name, icon, gs_paper, intro)

UPSC_THEMES = {
    1: ("ancient-india", "Ancient India", "🏺", "GS I", "From the Harappans to the Guptas and the southern kingdoms: the sources, states, religions and ideas that shaped early India."),
    2: ("medieval-india", "Medieval India", "🕌", "GS I", "The Delhi Sultanate, Vijayanagara, the Mughals, the Bhakti and Sufi movements, and the rise of the Marathas and Sikhs."),
    3: ("art-culture", "Art & culture", "🎭", "GS I", "Temple architecture, painting, classical dance and music, literature, festivals and heritage protection, in exam-ready form."),
    4: ("colonial-india", "Colonial India & 1857", "⚓", "GS I", "How the East India Company won power, what colonial rule did to land, trade and education, and why 1857 happened."),
    5: ("freedom-struggle", "The freedom struggle", "🇮🇳", "GS I", "From the Congress of 1885 to Partition in 1947: moderates and extremists, Gandhi's movements, revolutionaries, and the road to independence."),
    6: ("post-independence", "India after 1947", "🧭", "GS I", "Integration of the princely states, linguistic states, planning, wars, the Emergency, and the 1991 reforms."),
    7: ("world-history", "World history", "🌍", "GS I", "Industrial revolution, the American and French revolutions, colonialism, two world wars, the Cold War and decolonisation."),
    8: ("indian-society", "Indian society", "👥", "GS I", "Diversity, caste, family, women, population, urbanisation, globalisation, communalism, regionalism and secularism."),
    9: ("physical-geography", "Physical geography", "🌋", "GS I", "Earth's interior, plate tectonics, landforms, the atmosphere, winds, ocean currents and the climate system."),
    10: ("indian-geography", "Geography of India", "🗺️", "GS I", "The Himalayas, rivers, the monsoon, soils, natural vegetation and the physiographic regions of India."),
    11: ("resources-world-geography", "Resources & world geography", "⛏️", "GS I", "Where minerals, energy and industries are found, why, and the world's key straits, regions and resource geopolitics."),
    12: ("constitutional-framework", "Constitutional framework", "📜", "GS II", "The making of the Constitution, schedules, citizenship, fundamental duties, emergency provisions and other topics beyond the basics."),
    13: ("legislatures-executives", "Legislatures & executives in detail", "🏛️", "GS II", "Rajya Sabha, money bills, ordinances, the Speaker, anti-defection, the Attorney General, special provisions and union territories."),
    14: ("governance", "Governance & public policy", "🧾", "GS II", "Civil services, RTI, e-governance, citizens' charters, statutory and regulatory bodies, pressure groups and accountability."),
    15: ("social-justice", "Social justice & welfare", "🤝", "GS II", "Laws and schemes for SCs, STs, OBCs, minorities, women, children, disabled people, the elderly, and the health and education systems."),
    16: ("international-relations", "International relations & organisations", "🌐", "GS II", "The UN system, WTO, IMF and World Bank, regional groupings, and India's key bilateral and maritime relationships."),
    17: ("economy-basics", "Growth, development & inflation", "📈", "GS III", "GDP and how it is measured, inflation, poverty, unemployment, human development and India's growth story."),
    18: ("money-banking", "Money, banking & markets", "🏦", "GS III", "The RBI, monetary policy, banks, NPAs, financial inclusion, SEBI and capital markets, insurance, and digital payments."),
    19: ("public-finance-trade", "Public finance & external sector", "💱", "GS III", "Budgets, deficits, FRBM, GST, the balance of payments, exchange rates, FDI and trade policy."),
    20: ("agriculture", "Agriculture & food processing", "🌾", "GS III", "Cropping patterns, irrigation, land reforms, MSP and procurement, farm subsidies, the Green Revolution and allied sectors."),
    21: ("industry-infrastructure", "Industry, infrastructure & energy", "🏗️", "GS III", "Industrial policy, MSMEs, roads, railways, ports, power, renewable energy, and investment models such as PPP."),
    22: ("science-technology", "Science & technology", "🔬", "GS III", "Biotechnology, genetics, vaccines, nanotechnology, intellectual property and India's research system."),
    23: ("space-digital", "Space, defence technology & digital India", "🚀", "GS III", "ISRO's missions, satellites, missiles, nuclear policy, AI, semiconductors, cyber security and data protection."),
    24: ("environment-ecology", "Environment & ecology", "🌿", "GS III", "Ecosystems, food chains, pollution, environmental laws, EIA and the institutions that protect India's environment."),
    25: ("biodiversity", "Biodiversity & conservation", "🐅", "GS III", "Hotspots, protected areas, Project Tiger, wetlands, the IUCN Red List and international biodiversity treaties."),
    26: ("climate-disasters", "Climate change & disaster management", "🌀", "GS III", "Climate science, the UNFCCC and Paris Agreement, India's climate plans, and how India prepares for floods, cyclones and earthquakes."),
    27: ("internal-security", "Internal security", "🛡️", "GS III", "Left-wing extremism, the North-East, J&K, terrorism laws, border management, cyber threats, money laundering and security forces."),
    28: ("ethics-foundations", "Ethics: foundations", "🧠", "GS IV", "Ethics and human interface, attitude, emotional intelligence, moral thinkers and the values that guide decisions."),
    29: ("ethics-public-service", "Ethics in public service", "⚖️", "GS IV", "Integrity, probity, conflict of interest, codes of conduct, corruption, and how to approach case studies."),
    30: ("general-science", "General science for Prelims", "🧪", "Prelims", "Physics, chemistry and biology basics that keep turning up in the Prelims paper, explained simply."),
}

CA_THEMES = {
    1: ("polity-courts-2026", "Polity, Parliament & courts", "⚖️", "GS II", "The laws, bills and court rulings of 2026 that a UPSC aspirant needs to know, from SIR to the failed delimitation amendment."),
    2: ("elections-states-2026", "Elections & states", "🗳️", "GS II", "The 2026 assembly elections, new chief ministers, and the political changes in states across India."),
    3: ("economy-2026", "Economy", "📊", "GS III", "The 2026-27 Budget, new GDP and inflation series, RBI decisions, tax and labour changes, and the new rural jobs law."),
    4: ("trade-tariffs-2026", "Trade deals & tariffs", "🤝", "GS II/III", "The India–EU deal, the US tariff roller-coaster, and the other trade agreements India signed in 2026."),
    5: ("world-affairs-2026", "India & the world", "🌏", "GS II", "BRICS under India's chair, the Iran war and the Strait of Hormuz, and changes in India's neighbourhood."),
    6: ("security-defence-2026", "Security & defence", "🛡️", "GS III", "Maoist violence, terror cases, new military leadership, missile tests and maritime incidents in 2026."),
    7: ("science-tech-2026", "Science, tech & space", "🛰️", "GS III", "The AI Impact Summit, ISRO's year, digital regulation, semiconductors and public health alerts."),
    8: ("environment-2026", "Environment & disasters", "🌧️", "GS III", "Floods, heat, climate talks, new heritage sites and the environmental debates of 2026."),
    9: ("society-education-2026", "Education, health & society", "🎓", "GS I/II", "Exam leaks and the NEET cancellation, campus rules, public health and the social debates of 2026."),
    10: ("sports-culture-2026", "Sports, culture & people", "🏆", "Prelims", "India's T20 World Cup win, upcoming global events, awards, and notable people the country lost in 2026."),
}

SERIES_INFO = {
    "upsc-300": dict(
        name="UPSC 300", long="UPSC 300: the syllabus in short notes", themes=UPSC_THEMES, count=300, per_theme=10,
        hub="/upsc-300.html", kicker="Exam-ready series",
        lede="The UPSC Civil Services syllabus in 300 short notes across 30 themes: history, geography, society, polity, economy, science, environment, security and ethics. Each note ends with key takeaways, why it matters for the exam, and a practice question.",
        why_label="Why it matters for UPSC", q_label="Practice question"),
    "current-affairs-100": dict(
        name="Current Affairs 100", long="Current Affairs 100: India in 2026", themes=CA_THEMES, count=100, per_theme=10,
        hub="/current-affairs-100.html", kicker="Current affairs series",
        lede="One hundred short notes on what happened in India and the world in 2026, chosen for UPSC and competitive-exam readers. Every note lists the sources its facts were checked against.",
        why_label="Why it matters for UPSC", q_label="Discussion question"),
}
