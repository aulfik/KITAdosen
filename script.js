const linkGroups = [
    {
        category: "Dosen Nasional",
        links: [
            { name: "SINTA", url: "https://sinta.kemdiktisaintek.go.id/" },
            { name: "GARUDA", url: "http://garuda.kemdiktisaintek.go.id/" },
            { name: "SISTER", url: "https://sister.kemdiktisaintek.go.id/beranda" },
            { name: "DIKTI HR", url: "https://osdm.kemdiktisaintek.go.id/diktihr/" },
            { name: "OSDM SKP", url: "https://osdm.kemdiktisaintek.go.id/skp/site/login" },
            { name: "OSDM KEMDIKTISAINTEK", url: "https://osdm.kemdiktisaintek.go.id/" },
            { name: "INTRA PRESENSI", url: "https://intradikti.kemdiktisaintek.go.id/presensi/dashboard" },
            { name: "MY ASN", url: "https://asndigital.bkn.go.id/" },
            { name: "TUBEL", url: "https://osdm.kemdiktisaintek.go.id/etubel/" },
            { name: "BIMA", url: "https://bima.kemdiktisaintek.go.id/" },
            { name: "ARJUNA", url: "https://arjuna.kemdiktisaintek.go.id/#/beranda" },
            { name: "ANJANI", url: "https://anjani.kemdikbud.go.id/" },
            { name: "HILIR RISET", url: "https://hiliriset.kemdiktisaintek.go.id/" },
            { name: "RISBANG KEMDIKTISAINTEK", url: "https://risbang.kemdiktisaintek.go.id/" },
            { name: "BEASISWA SDM", url: "https://beasiswadosen.kemdiktisaintek.go.id/" },
            { name: "PDDIKTI", url: "https://pddikti.kemdiktisaintek.go.id/" }
        ]
    },
    {
        category: "Lainnya",
        links: [
            { name: "SCOPUS", url: "https://www.scopus.com/" },
            { name: "GOOGLE SCHOLAR", url: "https://scholar.google.com/" },
            { name: "ORCHID", url: "https://orcid.org/" },
            { name: "WOS", url: "https://www.webofscience.com/wos/" }
        ]
    }
];

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('contentContainer');
    const searchInput = document.getElementById('searchInput');

    // Render cards by category
    linkGroups.forEach((group, groupIndex) => {
        // Create section
        const section = document.createElement('div');
        section.className = 'category-section';
        section.style.animationDelay = `${groupIndex * 0.2}s`;

        // Create title
        const title = document.createElement('h2');
        title.className = 'category-title';
        title.textContent = group.category;
        section.appendChild(title);

        // Create grid
        const grid = document.createElement('div');
        grid.className = 'grid';

        group.links.forEach((link, index) => {
            let domain = "";
            try {
                domain = new URL(link.url).hostname.replace('www.', '');
            } catch (e) {
                domain = link.url;
            }

            const card = document.createElement('a');
            card.href = link.url;
            card.target = '_blank';
            card.rel = 'noopener noreferrer';
            card.className = 'card';
            card.style.animationDelay = `${(groupIndex * 0.2) + (index * 0.05)}s`;

            card.innerHTML = `
                <div class="card-icon-wrapper">
                    <img src="https://logo.clearbit.com/${domain}" alt="${link.name} Logo" class="card-logo" 
                    onerror="
                        if (!this.dataset.triedGoogle) { 
                            this.dataset.triedGoogle = 'true'; 
                            this.src = 'https://icons.duckduckgo.com/ip3/${domain}.ico'; 
                        } else if (!this.dataset.triedAvatar) { 
                            this.dataset.triedAvatar = 'true'; 
                            this.src = 'https://ui-avatars.com/api/?name=${encodeURIComponent(link.name)}&background=4F46E5&color=fff&size=128&bold=true'; 
                        }
                    ">
                </div>
                <div class="card-content">
                    <span class="card-title">${link.name}</span>
                    <span class="card-domain">${domain}</span>
                </div>
            `;

            grid.appendChild(card);
        });

        section.appendChild(grid);
        container.appendChild(section);
    });

    // Search functionality
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const sections = container.querySelectorAll('.category-section');

        sections.forEach(section => {
            const cards = section.querySelectorAll('.card');
            let hasVisibleCards = false;

            cards.forEach(card => {
                const title = card.querySelector('.card-title').textContent.toLowerCase();
                const domain = card.querySelector('.card-domain').textContent.toLowerCase();

                if (title.includes(searchTerm) || domain.includes(searchTerm)) {
                    card.classList.remove('hidden');
                    hasVisibleCards = true;
                } else {
                    card.classList.add('hidden');
                }
            });

            // Hide the entire section if no cards match
            if (hasVisibleCards) {
                section.classList.remove('hidden');
            } else {
                section.classList.add('hidden');
            }
        });
    });
});
