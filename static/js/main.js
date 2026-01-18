document.addEventListener('DOMContentLoaded', () => {
    const jobsContainer = document.getElementById('jobs-container');

    async function fetchJobs() {
        try {
            const response = await fetch('/api/jobs');
            const jobs = await response.json();
            renderJobs(jobs);
        } catch (error) {
            console.error('Error fetching jobs:', error);
            jobsContainer.innerHTML = '<p>Error loading jobs. Please try again later.</p>';
        }
    }

    function renderJobs(jobs) {
        jobsContainer.innerHTML = '';
        jobs.forEach((job, index) => {
            const jobCard = document.createElement('div');
            jobCard.className = 'job-card';
            jobCard.style.animationDelay = `${index * 0.1}s`;
            
            jobCard.innerHTML = `
                <span class="job-type">${job.type}</span>
                <h3 class="job-title">${job.title}</h3>
                <div class="company-name">🏢 ${job.company}</div>
                <div class="job-details">
                    <span>📍 ${job.location}</span>
                    <span class="job-salary">${job.salary}</span>
                </div>
            `;
            
            jobsContainer.appendChild(jobCard);
        });
    }

    fetchJobs();
});
