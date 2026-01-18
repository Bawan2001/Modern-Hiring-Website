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
                <button onclick="openApplyModal(${job.id}, '${job.title}')" class="btn-primary" style="width:100%;margin-top:1.5rem">Apply Now</button>
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

    // 3. Admin Dashboard Job Loading & Apps
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

    async function fetchAdminApps() {
        const adminAppsList = document.getElementById('admin-apps-list');
        if (!adminAppsList) return;
        try {
            const response = await fetch('/api/applications');
            const apps = await response.json();

            adminAppsList.innerHTML = apps.map(app => `
               <tr>
                   <td>
                       <strong>${app.user_name}</strong><br>
                       <span style="font-size:0.85rem;color:#94a3b8">${app.user_email}</span>
                   </td>
                   <td>${app.job_title}</td>
                   <td>${app.date}</td>
                   <td><span class="status-badge status-${app.status.toLowerCase()}">${app.status}</span></td>
                   <td>
                       <button onclick="updateStatus(${app.id}, 'Interviewing')" class="btn-primary btn-sm">Accept</button>
                       <button onclick="updateStatus(${app.id}, 'Rejected')" class="btn-secondary btn-sm">Reject</button>
                   </td>
               </tr>
           `).join('');
        } catch (error) {
            console.error('Error fetching admin apps:', error);
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

    // Tab Switching
    const tabs = document.querySelectorAll('.admin-nav li');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const target = tab.dataset.tab;
            document.querySelectorAll('.admin-section').forEach(s => s.classList.add('hidden'));
            document.getElementById(`section-${target}`).classList.remove('hidden');

            if (target === 'applications') fetchAdminApps();
        });
    });

    // 4. Modal and Job Posting
    const modal = document.getElementById('job-modal');
    const addJobTrigger = document.getElementById('add-job-trigger');
    const closeModal = document.getElementById('close-modal');
    const addJobForm = document.getElementById('add-job-form');

    if (addJobTrigger && modal) {
        addJobTrigger.addEventListener('click', () => modal.classList.add('active'));
    }

    if (closeModal && modal) {
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

    // 5. User Dashboard
    const myAppsList = document.getElementById('my-applications');
    if (myAppsList) {
        async function fetchMyApps() {
            try {
                const response = await fetch('/api/applications');
                const apps = await response.json();

                document.getElementById('stat-total').innerText = apps.length;
                document.getElementById('stat-interview').innerText = apps.filter(a => a.status === 'Interviewing').length;
                document.getElementById('stat-offer').innerText = apps.filter(a => a.status === 'Offer').length;

                if (apps.length === 0) {
                    myAppsList.innerHTML = '<p style="text-align:center;color:#94a3b8">You haven\'t applied to any jobs yet.</p>';
                    return;
                }

                myAppsList.innerHTML = apps.map(app => `
                    <div class="app-card">
                        <div class="app-info">
                            <h4>${app.job_title}</h4>
                            <p>${app.company}</p>
                        </div>
                        <span class="status-badge status-${app.status.toLowerCase()}">${app.status}</span>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Error fetching my apps:', error);
            }
        }
        fetchMyApps();
    }

    // 6. Apply Logic (Global)
    window.openApplyModal = (jobId, jobTitle) => {
        const applyModal = document.getElementById('apply-modal');
        if (!applyModal) {
            window.location.href = '/login'; // Redirect if not logged in (modal won't exist usually but logic flow)
            return;
        }
        document.getElementById('apply-job-id').value = jobId;
        document.getElementById('apply-job-title').innerText = jobTitle;
        applyModal.classList.add('active');
    };

    const applyForm = document.getElementById('apply-form');
    if (applyForm) {
        document.getElementById('close-apply-modal').addEventListener('click', () => {
            document.getElementById('apply-modal').classList.remove('active');
        });

        applyForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = applyForm.querySelector('button[type="submit"]');
            btn.innerText = 'Submitting...';
            btn.disabled = true;

            try {
                const res = await fetch('/api/apply', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        job_id: parseInt(document.getElementById('apply-job-id').value),
                        cover_letter: document.getElementById('cover-letter').value
                    })
                });
                if (res.ok) {
                    alert('Application submitted successfully!');
                    document.getElementById('apply-modal').classList.remove('active');
                    applyForm.reset();
                } else {
                    const d = await res.json();
                    alert(d.error || 'Failed to apply');
                }
            } catch (err) {
                alert('Error applying');
            } finally {
                btn.innerText = 'Submit Application';
                btn.disabled = false;
            }
        });
    }

    // Global helper for admin status update
    window.updateStatus = async (appId, status) => {
        try {
            const res = await fetch(`/api/applications/${appId}/status`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status })
            });
            if (res.ok) fetchAdminApps();
        } catch (e) { console.error(e); }
    };

    // Init
    fetchJobs();
    fetchAdminJobs();
    fetchAdminApps();
});
