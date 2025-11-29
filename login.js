// login.js
// Script dedicated to handling the login page logic.

import { sendRequest } from './api.js';
import { showMessage } from './ui.js';

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const usernameInput = document.getElementById('login-username');
    const passwordInput = document.getElementById('login-password');

    // ถ้าผู้ใช้เคยล็อกอินค้างไว้ ให้ redirect ไปหน้าเลือกเมนูทันที
    try {
        const currentUser = JSON.parse(localStorage.getItem('currentUser'));
        if (currentUser) {
            window.location.href = '/selection.html';
            return;
        }
    } catch (e) {
        localStorage.removeItem('currentUser');
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = usernameInput.value.trim();
            const password = passwordInput.value.trim();

            if (!username || !password) {
                showMessage('กรุณากรอกชื่อผู้ใช้และรหัสผ่าน', false);
                return;
            }

            try {
                // ปิดปุ่มระหว่างรอ เพื่อป้องกันการกดซ้ำ
                const submitBtn = loginForm.querySelector('button[type="submit"]');
                const originalBtnText = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span>กำลังเข้าสู่ระบบ...</span>';

                const response = await sendRequest('login', { username, password });

                if (response.status === 'success') {
                    // บันทึกข้อมูลผู้ใช้ลง Local Storage
                    localStorage.setItem('currentUser', JSON.stringify(response.user));
                    
                    // Redirect ไปยังหน้าเลือกเมนู (Selection Page)
                    // ไม่ว่าจะ role ไหน ก็ให้ไปหน้าเลือกเมนูก่อนเสมอ
                    window.location.href = '/selection.html';
                } else {
                    // แสดงข้อความแจ้งเตือนที่ได้จาก Backend (เช่น รหัสผิด, ถูกล็อก)
                    showMessage(response.message, false);
                }
                
                // คืนค่าปุ่มกลับสู่สภาพเดิม
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;

            } catch (error) {
                console.error('Login error:', error);
                showMessage('เกิดข้อผิดพลาดในการเชื่อมต่อระบบ', false);
                
                // คืนค่าปุ่มกรณี Error
                const submitBtn = loginForm.querySelector('button[type="submit"]');
                submitBtn.disabled = false;
                submitBtn.innerHTML = `
                    <span>เข้าสู่ระบบ</span>
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M3 3a1 1 0 011 1v12a1 1 0 11-2 0V4a1 1 0 011-1zm7.707 3.293a1 1 0 010 1.414L9.414 9H17a1 1 0 110 2H9.414l1.293 1.293a1 1 0 01-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>`;
            }
        });
    }
});