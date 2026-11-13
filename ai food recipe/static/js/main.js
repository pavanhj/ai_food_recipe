/**
 * AI Food Recipe Preparation & Recommendation System
 * Frontend Interactions & Features
 */

document.addEventListener('DOMContentLoaded', () => {
    initFavouriteButtons();
    initIngredientCheckboxes();
    initCookingTimer();
    initCopyIngredients();
    initDemoCredentials();
});

// ========================================================
// 1. AJAX Favourite Toggle Button
// ========================================================
function initFavouriteButtons() {
    const favButtons = document.querySelectorAll('.card-fav-btn, .recipe-fav-btn');
    favButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();

            const recipeId = btn.getAttribute('data-recipe-id');
            if (!recipeId) return;

            try {
                const response = await fetch(`/favourite/toggle/${recipeId}`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json'
                    }
                });

                if (response.redirected) {
                    window.location.href = response.url;
                    return;
                }

                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        const icon = btn.querySelector('i');
                        if (data.is_favourite) {
                            btn.classList.add('active');
                            if (icon) {
                                icon.classList.remove('fa-regular');
                                icon.classList.add('fa-solid');
                            }
                            showToast(data.message || 'Added to favourites!', 'success');
                        } else {
                            btn.classList.remove('active');
                            if (icon) {
                                icon.classList.remove('fa-solid');
                                icon.classList.add('fa-regular');
                            }
                            showToast(data.message || 'Removed from favourites.', 'info');
                        }
                    }
                } else if (response.status === 401 || response.status === 302) {
                    window.location.href = '/login';
                }
            } catch (err) {
                console.error('Favourite toggle error:', err);
            }
        });
    });
}

// ========================================================
// 2. Interactive Ingredients Checklist
// ========================================================
function initIngredientCheckboxes() {
    const ingredientItems = document.querySelectorAll('.ingredient-item');
    ingredientItems.forEach(item => {
        const checkbox = item.querySelector('.ingredient-checkbox');
        const text = item.querySelector('.ingredient-text');

        if (checkbox) {
            checkbox.addEventListener('change', () => {
                if (checkbox.checked) {
                    item.classList.add('checked');
                } else {
                    item.classList.remove('checked');
                }
            });
        }

        if (text && checkbox) {
            text.addEventListener('click', () => {
                checkbox.checked = !checkbox.checked;
                checkbox.dispatchEvent(new Event('change'));
            });
        }
    });

    // Select all / Deselect all
    const selectAllBtn = document.getElementById('btnSelectAllIngredients');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
            const checkboxes = document.querySelectorAll('.ingredient-checkbox');
            const allChecked = Array.from(checkboxes).every(cb => cb.checked);
            checkboxes.forEach(cb => {
                cb.checked = !allChecked;
                cb.dispatchEvent(new Event('change'));
            });
            selectAllBtn.innerHTML = allChecked 
                ? '<i class="fa-regular fa-square-check me-1"></i> Check All' 
                : '<i class="fa-regular fa-square me-1"></i> Uncheck All';
        });
    }
}

// ========================================================
// 3. One-Click Copy Ingredients to Clipboard
// ========================================================
function initCopyIngredients() {
    const copyBtn = document.getElementById('btnCopyIngredients');
    if (!copyBtn) return;

    copyBtn.addEventListener('click', () => {
        const textNodes = document.querySelectorAll('.ingredient-text');
        const ingredients = Array.from(textNodes).map(node => `• ${node.innerText.trim()}`).join('\n');
        
        const recipeTitle = document.querySelector('h1')?.innerText || 'Recipe';
        const clipboardContent = `Ingredients for ${recipeTitle}:\n\n${ingredients}\n\nGenerated by AI Food Recipe Preparation System`;

        navigator.clipboard.writeText(clipboardContent).then(() => {
            const originalHTML = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fa-solid fa-check text-success me-1"></i> Copied to Clipboard!';
            copyBtn.classList.add('btn-outline-success');
            copyBtn.classList.remove('btn-outline-secondary');
            setTimeout(() => {
                copyBtn.innerHTML = originalHTML;
                copyBtn.classList.remove('btn-outline-success');
                copyBtn.classList.add('btn-outline-secondary');
            }, 2500);
        }).catch(err => {
            console.error('Clipboard copy failed:', err);
        });
    });
}

// ========================================================
// 4. Kitchen Cooking Timer with Audio Chime
// ========================================================
let timerInterval = null;
let timerSeconds = 0;
let isTimerRunning = false;

function initCookingTimer() {
    const timerDisplay = document.getElementById('timerCountdownDisplay');
    const startBtn = document.getElementById('btnTimerStart');
    const pauseBtn = document.getElementById('btnTimerPause');
    const resetBtn = document.getElementById('btnTimerReset');
    const addMinBtn = document.getElementById('btnTimerAddMin');
    const presetPills = document.querySelectorAll('.timer-preset-btn');

    if (!timerDisplay) return;

    // Default time from modal data attribute
    const defaultMinutes = parseInt(timerDisplay.getAttribute('data-default-minutes') || '20', 10);
    timerSeconds = defaultMinutes * 60;
    updateDisplay();

    presetPills.forEach(pill => {
        pill.addEventListener('click', () => {
            const mins = parseInt(pill.getAttribute('data-minutes') || '10', 10);
            pauseTimer();
            timerSeconds = mins * 60;
            updateDisplay();
        });
    });

    if (startBtn) {
        startBtn.addEventListener('click', () => {
            if (!isTimerRunning && timerSeconds > 0) {
                isTimerRunning = true;
                startBtn.disabled = true;
                if (pauseBtn) pauseBtn.disabled = false;
                timerInterval = setInterval(() => {
                    if (timerSeconds > 0) {
                        timerSeconds--;
                        updateDisplay();
                    } else {
                        pauseTimer();
                        playAlarmChime();
                        alert('🍳 Cooking Time Completed! Your dish is ready to enjoy.');
                    }
                }, 1000);
            }
        });
    }

    if (pauseBtn) {
        pauseBtn.addEventListener('click', pauseTimer);
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            pauseTimer();
            timerSeconds = defaultMinutes * 60;
            updateDisplay();
        });
    }

    if (addMinBtn) {
        addMinBtn.addEventListener('click', () => {
            timerSeconds += 60;
            updateDisplay();
        });
    }

    function pauseTimer() {
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
        isTimerRunning = false;
        if (startBtn) startBtn.disabled = false;
        if (pauseBtn) pauseBtn.disabled = true;
    }

    function updateDisplay() {
        const m = Math.floor(timerSeconds / 60);
        const s = timerSeconds % 60;
        timerDisplay.textContent = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }
}

// Web Audio API Synthesizer Chime (Zero external mp3 files needed)
function playAlarmChime() {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const now = audioCtx.currentTime;

        const osc1 = audioCtx.createOscillator();
        const gain1 = audioCtx.createGain();
        osc1.type = 'sine';
        osc1.frequency.setValueAtTime(587.33, now); // D5
        osc1.frequency.setValueAtTime(880.00, now + 0.2); // A5
        gain1.gain.setValueAtTime(0.3, now);
        gain1.gain.exponentialRampToValueAtTime(0.001, now + 1.2);
        osc1.connect(gain1);
        gain1.connect(audioCtx.destination);
        osc1.start(now);
        osc1.stop(now + 1.2);
    } catch (e) {
        console.log('Audio chime not supported');
    }
}

// ========================================================
// 5. Toast Notification Helper
// ========================================================
function showToast(message, type = 'info') {
    let toastContainer = document.getElementById('liveToastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'liveToastContainer';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '1100';
        document.body.appendChild(toastContainer);
    }

    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-bg-${type === 'danger' ? 'danger' : (type === 'success' ? 'success' : 'dark')} border-0 shadow-lg`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body fw-semibold">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    toastContainer.appendChild(toastEl);
    const bsToast = new bootstrap.Toast(toastEl, { delay: 3000 });
    bsToast.show();
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}

// ========================================================
// 6. Autofill Demo Credentials for Viva / Quick Testing
// ========================================================
function initDemoCredentials() {
    const demoFillBtn = document.getElementById('btnFillDemo');
    if (demoFillBtn) {
        demoFillBtn.addEventListener('click', () => {
            const emailInput = document.getElementById('email');
            const passwordInput = document.getElementById('password');
            if (emailInput && passwordInput) {
                emailInput.value = 'demo@recipeai.com';
                passwordInput.value = 'password123';
                showToast('Demo credentials filled!', 'info');
            }
        });
    }
}
