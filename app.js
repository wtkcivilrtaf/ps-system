// app.js
// Main application file for initialization and state management.

import { sendRequest } from './api.js';
import * as ui from './ui.js';
import * as handlers from './handlers.js';
import { escapeHTML, exportSingleReportToExcel } from './utils.js';

// --- Global State and DOM References ---
window.currentUser = null;
window.currentWeeklyReports = [];
window.allArchivedReports = {};
window.allHistoryData = {};
window.personnelCurrentPage = 1;
window.userCurrentPage = 1;
window.holidayDatepicker = null; 

// --- Auto Logout Feature ---
let inactivityTimer;
const INACTIVITY_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes

function performLogout() {
    clearTimeout(inactivityTimer);
    sendRequest('logout', {}).finally(() => {
        localStorage.removeItem('currentUser');
        window.location.href = '/login.html';
    });
}

function autoLogoutUser() {
    alert("คุณไม่มีการใช้งานเป็นเวลานาน ระบบจะทำการออกจากระบบเพื่อความปลอดภัย");
    performLogout();
}

function resetInactivityTimer() {
    clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(autoLogoutUser, INACTIVITY_TIMEOUT_MS);
}

// DOM Elements
window.appContainer = null;
window.messageArea = null;
window.welcomeMessage = null;
window.logoutBtn = null;
window.tabs = null;
window.panes = null;
window.statusSubmissionListArea = null;
window.submitStatusTitle = null;
window.submissionFormSection = null;
window.reviewReportSection = null;
window.reviewListArea = null;
window.backToFormBtn = null;
window.confirmSubmitBtn = null;
window.reviewStatusBtn = null;
window.reportContainer = null;
window.exportArchiveBtn = null;
window.archiveContainer = null;
window.archiveYearSelect = null;
window.archiveMonthSelect = null;
window.showArchiveBtn = null;
window.archiveConfirmModal = null;
window.cancelArchiveBtn = null;
window.confirmArchiveBtn = null;
window.personnelListArea = null;
window.addPersonnelBtn = null;
window.personnelModal = null;
window.personnelForm = null;
window.cancelPersonnelBtn = null;
window.importExcelBtn = null;
window.excelImportInput = null;
window.userListArea = null;
window.addUserBtn = null;
window.userModal = null;
window.userForm = null;
window.cancelUserBtn = null;
window.userModalTitle = null;
window.personnelSearchInput = null;
window.personnelSearchBtn = null;
window.userSearchInput = null;
window.userSearchBtn = null;
window.historyContainer = null;
window.historyYearSelect = null;
window.historyMonthSelect = null;
window.showHistoryBtn = null;
window.activeStatusesContainer = null;
window.mainNav = null;
window.mainTitle = null;
window.holidayForm = null;
window.holidayListContainer = null;
window.submitAllBtn = null;

// --- Main Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    assignDomElements();
    
    try {
        window.currentUser = JSON.parse(localStorage.getItem('currentUser'));
    } catch (e) {
        window.currentUser = null;
    }

    if (!window.currentUser) {
        localStorage.removeItem('currentUser');
        window.location.href = '/login.html';
        return;
    }
    
    ui.populateRankDropdowns();
    initializePage();
});

function assignDomElements() {
    window.appContainer = document.getElementById('app-container');
    window.messageArea = document.getElementById('message-area');
    window.welcomeMessage = document.getElementById('welcome-message');
    window.logoutBtn = document.getElementById('logout-btn');
    window.tabs = document.querySelectorAll('.tab-button');
    window.panes = document.querySelectorAll('.tab-pane');
    window.statusSubmissionListArea = document.getElementById('status-submission-list-area');
    window.submitStatusTitle = document.getElementById('submit-status-title');
    window.submissionFormSection = document.getElementById('submission-form-section');
    window.reviewReportSection = document.getElementById('review-report-section');
    window.reviewListArea = document.getElementById('review-list-area');
    window.backToFormBtn = document.getElementById('back-to-form-btn');
    window.confirmSubmitBtn = document.getElementById('confirm-submit-btn');
    window.reviewStatusBtn = document.getElementById('review-status-btn');
    window.reportContainer = document.getElementById('report-container');
    window.exportArchiveBtn = document.getElementById('export-archive-btn');
    window.archiveContainer = document.getElementById('archive-container');
    window.archiveYearSelect = document.getElementById('archive-year-select');
    window.archiveMonthSelect = document.getElementById('archive-month-select');
    window.showArchiveBtn = document.getElementById('show-archive-btn');
    window.archiveConfirmModal = document.getElementById('archive-confirm-modal');
    window.cancelArchiveBtn = document.getElementById('cancel-archive-btn');
    window.confirmArchiveBtn = document.getElementById('confirm-archive-btn');
    window.personnelListArea = document.getElementById('personnel-list-area');
    window.addPersonnelBtn = document.getElementById('add-personnel-btn');
    window.personnelModal = document.getElementById('personnel-modal');
    window.personnelForm = document.getElementById('personnel-form');
    window.cancelPersonnelBtn = document.getElementById('cancel-personnel-btn');
    window.importExcelBtn = document.getElementById('import-excel-btn');
    window.excelImportInput = document.getElementById('excel-import-input');
    window.userListArea = document.getElementById('user-list-area');
    window.addUserBtn = document.getElementById('add-user-btn');
    window.userModal = document.getElementById('user-modal');
    window.userForm = document.getElementById('user-form');
    window.cancelUserBtn = document.getElementById('cancel-user-btn');
    window.userModalTitle = document.getElementById('user-modal-title');
    window.personnelSearchInput = document.getElementById('personnel-search-input');
    window.personnelSearchBtn = document.getElementById('personnel-search-btn');
    window.userSearchInput = document.getElementById('user-search-input');
    window.userSearchBtn = document.getElementById('user-search-btn');
    window.historyContainer = document.getElementById('history-container');
    window.historyYearSelect = document.getElementById('history-year-select');
    window.historyMonthSelect = document.getElementById('history-month-select');
    window.showHistoryBtn = document.getElementById('show-history-btn');
    window.activeStatusesContainer = document.getElementById('active-statuses-container');
    window.mainNav = document.getElementById('main-nav');
    window.mainTitle = document.getElementById('main-title');
    window.holidayForm = document.getElementById('holiday-form');
    window.holidayListContainer = document.getElementById('holiday-list-container');
    window.submitAllBtn = document.getElementById('submit-all-btn');
}


function initializePage() {
    appContainer.classList.remove('hidden');
    const userRole = currentUser.role;
    welcomeMessage.textContent = `ล็อกอินในฐานะ: ${escapeHTML(currentUser.username)} (${escapeHTML(userRole)})`;
    const backToSelectionBtn = document.getElementById('back-to-selection-btn');
    if (backToSelectionBtn) {
        backToSelectionBtn.addEventListener('click', () => {
            window.location.href = '/selection.html';
        });
    }

    const is_admin = (userRole === 'admin');
    
    const urlParams = new URLSearchParams(window.location.search);
    const view = urlParams.get('view');

    if (is_admin && view) {
        mainNav.classList.add('hidden');
        panes.forEach(pane => pane.classList.add('hidden'));

        let targetPaneId, titleText;
        if (view === 'personnel') {
            targetPaneId = 'pane-personnel';
            titleText = 'จัดการกำลังพล';
        } else if (view === 'users') {
            targetPaneId = 'pane-admin';
            titleText = 'จัดการผู้ใช้';
        } else if (view === 'holidays') {
            targetPaneId = 'pane-holidays';
            titleText = 'จัดการวันหยุด';
        }

        if (targetPaneId) {
            mainTitle.textContent = titleText;
            const targetPane = document.getElementById(targetPaneId);
            if (targetPane) {
                targetPane.classList.remove('hidden');
                loadDataForPane(targetPaneId);
            }
        }
    } else {
        mainNav.classList.remove('hidden');
        mainTitle.textContent = 'ระบบรายงานยอดกำลังพลประจำสัปดาห์';
        
        document.getElementById('tab-dashboard').classList.toggle('hidden', !is_admin);
        document.getElementById('tab-active-statuses').classList.remove('hidden');
        document.getElementById('tab-submit-status').classList.remove('hidden');
        document.getElementById('tab-history').classList.remove('hidden');
        document.getElementById('tab-report').classList.toggle('hidden', !is_admin);
        document.getElementById('tab-archive').classList.toggle('hidden', !is_admin);
        
        if (is_admin) {
            switchTab('tab-dashboard');
        } else {
            switchTab('tab-active-statuses');
        }
    }

    logoutBtn.addEventListener('click', () => performLogout());

    window.addEventListener('mousemove', resetInactivityTimer);
    window.addEventListener('keydown', resetInactivityTimer);
    window.addEventListener('click', resetInactivityTimer);
    resetInactivityTimer();

    tabs.forEach(tab => tab.addEventListener('click', () => switchTab(tab.id)));
    if(addPersonnelBtn) addPersonnelBtn.addEventListener('click', () => ui.openPersonnelModal());
    if(cancelPersonnelBtn) cancelPersonnelBtn.addEventListener('click', () => personnelModal.classList.remove('active'));
    if(personnelForm) personnelForm.addEventListener('submit', handlers.handlePersonnelFormSubmit);
    if(personnelListArea) personnelListArea.addEventListener('click', handlers.handlePersonnelListClick);
    if(addUserBtn) addUserBtn.addEventListener('click', () => ui.openUserModal());
    if(cancelUserBtn) cancelUserBtn.addEventListener('click', () => userModal.classList.remove('active'));
    if(userForm) userForm.addEventListener('submit', handlers.handleUserFormSubmit);
    if(userListArea) userListArea.addEventListener('click', handlers.handleUserListClick);
    if(importExcelBtn) importExcelBtn.addEventListener('click', () => excelImportInput.click());
    if(excelImportInput) excelImportInput.addEventListener('change', handlers.handleExcelImport);
    if (reviewStatusBtn) reviewStatusBtn.addEventListener('click', handlers.handleReviewStatus);
    if (backToFormBtn) backToFormBtn.addEventListener('click', () => {
        reviewReportSection.classList.add('hidden');
        submissionFormSection.classList.remove('hidden');
    });
    if (confirmSubmitBtn) confirmSubmitBtn.addEventListener('click', handlers.handleSubmitStatusReport);
    
    // หมายเหตุ: Logic ของ exportArchiveBtn ถูกย้ายไปจัดการใน loadDataForPane ('pane-report')
    // เพื่อให้สามารถตรวจสอบ Missing Count และเปลี่ยนสถานะปุ่มได้อย่างถูกต้องแบบ Realtime

    if (cancelArchiveBtn) cancelArchiveBtn.addEventListener('click', () => archiveConfirmModal.classList.remove('active'));
    if (confirmArchiveBtn) confirmArchiveBtn.addEventListener('click', handlers.handleExportAndArchive);
    
    if (showArchiveBtn) showArchiveBtn.addEventListener('click', handlers.handleShowArchive);
    if (archiveContainer) archiveContainer.addEventListener('click', handlers.handleArchiveDownloadClick);
    
    if (personnelSearchBtn) {
        const searchPersonnel = () => {
            window.personnelCurrentPage = 1;
            loadDataForPane('pane-personnel');
        };
        personnelSearchBtn.addEventListener('click', searchPersonnel);
        personnelSearchInput.addEventListener('keyup', (e) => { if (e.key === 'Enter') searchPersonnel(); });
    }
    if (userSearchBtn) {
        const searchUser = () => {
            window.userCurrentPage = 1;
            loadDataForPane('pane-admin');
        };
        userSearchBtn.addEventListener('click', searchUser);
        userSearchInput.addEventListener('keyup', (e) => { if (e.key === 'Enter') searchUser(); });
    }
    
    if (archiveYearSelect) {
        archiveYearSelect.addEventListener('change', () => {
            const selectedYear = archiveYearSelect.value;
            archiveMonthSelect.innerHTML = '<option value="">เลือกเดือน</option>';
            if (selectedYear && allArchivedReports[selectedYear]) {
                const sortedMonths = Object.keys(allArchivedReports[selectedYear]).sort((a, b) => b - a);
                sortedMonths.forEach(month => {
                    const option = document.createElement('option');
                    option.value = month;
                    option.textContent = new Date(2000, parseInt(month) - 1, 1).toLocaleString('th-TH', { month: 'long' });
                    archiveMonthSelect.appendChild(option);
                });
            }
        });
    }

    if (showHistoryBtn) showHistoryBtn.addEventListener('click', handlers.handleShowHistory);
    
    if (historyYearSelect) {
        historyYearSelect.addEventListener('change', () => {
            const selectedYear = historyYearSelect.value;
            historyMonthSelect.innerHTML = '<option value="">เลือกเดือน</option>';
            if (selectedYear && window.allHistoryData[selectedYear]) {
                const sortedMonths = Object.keys(window.allHistoryData[selectedYear]).sort((a, b) => b - a);
                sortedMonths.forEach(month => {
                    const option = document.createElement('option');
                    option.value = month;
                    option.textContent = new Date(2000, parseInt(month) - 1, 1).toLocaleString('th-TH', { month: 'long' });
                    historyMonthSelect.appendChild(option);
                });
            }
        });
    }

    if(historyContainer) historyContainer.addEventListener('click', handlers.handleHistoryEditClick);
    if(reportContainer) reportContainer.addEventListener('click', handlers.handleWeeklyReportEditClick);

    if (statusSubmissionListArea) {
        statusSubmissionListArea.addEventListener('click', function(e) {
            if (e.target && e.target.classList.contains('add-status-btn')) {
                ui.addStatusRow(e.target);
            }
            if (e.target && e.target.classList.contains('remove-status-btn')) {
                const subRow = e.target.closest('tr');
                if (subRow) {
                    subRow.remove();
                }
            }
        });
    }

    if (window.submitAllBtn) {
        window.submitAllBtn.style.display = 'none'; 
    }

    if (holidayForm) {
        window.holidayDatepicker = flatpickr("#holiday-date", {
            locale: ui.thai_locale,
            altInput: true,
            altFormat: "j F Y",
            dateFormat: "Y-m-d",
        });
        holidayForm.addEventListener('submit', handlers.handleAddHoliday);
    }
    if (holidayListContainer) {
        holidayListContainer.addEventListener('click', handlers.handleDeleteHoliday);
    }
}

// --- Data Loading and Tab Switching ---
window.loadDataForPane = async function(paneId) {
    let payload = {};
    const actions = {
        'pane-dashboard': { action: 'get_dashboard_summary', renderer: ui.renderDashboard },
        'pane-active-statuses': { action: 'get_active_statuses', renderer: ui.renderActiveStatuses },
        'pane-personnel': { action: 'list_personnel', renderer: ui.renderPersonnel, searchInput: personnelSearchInput, pageState: 'personnelCurrentPage' },
        'pane-admin': { action: 'list_users', renderer: ui.renderUsers, searchInput: userSearchInput, pageState: 'userCurrentPage' },
        'pane-submit-status': { action: 'list_personnel', renderer: ui.renderStatusSubmissionForm, fetchAll: true },
        'pane-history': { action: 'get_submission_history', renderer: ui.renderSubmissionHistory },
        
        // --- [UPDATED] 2-Step Button Logic ---
        'pane-report': { 
            action: 'get_status_reports', 
            renderer: (res) => {
                ui.renderWeeklyReport(res);

                if (window.currentUser && window.currentUser.role === 'admin') {
                    let btn = document.getElementById('export-archive-btn');
                    if (btn) {
                        // 1. Reset ปุ่มโดยการ Clone (ลบ Event Listener เก่าออกทั้งหมด)
                        const newBtn = btn.cloneNode(true);
                        btn.parentNode.replaceChild(newBtn, btn);
                        btn = newBtn; 

                        btn.disabled = false;
                        btn.classList.remove('bg-gray-400', 'cursor-not-allowed');
                        
                        const allDepts = res.all_departments || [];
                        const submittedDepts = res.submitted_departments || [];
                        const missingCount = allDepts.length - submittedDepts.length;

                        if (missingCount > 0) {
                            // --- สถานะที่ 1: ยังส่งไม่ครบ -> ปุ่มเป็น "Submit All" ---
                            btn.className = 'bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded-lg shadow-md transition-all duration-200';
                            btn.innerHTML = `⚡ ดึงยอดทุกแผนก (${missingCount} ขาด)`;
                            btn.title = 'คลิกเพื่อดึงยอดล่าสุดของแผนกที่ยังไม่ส่งให้ครบ';
                            
                            btn.addEventListener('click', async () => {
                                if (!confirm(`มี ${missingCount} แผนกยังไม่ส่งยอด\nยืนยันการ "ดึงยอดปัจจุบัน" ของทุกแผนกมาบันทึกทันทีหรือไม่?`)) return;
                                
                                try {
                                    btn.disabled = true;
                                    btn.textContent = 'กำลังประมวลผล...';
                                    const submitRes = await sendRequest('submit_all_status_reports', {});
                                    
                                    if (submitRes.status === 'success') {
                                        ui.showMessage('ดึงยอดครบทุกแผนกแล้ว (แดชบอร์ดเป็นสีเขียว)', true);
                                        loadDataForPane('pane-report'); // รีโหลดหน้าจอ ปุ่มจะเปลี่ยนเป็นสถานะ 2
                                    } else {
                                        ui.showMessage(submitRes.message, false);
                                        btn.disabled = false;
                                        btn.innerHTML = `⚡ ดึงยอดทุกแผนก (${missingCount} ขาด)`;
                                    }
                                } catch(e) {
                                    ui.showMessage(e.message, false);
                                    btn.disabled = false;
                                    btn.innerHTML = `⚡ ดึงยอดทุกแผนก (${missingCount} ขาด)`;
                                }
                            });

                        } else {
                            // --- สถานะที่ 2: ครบแล้ว -> ปุ่มเป็น "Export & Archive" ---
                            btn.className = 'bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg shadow-md transition-all duration-200';
                            btn.innerHTML = 'ส่งออกและเก็บรายงาน';
                            btn.title = 'ข้อมูลครบถ้วน พร้อมส่งออกไฟล์ Excel และเก็บเข้า Archive';

                            btn.addEventListener('click', async () => {
                                if (!confirm('ยอดครบทุกแผนกแล้ว\nยืนยันการ "ส่งออกไฟล์ Excel" และ "เก็บรายงานเข้า Archive" หรือไม่?')) return;
                                
                                try {
                                    btn.disabled = true;
                                    btn.textContent = 'กำลังส่งออก...';
                                    
                                    // 1. ดึงข้อมูลรายงาน
                                    const reportsRes = await sendRequest('get_status_reports', {});
                                    
                                    // 2. สร้างไฟล์ Excel
                                    try {
                                        exportSingleReportToExcel(reportsRes.reports, `รายงานประจำสัปดาห์-${reportsRes.weekly_date_range}.xlsx`, reportsRes.weekly_date_range);
                                    } catch (ex) { console.error(ex); alert('สร้างไฟล์ Excel ไม่สำเร็จ'); }

                                    // 3. สั่ง Archive
                                    const archiveRes = await sendRequest('archive_reports', {
                                        reports: reportsRes.reports,
                                        week_range: reportsRes.weekly_date_range
                                    });

                                    if (archiveRes.status === 'success') {
                                        ui.showMessage('เก็บรายงานเรียบร้อยแล้ว', true);
                                        loadDataForPane('pane-dashboard'); // กลับไปหน้า Dashboard
                                        document.getElementById('report-container').innerHTML = ''; // ล้างหน้า Report
                                    } else {
                                        ui.showMessage(archiveRes.message, false);
                                    }
                                } catch(e) {
                                    ui.showMessage(e.message, false);
                                } finally {
                                    btn.disabled = false;
                                    btn.textContent = 'ส่งออกและเก็บรายงาน';
                                }
                            });
                        }
                    }
                }
            } 
        },
        // -------------------------------------------------------------

        'pane-archive': { action: 'get_archived_reports', renderer: (res) => {
            const archives = res.archives;
            window.allArchivedReports = archives || {};
            ui.populateArchiveSelectors(window.allArchivedReports);
            if(window.archiveContainer) window.archiveContainer.innerHTML = '';
        }},
        'pane-holidays': { action: 'list_holidays', renderer: handlers.renderHolidays }
    };

    const paneConfig = actions[paneId];
    if (!paneConfig) {
        console.error("No config for pane:", paneId);
        return;
    };

    if (paneConfig.searchInput) {
        payload.searchTerm = paneConfig.searchInput.value;
    }
    if (paneConfig.pageState) {
        payload.page = window[paneConfig.pageState];
    }
    if (paneConfig.fetchAll) {
        payload.fetchAll = true;
    }

    if (paneId === 'pane-submit-status' && window.currentUser.role === 'admin') {
        const deptSelector = document.getElementById('admin-dept-selector');
        if (deptSelector && deptSelector.value) {
            payload.department = deptSelector.value;
        }
    }

    try {
        const res = await sendRequest(paneConfig.action, payload);
        if (res && res.status === 'success') {
            if (paneConfig.renderer) {
                paneConfig.renderer(res);
            }
        } else if (res && res.message) {
            ui.showMessage(res.message, false);
        }
    } catch (error) {
        ui.showMessage(error.message, false);
    }
}

window.switchTab = function(tabId) {
    tabs.forEach(tab => {
        const paneId = tab.id.replace('tab-', 'pane-');
        const pane = document.getElementById(paneId);
        if(!pane) return;
        if (tab.id === tabId) {
            tab.classList.add('active');
            pane.classList.remove('hidden');
            if (paneId === 'pane-personnel') window.personnelCurrentPage = 1;
            if (paneId === 'pane-admin') window.userCurrentPage = 1;
            loadDataForPane(paneId);
        } else {
            tab.classList.remove('active');
            pane.classList.add('hidden');
        }
    });
}