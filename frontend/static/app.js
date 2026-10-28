/**
 * AI Karmayogi Prototype v2.0 - Client Application Engine
 */

const API_BASE = '/api';

class KarmayogiApp {
  constructor() {
    this.userId = 'U001';
    this.activeTab = 'dashboard';
    this.roles = [];
    this.selectedInterviewRole = 'R002';
    this.selectedGapRole = 'R002';
    this.selectedCareerRole = 'R002';
    
    // Active Interview State
    this.interviewSession = null;
    this.interviewQuestions = [];
    this.currentInterviewIndex = 0;
    
    // Active Test State
    this.activeTest = null;
    this.testQuestions = [];
    this.currentTestIndex = 0;
    this.userAnswers = {};

    // Active Syllabus Module
    this.selectedSyllabusModuleId = 'MOD_006'; // Project Management default
    this.syllabusModules = [];

    this.init();
  }

  async init() {
    this.bindEvents();
    await this.loadInitialData();
    this.switchTab('dashboard');
  }

  bindEvents() {
    // User Switcher
    const userSelect = document.getElementById('userSelect');
    if (userSelect) {
      userSelect.addEventListener('change', (e) => {
        this.userId = e.target.value;
        this.showToast(`Switched active profile to ${e.target.options[e.target.selectedIndex].text}`, 'info');
        this.refreshCurrentTab();
      });
    }

    // Reset State Button
    const resetBtn = document.getElementById('resetStateBtn');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => this.resetUserProgress());
    }

    // Nav Tabs
    document.querySelectorAll('#mainNav .nav-tab').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const tab = btn.getAttribute('data-tab');
        this.switchTab(tab);
      });
    });

    // Interview Events
    document.getElementById('startInterviewBtn')?.addEventListener('click', () => this.startInterview());
    document.getElementById('submitAnswerBtn')?.addEventListener('click', () => this.submitInterviewAnswer());
    document.getElementById('nextInterviewQBtn')?.addEventListener('click', () => this.nextInterviewQuestion());

    // Skill Gap Role Change
    document.getElementById('gapTargetRoleSelect')?.addEventListener('change', (e) => {
      this.selectedGapRole = e.target.value;
      this.loadSkillGaps();
    });

    // Career Role Change
    document.getElementById('careerTargetRoleSelect')?.addEventListener('change', (e) => {
      this.selectedCareerRole = e.target.value;
      this.loadCareerRoadmap();
    });

    // Test Events
    document.getElementById('generateTestBtn')?.addEventListener('click', () => this.generateTest());
    document.getElementById('testPrevBtn')?.addEventListener('click', () => this.prevTestQuestion());
    document.getElementById('testNextBtn')?.addEventListener('click', () => this.nextTestQuestion());
    document.getElementById('testSubmitBtn')?.addEventListener('click', () => this.submitTest());

    // Mentor Events
    document.getElementById('sendMentorBtn')?.addEventListener('click', () => this.sendMentorMessage());
    document.getElementById('mentorInput')?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') this.sendMentorMessage();
    });
  }

  showToast(msg, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    const colorClass = type === 'success' ? 'bg-emerald-600' : type === 'error' ? 'bg-rose-600' : 'bg-knavy-900';
    toast.className = `${colorClass} text-white text-xs px-4 py-2.5 rounded-lg shadow-lg flex items-center space-x-2 transition-all duration-300 pointer-events-auto border border-white/10`;
    toast.innerHTML = `<span>${msg}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  switchTab(tabId) {
    this.activeTab = tabId;
    document.querySelectorAll('#mainNav .nav-tab').forEach(btn => {
      if (btn.getAttribute('data-tab') === tabId) {
        btn.classList.add('active', 'bg-slate-800/80', 'text-white');
      } else {
        btn.classList.remove('active', 'bg-slate-800/80', 'text-white');
      }
    });

    document.querySelectorAll('.tab-content').forEach(sec => {
      sec.classList.add('hidden');
    });

    const activeSec = document.getElementById(`tab-${tabId}`);
    if (activeSec) {
      activeSec.classList.remove('hidden');
    }

    this.refreshCurrentTab();
    lucide.createIcons();
  }

  refreshCurrentTab() {
    switch (this.activeTab) {
      case 'dashboard': this.loadDashboard(); break;
      case 'interview': this.loadInterviewSetup(); break;
      case 'skill-gap': this.loadSkillGaps(); break;
      case 'career': this.loadCareerRoadmap(); break;
      case 'syllabus': this.loadSyllabus(); break;
      case 'tests': this.loadTestSetup(); break;
      case 'passport': this.loadPassport(); break;
    }
  }

  async loadInitialData() {
    try {
      const res = await fetch(`${API_BASE}/roles`);
      this.roles = await res.json();
      this.populateRoleSelects();
    } catch (e) {
      console.error('Failed to load initial roles:', e);
    }
  }

  populateRoleSelects() {
    const interviewSelect = document.getElementById('interviewRoleSelect');
    const gapSelect = document.getElementById('gapTargetRoleSelect');
    const careerSelect = document.getElementById('careerTargetRoleSelect');

    const opts = this.roles.map(r => `<option value="${r.role_id}">${r.role_name} (${r.role_id})</option>`).join('');
    
    if (interviewSelect) { interviewSelect.innerHTML = opts; interviewSelect.value = 'R002'; }
    if (gapSelect) { gapSelect.innerHTML = opts; gapSelect.value = 'R002'; }
    if (careerSelect) { careerSelect.innerHTML = opts; careerSelect.value = 'R002'; }
  }
  // ==========================================
  // DASHBOARD
  // ==========================================
  async loadDashboard() {
    try {
      const res = await fetch(`${API_BASE}/dashboard/${this.userId}`);
      if (!res.ok) throw new Error('Failed to load dashboard data');
      const data = await res.json();

      document.getElementById('dashUserName').textContent = `Welcome, ${data.name}`;
      document.getElementById('dashCurrentRole').textContent = data.current_role.role_name;
      document.getElementById('dashTargetRole').textContent = data.target_role.role_name;
      document.getElementById('dashDepartment').textContent = data.department || 'Administrative Reforms';
      document.getElementById('dashProgressPercent').textContent = `${data.overall_progress_percent}%`;
      document.getElementById('dashCompCount').textContent = data.competencies_count;

      // Recommended Action
      if (data.recommended_next_action) {
        document.getElementById('dashActionTitle').textContent = data.recommended_next_action.title;
        document.getElementById('dashActionDesc').textContent = data.recommended_next_action.description;
      }

      // Top Gaps List
      const gapsContainer = document.getElementById('dashTopGapsContainer');
      if (gapsContainer) {
        if (data.top_skill_gaps && data.top_skill_gaps.length > 0) {
          gapsContainer.innerHTML = data.top_skill_gaps.map(g => `
            <div class="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-lg hover:border-slate-300 transition-colors">
              <div>
                <strong class="text-xs text-slate-900 block">${g.competency_name}</strong>
                <span class="text-[11px] text-slate-500">Current Level ${g.current_level} → Required Level ${g.required_level}</span>
              </div>
              <div class="flex items-center space-x-2">
                <span class="bg-rose-100 text-rose-800 text-[10px] font-bold px-2 py-0.5 rounded-full">Gap: -${g.gap}</span>
                <button onclick="app.switchTab('skill-gap')" class="text-xs text-blue-600 hover:text-blue-800 font-medium">Practice</button>
              </div>
            </div>
          `).join('');
        } else {
          gapsContainer.innerHTML = `<p class="text-xs text-slate-400 italic">No significant competency gaps detected for this role.</p>`;
        }
      }

      // Courses List
      const coursesContainer = document.getElementById('dashCoursesContainer');
      if (coursesContainer) {
        if (data.courses_in_progress && data.courses_in_progress.length > 0) {
          coursesContainer.innerHTML = data.courses_in_progress.map(c => `
            <div class="p-2.5 bg-slate-50 border border-slate-200 rounded-lg space-y-1.5">
              <div class="flex justify-between items-center text-xs">
                <span class="font-semibold text-slate-800 truncate max-w-[180px]">${c.course_title}</span>
                <span class="text-[10px] text-slate-500">${c.progress_percent}%</span>
              </div>
              <div class="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                <div class="bg-blue-600 h-full rounded-full" style="width: ${c.progress_percent}%"></div>
              </div>
            </div>
          `).join('');
        } else {
          coursesContainer.innerHTML = `<p class="text-xs text-slate-400 italic">No enrolled courses.</p>`;
        }
      }

      // Recent Tests
      const testsContainer = document.getElementById('dashRecentTestsContainer');
      if (testsContainer) {
        if (data.recent_test_scores && data.recent_test_scores.length > 0) {
          testsContainer.innerHTML = data.recent_test_scores.map(t => `
            <div class="flex items-center justify-between p-2 bg-slate-50 border border-slate-200 rounded-lg text-xs">
              <span class="font-medium text-slate-700">${t.topic}</span>
              <span class="font-bold ${t.percentage >= 75 ? 'text-emerald-600' : 'text-amber-600'}">${t.score}/${t.total_questions} (${t.percentage}%)</span>
            </div>
          `).join('');
        } else {
          testsContainer.innerHTML = `<p class="text-xs text-slate-400 italic">No test attempts yet.</p>`;
        }
      }

      lucide.createIcons();
    } catch (e) {
      console.error('Error loading dashboard:', e);
      this.showToast('Failed to load dashboard summary.', 'error');
    }
  }

  // ==========================================
  // AI MOCK INTERVIEW
  // ==========================================
  async loadInterviewSetup() {
    try {
      const res = await fetch(`${API_BASE}/test/topics`);
      const data = await res.json();
      const compSelect = document.getElementById('interviewCompSelect');
      if (compSelect && data.competencies) {
        compSelect.innerHTML = `<option value="Auto">Auto (Balanced Role Competencies)</option>` +
          data.competencies.map(c => `<option value="${c.competency_id}">${c.competency_name}</option>`).join('');
      }
    } catch (e) {
      console.error('Failed to load interview competencies:', e);
    }
  }

  async startInterview() {
    const roleId = document.getElementById('interviewRoleSelect').value;
    const compId = document.getElementById('interviewCompSelect').value;
    const count = parseInt(document.getElementById('interviewCountSelect').value) || 5;

    const startBtn = document.getElementById('startInterviewBtn');
    startBtn.disabled = true;
    startBtn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Retrieving & Grounding...</span>`;
    lucide.createIcons();

    try {
      const res = await fetch(`${API_BASE}/interview/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.userId,
          role_id: roleId,
          competency_id: compId,
          question_count: count
        })
      });

      if (!res.ok) throw new Error('Failed to start interview session');
      const data = await res.json();

      this.interviewSession = data.session_id;
      this.interviewQuestions = data.questions;
      this.currentInterviewIndex = 0;

      document.getElementById('interviewSetupCard').classList.add('hidden');
      document.getElementById('interviewActiveCard').classList.remove('hidden');
      document.getElementById('interviewFinalReportCard').classList.add('hidden');

      this.renderInterviewQuestion();
      this.showToast(`Interview session started with ${data.total_questions} questions!`, 'success');
    } catch (e) {
      console.error('Error starting interview:', e);
      this.showToast('Could not start mock interview session.', 'error');
    } finally {
      startBtn.disabled = false;
      startBtn.innerHTML = `<i data-lucide="play" class="w-4 h-4"></i><span>Start Mock Interview</span>`;
      lucide.createIcons();
    }
  }

  renderInterviewQuestion() {
    const q = this.interviewQuestions[this.currentInterviewIndex];
    if (!q) return;

    document.getElementById('interviewQProgress').textContent = `Q ${this.currentInterviewIndex + 1} / ${this.interviewQuestions.length}`;
    document.getElementById('interviewQComp').textContent = `Competency: ${q.competency_name}`;
    document.getElementById('interviewQText').textContent = q.question_text;
    document.getElementById('interviewQFocus').textContent = `Behavioral Focus: ${q.behavioral_focus || 'Discretionary Judgment'}`;
    
    const sourceEl = document.getElementById('interviewQSource');
    if (q.source_type === 'ai_generated') {
      sourceEl.className = 'badge-generated text-[10px] px-2 py-0.5 rounded font-mono font-medium';
      sourceEl.textContent = '✨ AI Generated Question';
    } else {
      sourceEl.className = 'badge-prototype text-[10px] px-2 py-0.5 rounded font-mono font-medium';
      sourceEl.textContent = '📚 Prototype Question Bank';
    }

    document.getElementById('interviewAnswerInput').value = '';
    document.getElementById('interviewEvalCard').classList.add('hidden');
    document.getElementById('submitAnswerBtn').disabled = false;
    lucide.createIcons();
  }

  async submitInterviewAnswer() {
    const answerText = document.getElementById('interviewAnswerInput').value.trim();
    if (!answerText) {
      this.showToast('Please type your response using the STAR method before submitting.', 'info');
      return;
    }

    const submitBtn = document.getElementById('submitAnswerBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>AI Assessing Response...</span>`;
    lucide.createIcons();

    try {
      const res = await fetch(`${API_BASE}/interview/${this.interviewSession}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: this.interviewSession,
          question_index: this.currentInterviewIndex + 1,
          user_answer: answerText
        })
      });

      if (!res.ok) throw new Error('Evaluation failed');
      const data = await res.json();

      // Render 5D evaluation
      document.getElementById('evalAvgScore').textContent = `${data.average_score} / 5.0`;

      const dimsGrid = document.getElementById('evalDimensionsGrid');
      const scores = data.scores || {};
      dimsGrid.innerHTML = `
        <div class="bg-slate-50 border border-slate-200 p-2 rounded">
          <div class="font-bold text-slate-900">${scores.relevance || 4.0}</div>
          <div class="text-[10px] text-slate-500">Relevance</div>
        </div>
        <div class="bg-slate-50 border border-slate-200 p-2 rounded">
          <div class="font-bold text-slate-900">${scores.clarity_and_structure || 4.0}</div>
          <div class="text-[10px] text-slate-500">STAR Clarity</div>
        </div>
        <div class="bg-slate-50 border border-slate-200 p-2 rounded">
          <div class="font-bold text-slate-900">${scores.reasoning_and_depth || 4.0}</div>
          <div class="text-[10px] text-slate-500">Reasoning</div>
        </div>
        <div class="bg-slate-50 border border-slate-200 p-2 rounded">
          <div class="font-bold text-slate-900">${scores.role_competency || 4.0}</div>
          <div class="text-[10px] text-slate-500">Role Match</div>
        </div>
        <div class="bg-slate-50 border border-slate-200 p-2 rounded">
          <div class="font-bold text-slate-900">${scores.practical_judgment_ethics || 4.0}</div>
          <div class="text-[10px] text-slate-500">Ethics/Rules</div>
        </div>
      `;

      document.getElementById('evalStrengthsList').innerHTML = (data.strengths || []).map(s => `<li>${s}</li>`).join('');
      document.getElementById('evalWeaknessesList').innerHTML = (data.weaknesses || []).map(w => `<li>${w}</li>`).join('');
      document.getElementById('evalNarrativeText').textContent = data.feedback_narrative || data.suggested_improvement;

      const nextBtn = document.getElementById('nextInterviewQBtn');
      if (data.is_last_question) {
        nextBtn.innerHTML = `<span>View Final Comprehensive Report</span><i data-lucide="check-circle" class="w-3.5 h-3.5"></i>`;
      } else {
        nextBtn.innerHTML = `<span>Next Question</span><i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>`;
      }

      document.getElementById('interviewEvalCard').classList.remove('hidden');
      lucide.createIcons();
    } catch (e) {
      console.error('Error evaluating answer:', e);
      this.showToast('Could not evaluate interview answer.', 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<i data-lucide="send" class="w-3.5 h-3.5"></i><span>Submit Response for AI Evaluation</span>`;
      lucide.createIcons();
    }
  }

  async nextInterviewQuestion() {
    if (this.currentInterviewIndex + 1 < this.interviewQuestions.length) {
      this.currentInterviewIndex++;
      this.renderInterviewQuestion();
    } else {
      // Show final report
      try {
        const res = await fetch(`${API_BASE}/interview/${this.interviewSession}/result`);
        const report = await res.json();

        document.getElementById('finalReportRole').textContent = `Role: ${report.role_name}`;
        document.getElementById('finalOverallScore').textContent = `${report.overall_score} / 5.0`;
        document.getElementById('finalReportSummary').textContent = report.summary;

        document.getElementById('finalStrengthsList').innerHTML = (report.strengths_overview || []).map(s => `<li>${s}</li>`).join('');
        document.getElementById('finalActionsList').innerHTML = (report.recommended_actions || []).map(a => `<li>${a}</li>`).join('');

        document.getElementById('interviewActiveCard').classList.add('hidden');
        document.getElementById('interviewFinalReportCard').classList.remove('hidden');
        lucide.createIcons();
      } catch (e) {
        console.error('Error fetching final interview report:', e);
      }
    }
  }

  restartInterview() {
    document.getElementById('interviewSetupCard').classList.remove('hidden');
    document.getElementById('interviewActiveCard').classList.add('hidden');
    document.getElementById('interviewFinalReportCard').classList.add('hidden');
  }

  // ==========================================
  // SKILL GAP ANALYSIS
  // ==========================================
  async loadSkillGaps() {
    try {
      const res = await fetch(`${API_BASE}/users/${this.userId}/skill-gaps?target_role_id=${this.selectedGapRole}`);
      if (!res.ok) throw new Error('Failed to load skill gaps');
      const data = await res.json();

      document.getElementById('gapOverallSummary').innerHTML = `<strong>Role Summary (${data.current_role} → ${data.target_role}):</strong> ${data.overall_summary}`;

      const tbody = document.getElementById('skillGapTableBody');
      if (tbody) {
        tbody.innerHTML = (data.gaps || []).map(g => {
          const priorityBadge = g.gap <= 0 
            ? `<span class="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-full">Meets Target</span>`
            : g.gap === 1 
            ? `<span class="bg-blue-100 text-blue-800 text-[10px] font-bold px-2 py-0.5 rounded-full">Small Gap</span>`
            : g.gap === 2 
            ? `<span class="bg-amber-100 text-amber-800 text-[10px] font-bold px-2 py-0.5 rounded-full">Moderate Gap</span>`
            : `<span class="bg-rose-100 text-rose-800 text-[10px] font-bold px-2 py-0.5 rounded-full">High Priority</span>`;

          const courseTitle = g.recommended_courses && g.recommended_courses.length > 0 ? g.recommended_courses[0].course_title : 'General Public Admin Track';

          return `
            <tr class="hover:bg-slate-50/80 transition-colors">
              <td class="py-3 px-4">
                <strong class="text-slate-900 block font-semibold">${g.competency_name}</strong>
                <p class="text-[11px] text-slate-500 mt-0.5 line-clamp-1">${g.ai_explanation || ''}</p>
              </td>
              <td class="py-3 px-3 text-slate-600 font-medium">${g.competency_type || 'Functional'}</td>
              <td class="py-3 px-3 text-center">
                <span class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-800 font-bold text-xs">L${g.current_level}</span>
              </td>
              <td class="py-3 px-3 text-center">
                <span class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-ksaffron-100 text-ksaffron-800 font-bold text-xs">L${g.required_level}</span>
              </td>
              <td class="py-3 px-3 text-center">
                <span class="font-mono font-bold ${g.gap > 0 ? 'text-rose-600' : 'text-emerald-600'}">${g.gap > 0 ? `-${g.gap}` : '0'}</span>
              </td>
              <td class="py-3 px-3">${priorityBadge}</td>
              <td class="py-3 px-4 space-y-1">
                <div class="text-[11px] font-medium text-slate-700 truncate max-w-[200px]" title="${courseTitle}">📖 ${courseTitle}</div>
                <button onclick="app.switchTab('tests')" class="text-[11px] text-blue-600 hover:text-blue-800 font-semibold underline block">Take Assessment</button>
              </td>
            </tr>
          `;
        }).join('');
      }

      lucide.createIcons();
    } catch (e) {
      console.error('Error loading skill gaps:', e);
      this.showToast('Could not load skill gap analysis.', 'error');
    }
  }

  // ==========================================
  // CAREER PATH PLANNER
  // ==========================================
  async loadCareerRoadmap() {
    try {
      const res = await fetch(`${API_BASE}/career/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.userId,
          target_role_id: this.selectedCareerRole
        })
      });

      if (!res.ok) throw new Error('Failed to generate career roadmap');
      const data = await res.json();

      document.getElementById('careerFromRole').textContent = data.current_role_name;
      document.getElementById('careerToRole').textContent = data.target_role_name;
      document.getElementById('careerReadinessStatus').textContent = data.readiness_status;
      document.getElementById('careerReadinessScore').textContent = `${data.readiness_score}%`;
      document.getElementById('careerActionPlanSummary').textContent = data.action_plan;

      // 4-Phase Roadmap
      const roadmapGrid = document.getElementById('careerRoadmapGrid');
      if (roadmapGrid) {
        roadmapGrid.innerHTML = (data.roadmap_steps || []).map((step, idx) => `
          <div class="border border-slate-200 bg-white p-4 rounded-xl space-y-2 shadow-sm relative overflow-hidden">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-bold text-ksaffron-600 uppercase">Stage 0${idx+1}</span>
              <span class="text-[10px] ${step.status === 'in_progress' ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-600'} px-2 py-0.5 rounded-full font-medium">${step.status || 'upcoming'}</span>
            </div>
            <h5 class="text-xs font-bold text-slate-900">${step.title}</h5>
            <p class="text-[11px] text-slate-600 leading-relaxed">${step.description}</p>
            <ul class="text-[10px] text-slate-500 list-disc list-inside space-y-0.5 pt-1">
              ${(step.actions || []).map(a => `<li>${a}</li>`).join('')}
            </ul>
          </div>
        `).join('');
      }

      // Target Competency Matrix
      const compsGrid = document.getElementById('careerCompsGrid');
      if (compsGrid) {
        compsGrid.innerHTML = (data.target_competencies || []).map(c => `
          <div class="p-3 bg-slate-50 border border-slate-200 rounded-lg flex items-center justify-between text-xs">
            <div>
              <strong class="text-slate-900 block">${c.competency_name}</strong>
              <span class="text-[11px] text-slate-500">Current L${c.current_level} → Target L${c.required_level}</span>
            </div>
            <span class="font-bold ${c.gap > 0 ? 'text-rose-600' : 'text-emerald-600'} font-mono">${c.gap > 0 ? `Gap: -${c.gap}` : 'Aligned'}</span>
          </div>
        `).join('');
      }

      // Curated Courses
      const coursesGrid = document.getElementById('careerCoursesGrid');
      if (coursesGrid) {
        coursesGrid.innerHTML = (data.recommended_courses || []).map(c => `
          <div class="p-3 bg-white border border-slate-200 rounded-lg flex items-center justify-between text-xs shadow-sm">
            <div>
              <strong class="text-slate-900 block">${c.course_title}</strong>
              <span class="text-[11px] text-slate-500">Provider: ${c.provider || 'iGOT Karmayogi'} • ${c.duration_hours || 4}h</span>
            </div>
            <span class="bg-blue-50 text-blue-700 text-[10px] font-semibold px-2.5 py-1 rounded">iGOT Module</span>
          </div>
        `).join('');
      }

      lucide.createIcons();
    } catch (e) {
      console.error('Error loading career roadmap:', e);
      this.showToast('Could not load career path roadmap.', 'error');
    }
  }
  // ==========================================
  // COMMON SYLLABUS
  // ==========================================
  async loadSyllabus() {
    try {
      const res = await fetch(`${API_BASE}/syllabus`);
      if (!res.ok) throw new Error('Failed to load syllabus');
      this.syllabusModules = await res.json();

      // Render Categories Filter
      const cats = ['All', ...new Set(this.syllabusModules.map(m => m.category))];
      const pillsContainer = document.getElementById('syllabusCategoryPills');
      if (pillsContainer) {
        pillsContainer.innerHTML = cats.map((cat, idx) => `
          <button onclick="app.filterSyllabus('${cat}')" class="px-3 py-1 text-xs rounded-full border ${idx === 0 ? 'bg-indigo-600 text-white border-indigo-600 font-semibold' : 'bg-slate-50 text-slate-700 border-slate-300 hover:bg-slate-100'} transition-colors">
            ${cat}
          </button>
        `).join('');
      }

      this.renderSyllabusCards(this.syllabusModules);
      lucide.createIcons();
    } catch (e) {
      console.error('Error loading syllabus:', e);
      this.showToast('Could not load syllabus modules.', 'error');
    }
  }

  filterSyllabus(category) {
    if (category === 'All') {
      this.renderSyllabusCards(this.syllabusModules);
    } else {
      const filtered = this.syllabusModules.filter(m => m.category === category);
      this.renderSyllabusCards(filtered);
    }
  }

  renderSyllabusCards(modules) {
    const grid = document.getElementById('syllabusCardsGrid');
    if (!grid) return;

    grid.innerHTML = modules.map(m => `
      <div onclick="app.selectSyllabusModule('${m.module_id}')" class="border ${this.selectedSyllabusModuleId === m.module_id ? 'border-indigo-500 ring-2 ring-indigo-500/20 bg-indigo-50/20' : 'border-slate-200 bg-white'} p-4 rounded-xl space-y-3 cursor-pointer hover:shadow-md transition-all">
        <div class="flex items-center justify-between">
          <span class="text-[10px] font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded">${m.category}</span>
          <span class="text-[10px] text-slate-500 font-medium">⏱️ ${m.duration_hours} Hours</span>
        </div>
        <h4 class="text-sm font-bold text-slate-900">${m.module_name}</h4>
        <p class="text-xs text-slate-600 leading-relaxed line-clamp-2">${m.description}</p>
        <div class="pt-1 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
          <span>${(m.related_competencies || []).length} Competencies</span>
          <span class="text-indigo-600 font-medium hover:underline">Select for AI Tutor →</span>
        </div>
      </div>
    `).join('');
    lucide.createIcons();
  }

  selectSyllabusModule(moduleId) {
    this.selectedSyllabusModuleId = moduleId;
    this.renderSyllabusCards(this.syllabusModules);
    const mod = this.syllabusModules.find(m => m.module_id === moduleId);
    if (mod) {
      this.showToast(`Selected module: ${mod.module_name} for AI Tutor`, 'info');
    }
  }

  async askSyllabusTutor(queryType) {
    const customText = queryType === 'custom' ? document.getElementById('syllabusCustomInput').value.trim() : null;
    if (queryType === 'custom' && !customText) {
      this.showToast('Please enter your curriculum question.', 'info');
      return;
    }

    const respBox = document.getElementById('syllabusResponseBox');
    const respTitle = document.getElementById('syllabusRespTitle');
    const respContent = document.getElementById('syllabusRespContent');

    respBox.classList.remove('hidden');
    respTitle.textContent = `Tutor analyzing ${queryType.replace('_', ' ')}...`;
    respContent.innerHTML = `<div class="flex items-center space-x-2 text-slate-400 py-2"><i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Retrieving syllabus context & grounding curriculum answer...</span></div>`;
    lucide.createIcons();

    try {
      const res = await fetch(`${API_BASE}/syllabus/tutor`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_id: this.selectedSyllabusModuleId || 'MOD_006',
          query_type: queryType,
          custom_question: customText
        })
      });

      if (!res.ok) throw new Error('Tutor query failed');
      const data = await res.json();

      respTitle.textContent = `Tutor Guidance (${data.response_type.toUpperCase()})`;
      respContent.textContent = data.content;
      document.getElementById('syllabusSourceTag').textContent = `RAG: ${data.rag_source}`;
    } catch (e) {
      console.error('Error querying syllabus tutor:', e);
      respContent.textContent = 'Curriculum guidance currently unavailable. Please review module objectives.';
    }
  }

  // ==========================================
  // AI MOCK TESTS
  // ==========================================
  async loadTestSetup() {
    try {
      const res = await fetch(`${API_BASE}/test/topics`);
      const data = await res.json();
      const topicSelect = document.getElementById('testTopicSelect');
      if (topicSelect && data.topics) {
        topicSelect.innerHTML = data.topics.map(t => `<option value="${t}">${t}</option>`).join('');
      }
    } catch (e) {
      console.error('Failed to load test topics:', e);
    }
  }

  async generateTest() {
    const topic = document.getElementById('testTopicSelect').value;
    const difficulty = document.getElementById('testDifficultySelect').value;
    const count = parseInt(document.getElementById('testCountSelect').value) || 10;

    const genBtn = document.getElementById('generateTestBtn');
    genBtn.disabled = true;
    genBtn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Retrieving & Synthesizing MCQs...</span>`;
    lucide.createIcons();

    try {
      const res = await fetch(`${API_BASE}/test/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.userId,
          topic: topic,
          difficulty: difficulty,
          count: count
        })
      });

      if (!res.ok) throw new Error('Test generation failed');
      const data = await res.json();

      this.activeTest = data;
      this.testQuestions = data.questions;
      this.currentTestIndex = 0;
      this.userAnswers = {};

      document.getElementById('testActiveTopic').textContent = `Topic: ${data.topic}`;
      document.getElementById('testActiveDifficulty').textContent = `Difficulty: ${data.difficulty}`;
      document.getElementById('testRetrievedCount').textContent = `${data.retrieved_count} from Database`;
      document.getElementById('testGeneratedCount').textContent = `${data.generated_count} AI Generated`;

      document.getElementById('testSetupCard').classList.add('hidden');
      document.getElementById('testActiveCard').classList.remove('hidden');
      document.getElementById('testReviewCard').classList.add('hidden');

      this.renderTestQuestion();
      this.showToast(`Generated ${data.total_questions} questions (${data.retrieved_count} DB + ${data.generated_count} Dynamic LLM)!`, 'success');
    } catch (e) {
      console.error('Error generating mock test:', e);
      this.showToast('Could not generate mock assessment.', 'error');
    } finally {
      genBtn.disabled = false;
      genBtn.innerHTML = `<i data-lucide="sparkles" class="w-4 h-4"></i><span>Generate Mock Assessment</span>`;
      lucide.createIcons();
    }
  }

  renderTestQuestion() {
    const q = this.testQuestions[this.currentTestIndex];
    if (!q) return;

    document.getElementById('testProgressCount').textContent = `Q ${this.currentTestIndex + 1} of ${this.testQuestions.length}`;
    document.getElementById('testQuestionText').textContent = q.question_text;

    const srcEl = document.getElementById('testQuestionSource');
    if (q.source_type === 'ai_generated') {
      srcEl.className = 'badge-generated text-[10px] px-2 py-0.5 rounded font-mono font-medium';
      srcEl.textContent = '✨ AI Generated MCQ';
    } else {
      srcEl.className = 'badge-prototype text-[10px] px-2 py-0.5 rounded font-mono font-medium';
      srcEl.textContent = '📚 Prototype Question Bank';
    }

    const optsContainer = document.getElementById('testOptionsContainer');
    const selected = this.userAnswers[q.question_id];

    optsContainer.innerHTML = Object.entries(q.options || {}).map(([key, val]) => `
      <label onclick="app.selectTestOption('${q.question_id}', '${key}')" class="flex items-start p-3 rounded-lg border ${selected === key ? 'border-rose-500 bg-rose-50/40' : 'border-slate-200 hover:bg-slate-50'} cursor-pointer transition-colors text-xs space-x-3">
        <input type="radio" name="testOption" value="${key}" ${selected === key ? 'checked' : ''} class="mt-0.5 text-rose-600 focus:ring-rose-500 cursor-pointer" />
        <span class="flex-1 font-medium text-slate-800"><strong class="font-bold text-slate-900 mr-1">${key}.</strong> ${val}</span>
      </label>
    `).join('');

    document.getElementById('testPrevBtn').disabled = (this.currentTestIndex === 0);
    document.getElementById('testNextBtn').disabled = (this.currentTestIndex === this.testQuestions.length - 1);
    lucide.createIcons();
  }

  selectTestOption(questionId, optionKey) {
    this.userAnswers[questionId] = optionKey;
    this.renderTestQuestion();
  }

  prevTestQuestion() {
    if (this.currentTestIndex > 0) {
      this.currentTestIndex--;
      this.renderTestQuestion();
    }
  }

  nextTestQuestion() {
    if (this.currentTestIndex + 1 < this.testQuestions.length) {
      this.currentTestIndex++;
      this.renderTestQuestion();
    }
  }

  async submitTest() {
    const answeredCount = Object.keys(this.userAnswers).length;
    if (answeredCount < this.testQuestions.length) {
      if (!confirm(`You have answered ${answeredCount} of ${this.testQuestions.length} questions. Submit anyway?`)) {
        return;
      }
    }

    const submitBtn = document.getElementById('testSubmitBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>Grading Assessment...</span>`;
    lucide.createIcons();

    try {
      const res = await fetch(`${API_BASE}/test/${this.activeTest.test_id}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.userId,
          test_id: this.activeTest.test_id,
          answers: this.userAnswers
        })
      });

      if (!res.ok) throw new Error('Submission failed');
      const data = await res.json();

      document.getElementById('testReviewScore').textContent = `${data.score} / ${data.total_questions} (${data.percentage}%)`;
      document.getElementById('testReviewFeedback').textContent = data.ai_feedback;

      const upgBadge = document.getElementById('testCompetencyUpgradeBadge');
      if (data.competency_updated) {
        upgBadge.classList.remove('hidden');
        document.getElementById('testUpgradeText').textContent = `${data.competency_updated.competency_name} Upgraded to Level ${data.competency_updated.current_level}!`;
      } else {
        upgBadge.classList.add('hidden');
      }

      // Render Question Reviews
      const reviewList = document.getElementById('testReviewQuestionsList');
      reviewList.innerHTML = (data.reviews || []).map((r, idx) => `
        <div class="border ${r.is_correct ? 'border-emerald-200 bg-emerald-50/20' : 'border-rose-200 bg-rose-50/20'} p-4 rounded-xl space-y-2 text-xs">
          <div class="flex items-center justify-between">
            <span class="font-bold text-slate-800">Question ${idx + 1}</span>
            <span class="${r.is_correct ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'} px-2 py-0.5 rounded font-bold">
              ${r.is_correct ? '✓ Correct' : '✗ Incorrect'}
            </span>
          </div>
          <p class="font-semibold text-slate-900">${r.question_text}</p>
          <div class="flex flex-wrap gap-4 text-[11px] text-slate-600">
            <span>Your Choice: <strong>${r.user_answer || 'None'}</strong></span>
            <span>Correct Choice: <strong class="text-emerald-700">${r.correct_answer}</strong></span>
          </div>
          <div class="bg-white p-2.5 rounded border border-slate-200 text-[11px] text-slate-700">
            <strong class="text-slate-900 block mb-0.5">Administrative Grounding & Rule Explanation:</strong>
            ${r.explanation}
          </div>
        </div>
      `).join('');

      document.getElementById('testActiveCard').classList.add('hidden');
      document.getElementById('testReviewCard').classList.remove('hidden');
      this.showToast(`Test evaluated! Score: ${data.percentage}%`, 'success');
      lucide.createIcons();
    } catch (e) {
      console.error('Error submitting test:', e);
      this.showToast('Could not submit mock assessment.', 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<i data-lucide="check-circle" class="w-3.5 h-3.5"></i><span>Submit & View Explanations</span>`;
      lucide.createIcons();
    }
  }

  restartTest() {
    document.getElementById('testSetupCard').classList.remove('hidden');
    document.getElementById('testActiveCard').classList.add('hidden');
    document.getElementById('testReviewCard').classList.add('hidden');
  }

  // ==========================================
  // AI PERSONAL MENTOR
  // ==========================================
  sendMentorPreset(text) {
    document.getElementById('mentorInput').value = text;
    this.sendMentorMessage();
  }

  async sendMentorMessage() {
    const input = document.getElementById('mentorInput');
    const msg = input.value.trim();
    if (!msg) return;

    input.value = '';
    const chatStream = document.getElementById('mentorChatStream');

    // Append User Message
    const userDiv = document.createElement('div');
    userDiv.className = 'flex items-start justify-end space-x-2';
    userDiv.innerHTML = `
      <div class="bg-purple-600 text-white rounded-xl p-3.5 text-xs shadow-sm max-w-lg">
        ${msg}
      </div>
    `;
    chatStream.appendChild(userDiv);
    chatStream.scrollTop = chatStream.scrollHeight;

    // Loading Indicator
    const loadDiv = document.createElement('div');
    loadDiv.className = 'flex items-start space-x-3 text-xs text-slate-400';
    loadDiv.id = 'mentorLoadingBubble';
    loadDiv.innerHTML = `
      <div class="w-7 h-7 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-bold text-xs">KY</div>
      <div class="bg-white border border-slate-200 rounded-xl p-3 shadow-sm flex items-center space-x-2">
        <i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin text-purple-600"></i>
        <span>AI Mentor retrieving profile context & formulating coaching guidance...</span>
      </div>
    `;
    chatStream.appendChild(loadDiv);
    chatStream.scrollTop = chatStream.scrollHeight;
    lucide.createIcons();

    try {
      const res = await fetch(`${API_BASE}/mentor/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.userId,
          message: msg
        })
      });

      document.getElementById('mentorLoadingBubble')?.remove();

      if (!res.ok) throw new Error('Mentor chat failed');
      const data = await res.json();

      const aiDiv = document.createElement('div');
      aiDiv.className = 'flex items-start space-x-3';
      aiDiv.innerHTML = `
        <div class="w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold text-xs flex-shrink-0 shadow-sm">KY</div>
        <div class="bg-white border border-slate-200 rounded-xl p-4 text-xs text-slate-700 shadow-sm max-w-2xl space-y-3">
          <div class="font-bold text-purple-900 flex items-center justify-between">
            <span>AI Karmayogi Mentor</span>
            <span class="badge-official text-[10px] px-1.5 py-0.2 rounded font-mono">${(data.rag_sources || ['mentor_guide.md'])[0]}</span>
          </div>
          <p class="leading-relaxed">${data.reply}</p>
          
          ${data.suggested_exercise ? `
            <div class="bg-purple-50 border border-purple-200 p-3 rounded-lg">
              <strong class="text-purple-900 block mb-1">⏱️ 15-Minute Micro-Exercise:</strong>
              <p class="text-purple-950">${data.suggested_exercise}</p>
            </div>
          ` : ''}

          ${data.suggested_actions && data.suggested_actions.length > 0 ? `
            <div class="space-y-1">
              <strong class="text-slate-900 block">Recommended Action Steps:</strong>
              <ul class="list-disc list-inside text-slate-600 space-y-0.5">
                ${data.suggested_actions.map(a => `<li>${a}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
        </div>
      `;
      chatStream.appendChild(aiDiv);
      chatStream.scrollTop = chatStream.scrollHeight;
      lucide.createIcons();
    } catch (e) {
      document.getElementById('mentorLoadingBubble')?.remove();
      console.error('Mentor error:', e);
      this.showToast('Mentor service temporarily unavailable.', 'error');
    }
  }

  // ==========================================
  // PROGRESS PASSPORT
  // ==========================================
  async loadPassport() {
    try {
      const res = await fetch(`${API_BASE}/passport/${this.userId}`);
      if (!res.ok) throw new Error('Failed to load passport');
      const data = await res.json();

      document.getElementById('passUserName').textContent = data.name;
      document.getElementById('passCurrentRole').textContent = data.current_role_id === 'R001' ? 'Section Officer (R001)' : 'Under Secretary (R002)';
      document.getElementById('passTargetRole').textContent = data.target_role_id === 'R002' ? 'Project Officer (R002)' : 'Deputy Secretary (R003)';

      const compsContainer = document.getElementById('passportCompetenciesContainer');
      if (compsContainer) {
        compsContainer.innerHTML = (data.competencies || []).map(c => `
          <div class="p-3 bg-slate-50 border border-slate-200 rounded-lg flex items-center justify-between text-xs">
            <div class="space-y-1">
              <strong class="text-slate-900 block">${c.competency_name}</strong>
              <span class="text-[11px] text-slate-500">${c.competency_type} • Last Assessed: ${c.last_assessed}</span>
            </div>
            <div class="flex items-center space-x-3">
              <div class="flex space-x-1">
                ${[1,2,3,4,5].map(lvl => `
                  <span class="w-5 h-5 rounded-full flex items-center justify-center font-bold text-[10px] ${lvl <= c.current_level ? 'bg-teal-600 text-white' : 'bg-slate-200 text-slate-400'}">${lvl}</span>
                `).join('')}
              </div>
              <span class="font-bold text-slate-700 min-w-[45px] text-right">${c.assessment_score}%</span>
            </div>
          </div>
        `).join('');
      }

      // Test History
      const testList = document.getElementById('passTestHistoryList');
      if (testList) {
        testList.innerHTML = (data.test_history || []).length > 0
          ? data.test_history.map(t => `
            <div class="flex justify-between items-center p-2 bg-white border border-slate-200 rounded text-xs">
              <span class="font-medium text-slate-800">${t.topic}</span>
              <span class="font-bold text-rose-600">${t.score}/${t.total_questions} (${t.percentage}%)</span>
            </div>
          `).join('')
          : `<p class="text-xs text-slate-400 italic">No previous test history.</p>`;
      }

      // Interview History
      const intList = document.getElementById('passInterviewHistoryList');
      if (intList) {
        intList.innerHTML = (data.interview_history || []).length > 0
          ? data.interview_history.map(i => `
            <div class="flex justify-between items-center p-2 bg-white border border-slate-200 rounded text-xs">
              <span class="font-medium text-slate-800 truncate max-w-[200px]">${i.feedback || 'Completed Session'}</span>
              <span class="font-bold text-blue-600">${i.overall_score} / 5.0</span>
            </div>
          `).join('')
          : `<p class="text-xs text-slate-400 italic">No previous interview history.</p>`;
      }

      lucide.createIcons();
    } catch (e) {
      console.error('Error loading passport:', e);
      this.showToast('Could not load competency progress passport.', 'error');
    }
  }

  async resetUserProgress() {
    if (!confirm(`Reset demo competency scores and progress for ${this.userId} back to initial baseline?`)) return;

    try {
      const res = await fetch(`${API_BASE}/passport/${this.userId}/reset`, { method: 'POST' });
      if (!res.ok) throw new Error('Reset failed');
      const data = await res.json();
      this.showToast(data.message, 'success');
      this.refreshCurrentTab();
    } catch (e) {
      console.error('Error resetting progress:', e);
      this.showToast('Could not reset demo progress.', 'error');
    }
  }

  // ==========================================
  // EXPLAINABILITY MODAL
  // ==========================================
  async explainRecommendation(recId) {
    try {
      const res = await fetch(`${API_BASE}/recommendations/explain?user_id=${this.userId}&recommendation_id=${recId}`, { method: 'POST' });
      if (!res.ok) throw new Error('Explain failed');
      const data = await res.json();

      document.getElementById('explainGapText').textContent = `Current Level ${data.current_level} → Target Level ${data.target_level} (Calculated Gap: ${data.gap})`;
      document.getElementById('explainSourceBadge').textContent = data.source_category || 'Verified Reference';
      document.getElementById('explainEvidenceList').innerHTML = (data.evidence || []).map(e => `<li>${e}</li>`).join('');
      document.getElementById('explainOutcomeText').textContent = data.expected_outcome;

      document.getElementById('explainModal').classList.remove('hidden');
      lucide.createIcons();
    } catch (e) {
      console.error('Error explaining recommendation:', e);
      this.showToast('Could not retrieve recommendation evidence.', 'error');
    }
  }

  closeExplainModal() {
    document.getElementById('explainModal').classList.add('hidden');
  }
}

// Instantiate global app instance
const app = new KarmayogiApp();
