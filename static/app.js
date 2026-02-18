// Telegram Web App initialization
let tg = window.Telegram?.WebApp;
if (tg) {
    tg.expand();
    tg.ready();
}

// Global variables
let calculationResults = [];
let chart = null;

// DOM elements
const form = document.getElementById('calculatorForm');
const formCard = document.getElementById('formCard');
const editDataContainer = document.getElementById('editDataContainer');
const editDataBtn = document.getElementById('editDataBtn');

const loadingOverlay = document.getElementById('loadingOverlay');
const resultsSection = document.getElementById('resultsSection');
const resultsTableBody = document.getElementById('resultsTableBody');
const summaryContent = document.getElementById('summaryContent');

const toggleTableBtn = document.getElementById('toggleTableBtn');
const tableContainer = document.getElementById('tableContainer');

const retirementModeRadios = document.getElementsByName('retirement_mode');
const retirementAgeInput = document.getElementById('retirementAge');
const retirementAgeGroup = document.getElementById('retirementAgeGroup');

const advancedToggle = document.getElementById('advancedToggle');
const advancedContent = document.getElementById('advancedContent');

const infoTrigger = document.querySelector('.info-trigger');
const interestTooltip = document.getElementById('interestTooltip');

const inflationTrigger = document.querySelector('.info-trigger-inflation');
const inflationTooltip = document.getElementById('inflationTooltip');

const resetBtn = document.getElementById('resetBtn');

const promoLinks = {
    youtube: 'https://youtube.com', // Placeholder, user will provide later
    freedom: 'https://freedom24.com/invite_from/7446576'
};

// Load saved data on startup
document.addEventListener('DOMContentLoaded', () => {
    loadSavedData();
    updateRetirementModeUI();

    // Set promo links
    document.getElementById('youtubeBtn').href = promoLinks.youtube;
    document.getElementById('freedomBtn').href = promoLinks.freedom;

    // Apply formatting to numeric fields
    const numericFields = ['initialCapital', 'monthlyIncome', 'monthlyLivingExpenses'];
    numericFields.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', (e) => handleNumericInput(e.target));
            // Initial format if there's a value
            if (el.value) handleNumericInput(el);
        }
    });
});

// Helper for numeric formatting with cursor preservation
function handleNumericInput(input) {
    let value = input.value.replace(/\s/g, ''); // Remove existing spaces
    if (!/^\d*$/.test(value)) {
        // If not a number, revert to digits only
        value = value.replace(/\D/g, '');
    }

    const selectionStart = input.selectionStart;
    const oldLength = input.value.length;

    // Format with spaces
    const formatted = value.replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    input.value = formatted;

    // Restore cursor position
    const newLength = formatted.length;
    const delta = newLength - oldLength;
    input.setSelectionRange(selectionStart + delta, selectionStart + delta);
}

function cleanNumericValue(val) {
    return val ? val.toString().replace(/\s/g, '') : '';
}

// Event listeners
form.addEventListener('submit', handleFormSubmit);

editDataBtn.addEventListener('click', () => {
    formCard.style.display = 'block';
    editDataContainer.style.display = 'none';
    resultsSection.style.display = 'none';
});

toggleTableBtn.addEventListener('click', () => {
    const isHidden = tableContainer.style.display === 'none';
    tableContainer.style.display = isHidden ? 'block' : 'none';
    toggleTableBtn.innerText = isHidden ? '🔼 Скрыть таблицу' : '📋 Показать детальную таблицу';

    if (isHidden) {
        tableContainer.scrollIntoView({ behavior: 'smooth' });
    }
});

// Retirement mode switching
retirementModeRadios.forEach(radio => {
    radio.addEventListener('change', updateRetirementModeUI);
});

function updateRetirementModeUI() {
    const mode = document.querySelector('input[name="retirement_mode"]:checked').value;
    if (mode === 'auto') {
        retirementAgeInput.disabled = true;
        retirementAgeInput.value = '';
        retirementAgeGroup.style.opacity = '0.5';
    } else {
        retirementAgeInput.disabled = false;
        retirementAgeGroup.style.opacity = '1';
    }
}

// Advanced toggle
advancedToggle.addEventListener('click', () => {
    const isHidden = advancedContent.style.display === 'none';
    advancedContent.style.display = isHidden ? 'block' : 'none';
    advancedToggle.classList.toggle('active', isHidden);
});

// Tooltip logic
function setupTooltip(trigger, tooltip) {
    if (!trigger || !tooltip) return;
    trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        const isHidden = tooltip.style.display === 'none';

        // Close other tooltips
        document.querySelectorAll('.custom-tooltip').forEach(t => t.style.display = 'none');

        tooltip.style.display = isHidden ? 'block' : 'none';
    });
}

setupTooltip(infoTrigger, interestTooltip);
setupTooltip(inflationTrigger, inflationTooltip);

document.addEventListener('click', () => {
    document.querySelectorAll('.custom-tooltip').forEach(t => t.style.display = 'none');
});

// Reset logic
const defaultValues = {
    initialCapital: 10000,
    monthlyIncome: 3000,
    monthlyLivingExpenses: 1500,
    interestRate: 8,
    currentAge: 30,
    retirementAge: 45,
    incomeGrowthRate: 3,
    inflationRate: 3,
    maxAge: 90,
    retirement_mode: 'manual'
};

resetBtn.addEventListener('click', () => {
    Object.entries(defaultValues).forEach(([id, val]) => {
        if (id === 'retirement_mode') {
            const radio = document.querySelector(`input[name="retirement_mode"][value="${val}"]`);
            if (radio) radio.checked = true;
        } else {
            const el = document.getElementById(id);
            if (el) {
                el.value = val;
                // Re-apply formatting if needed
                if (['initialCapital', 'monthlyIncome', 'monthlyLivingExpenses'].includes(id)) {
                    handleNumericInput(el);
                }
            }
        }
    });
    updateRetirementModeUI();
    // Optional: clear local storage too? No, let user decide when to save.
});

// Form submission handler
async function handleFormSubmit(e) {
    e.preventDefault();

    const formData = new FormData(form);
    const data = {
        initial_capital: parseFloat(cleanNumericValue(formData.get('initialCapital'))),
        monthly_income: parseFloat(cleanNumericValue(formData.get('monthlyIncome'))),
        monthly_living_expenses: parseFloat(cleanNumericValue(formData.get('monthlyLivingExpenses'))),
        income_growth_rate: parseFloat(formData.get('incomeGrowthRate')),
        interest_rate: parseFloat(formData.get('interestRate')),
        inflation_rate: parseFloat(formData.get('inflationRate')),
        current_age: parseInt(formData.get('currentAge')),
        retirement_age: parseInt(formData.get('retirementAge')) || 60,
        retirement_mode: formData.get('retirement_mode'),
        max_age: parseInt(formData.get('maxAge')) || 90
    };

    // Validation
    if (data.retirement_mode === 'manual' && data.retirement_age <= data.current_age) {
        showWarning('Возраст выхода на пенсию должен быть больше текущего!');
        return;
    }

    // Save for persistence
    saveToLocalStorage(data);

    await calculateInvestment(data);
}

function showWarning(msg) {
    if (tg?.showAlert) {
        tg.showAlert(msg);
    } else {
        alert(msg);
    }
}

// API call to calculate investment
async function calculateInvestment(data) {
    showLoading(true);

    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            calculationResults = result.data;
            displayResults(calculationResults, result.actual_retirement_age);
        } else {
            showWarning('Ошибка: ' + result.error);
        }
    } catch (error) {
        console.error('API Error:', error);
        showWarning('Ошибка при соединении с сервером');
    } finally {
        showLoading(false);
    }
}

// Display results
function displayResults(results, actualRetirementAge) {
    resultsSection.style.display = 'block';
    formCard.style.display = 'none';
    editDataContainer.style.display = 'block';

    // Hide table by default
    tableContainer.style.display = 'none';
    toggleTableBtn.innerText = '📋 Показать детальную таблицу';

    renderChart(results, actualRetirementAge);
    renderTable(results, actualRetirementAge);
    renderSummary(results, actualRetirementAge);

    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Render Chart.js chart
function renderChart(results, effectiveRetAge) {
    const ctx = document.getElementById('capitalChart').getContext('2d');

    const labels = results.map(r => r.age);
    const capitalData = results.map(r => r.total_capital_end === 'Ø' ? 0 : r.total_capital_end);

    if (chart) chart.destroy();

    const getThemeColor = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
    const hintColor = getThemeColor('--hint-color') || '#94a3b8';
    const accentColor = getThemeColor('--button-color') || '#6366f1';
    const safeColor = '#10b981';
    const dangerColor = '#ef4444';
    const borderColor = getThemeColor('--card-border') || 'rgba(255,255,255,0.1)';

    const getZoneColor = (row) => {
        if (!row || row.expense_percentage === undefined) return accentColor;
        const rate = row.expense_percentage;
        if (rate <= 0) return accentColor; // Accumulation phase
        if (rate <= 4) return safeColor;
        if (rate <= 6) return accentColor;
        return dangerColor;
    };

    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Капитал',
                data: capitalData,
                borderColor: accentColor,
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                segment: {
                    borderColor: ctx => getZoneColor(results[ctx.p1DataIndex]),
                    backgroundColor: ctx => getZoneColor(results[ctx.p1DataIndex]) + '33'
                }
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: c => 'Возраст: ' + c[0].label,
                        label: c => 'Капитал: ' + formatCurrency(c.parsed.y)
                    }
                }
            },
            scales: {
                x: { grid: { color: borderColor }, ticks: { color: hintColor } },
                y: { grid: { color: borderColor }, ticks: { color: hintColor, callback: v => formatCurrencyShort(v) } }
            }
        }
    });

    document.getElementById('chartLegend').style.display = results.some(r => r.expense_percentage > 0) ? 'flex' : 'none';
}

// Render table
function renderTable(results, effectiveRetAge) {
    resultsTableBody.innerHTML = '';
    results.forEach((row) => {
        const tr = document.createElement('tr');
        if (row.age === effectiveRetAge) tr.classList.add('highlight');

        const currentCapital = row.total_capital_start === 'Ø' ? 'Ø' : formatCurrency(row.total_capital_start);
        const interestIncome = formatCurrency(row.interest_income);
        const annualFlow = formatCurrency(row.investment_capital > 0 ? row.investment_capital * 12 : -row.expenses_inflation * 12);

        tr.innerHTML = `<td>${row.age}</td><td>${currentCapital}</td><td>${interestIncome}</td><td>${annualFlow}</td>`;
        resultsTableBody.appendChild(tr);
    });
}

// Render summary
function renderSummary(results, effectiveRetAge) {
    const retirementYear = results.find(r => r.age === effectiveRetAge);
    const lastYear = results[results.length - 1];
    const maxCapital = Math.max(...results.map(r => r.total_capital_end === 'Ø' ? 0 : r.total_capital_end));

    const currentAge = parseInt(document.getElementById('currentAge').value);
    const yearsUntilRet = effectiveRetAge - currentAge;

    // Build timeline milestones (every 10 years from retirement)
    let budgetTimelineHtml = '';
    if (retirementYear) {
        const milestones = [];
        for (let age = effectiveRetAge; age <= lastYear.age; age += 10) {
            const row = results.find(r => r.age === age);
            if (row && row.total_capital_start !== 'Ø') {
                milestones.push({
                    age: age,
                    expenses: row.expenses_inflation
                });
            }
        }

        budgetTimelineHtml = `
            <div class="summary-item budget-timeline">
                <div class="summary-label">📊 Планируемый бюджет (в месяц):</div>
                <ul class="milestone-list">
                    ${milestones.map(m => `
                        <li>
                            <span class="ms-age">В ${m.age} лет:</span>
                            <span class="ms-value">${formatCurrencyShort(m.expenses)}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }

    summaryContent.innerHTML = `
        <div class="summary-item">
            <div class="summary-label">⏳ Лет до пенсии</div>
            <div class="summary-value">${yearsUntilRet > 0 ? `${yearsUntilRet} лет (в ${effectiveRetAge})` : 'Уже на пенсии'}</div>
        </div>
        ${budgetTimelineHtml}
        <div class="summary-item">
            <div class="summary-label">💰 Капитал при выходе на пенсию</div>
            <div class="summary-value">${retirementYear ? formatCurrencyShort(retirementYear.total_capital_end) : '—'}</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">📈 Максимальный капитал</div>
            <div class="summary-value">${formatCurrencyShort(maxCapital)}</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">🎯 Капитал в ${lastYear.age} лет</div>
            <div class="summary-value">${lastYear.total_capital_end === 'Ø' ? 'Исчерпан' : formatCurrencyShort(lastYear.total_capital_end)}</div>
        </div>
    `;
}

// Utility functions
function formatCurrency(v) {
    if (v === 'Ø' || v === null || isNaN(v)) return 'Ø';
    return '$' + parseFloat(v).toLocaleString('ru-RU', { maximumFractionDigits: 0 });
}

function formatCurrencyShort(v) {
    if (v === 'Ø' || v === null || isNaN(v)) return 'Ø';
    if (v >= 1e9) return '$' + (v / 1e9).toFixed(1) + 'B';
    if (v >= 1e6) return '$' + (v / 1e6).toFixed(1) + 'M';
    if (v >= 1e3) return '$' + (v / 1e3).toFixed(1) + 'K';
    return '$' + v.toFixed(0);
}

function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

function saveToLocalStorage(data) {
    localStorage.setItem('investment_calculator_data_v2', JSON.stringify(data));
}

function loadSavedData() {
    const saved = localStorage.getItem('investment_calculator_data_v2');
    if (!saved) return;
    try {
        const data = JSON.parse(saved);
        const map = {
            initial_capital: 'initialCapital', monthly_income: 'monthlyIncome',
            monthly_living_expenses: 'monthlyLivingExpenses', interest_rate: 'interestRate',
            current_age: 'currentAge', retirement_age: 'retirementAge',
            income_growth_rate: 'incomeGrowthRate', inflation_rate: 'inflationRate', max_age: 'maxAge'
        };
        Object.entries(data).forEach(([k, v]) => {
            if (k === 'retirement_mode') {
                const radio = document.querySelector(`input[name="retirement_mode"][value="${v}"]`);
                if (radio) radio.checked = true;
            } else if (map[k]) {
                const el = document.getElementById(map[k]);
                if (el) {
                    el.value = v;
                    if (['initialCapital', 'monthlyIncome', 'monthlyLivingExpenses'].includes(map[k])) {
                        handleNumericInput(el);
                    }
                }
            }
        });
    } catch (e) { console.error(e); }
}
