document.addEventListener('DOMContentLoaded', () => {
    // Shared elements
    const jobsContainer = document.getElementById('jobs-container');
    const adminJobsList = document.getElementById('admin-jobs-list');

    // 1. Fetch and Render Jobs (Home Page)
    async function fetchJobs() {
        if (!jobsContainer) return;
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

    // 2. ATS Score Calculation
    const calculateBtn = document.getElementById('calculate-btn');
    if (calculateBtn) {
        calculateBtn.addEventListener('click', async () => {
            const resume = document.getElementById('resume-text').value;
            const description = document.getElementById('job-desc').value;
            const resultsDiv = document.getElementById('ats-results');

            if (!resume || !description) {
                alert('Please provide both resume and job description.');
                return;
            }

            calculateBtn.innerText = 'Analyzing...';
            calculateBtn.disabled = true;

            try {
                const response = await fetch('/api/ats-score', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ resume, description })
                });

                const data = await response.json();

                if (data.error) throw new Error(data.error);

                // Update UI
                resultsDiv.classList.remove('hidden');
                document.getElementById('score-value').innerText = `${data.score}%`;

                const matchedList = document.getElementById('matched-list');
                matchedList.innerHTML = data.matched_keywords.map(kw => `<span class="tag tag-matched">${kw}</span>`).join('');

                const missingList = document.getElementById('missing-list');
                missingList.innerHTML = data.suggestions.map(kw => `<span class="tag tag-missing">${kw}</span>`).join('');

                resultsDiv.scrollIntoView({ behavior: 'smooth' });
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                calculateBtn.innerText = 'Calculate Score';
                calculateBtn.disabled = false;
            }
        });
    }

    // 3. Admin Dashboard Job Loading
    async function fetchAdminJobs() {
        if (!adminJobsList) return;
        try {
            const response = await fetch('/api/jobs');
            const jobs = await response.json();
            renderAdminJobs(jobs);
        } catch (error) {
            console.error('Error fetching admin jobs:', error);
        }
    }

    function renderAdminJobs(jobs) {
        adminJobsList.innerHTML = jobs.map(job => `
            <tr>
                <td><strong>${job.title}</strong></td>
                <td>${job.company}</td>
                <td>${job.location}</td>
                <td><span class="badge">Active</span></td>
                <td>
                    <button class="btn-primary btn-sm">Edit</button>
                    <button class="btn-secondary btn-sm">Archive</button>
                </td>
            </tr>
        `).join('');
    }

    // 4. Modal and Job Posting
    const modal = document.getElementById('job-modal');
    const addJobTrigger = document.getElementById('add-job-trigger');
    const closeModal = document.getElementById('close-modal');
    const addJobForm = document.getElementById('add-job-form');

    if (addJobTrigger) {
        addJobTrigger.addEventListener('click', () => modal.classList.add('active'));
    }

    if (closeModal) {
        closeModal.addEventListener('click', () => modal.classList.remove('active'));
    }

    if (addJobForm) {
        addJobForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const jobData = {
                title: document.getElementById('title').value,
                company: document.getElementById('company').value,
                location: document.getElementById('location').value,
                salary: document.getElementById('salary').value,
                type: document.getElementById('type').value,
                category: 'Uncategorized',
                description: 'Added via admin dashboard'
            };

            try {
                const response = await fetch('/api/jobs', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jobData)
                });

                if (response.ok) {
                    modal.classList.remove('active');
                    addJobForm.reset();
                    fetchAdminJobs();
                    alert('Job posted successfully!');
                } else {
                    const data = await response.json();
                    alert('Error: ' + (data.error || 'Failed to post job'));
                }
            } catch (error) {
                console.error('Error posting job:', error);
            }
        });
    }

    // Init
    fetchJobs();
    fetchAdminJobs();
});
