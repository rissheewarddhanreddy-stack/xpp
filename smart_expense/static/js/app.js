const palette = ["#d1583d", "#e7a96e", "#25695f", "#1d2433", "#7e8a97", "#8f3523", "#78b0a1"];

function formatCurrency(value) {
    return `₹${Number(value || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

function renderExpenseDonut(activePlan) {
    const chart = document.getElementById("expense-donut");
    const legend = document.getElementById("expense-legend");
    if (!chart || !legend || !activePlan) {
        return;
    }

    const entries = Object.entries(activePlan.expense_breakdown || {});
    const total = entries.reduce((sum, [, amount]) => sum + Number(amount || 0), 0);
    if (!total) {
        return;
    }

    let cumulative = 0;
    const segments = entries.map(([label, amount], index) => {
        const degrees = (Number(amount) / total) * 360;
        const start = cumulative;
        cumulative += degrees;
        return `${palette[index % palette.length]} ${start}deg ${cumulative}deg`;
    });
    chart.style.background = `conic-gradient(${segments.join(", ")})`;

    legend.innerHTML = entries
        .map(
            ([label, amount], index) => `
                <div class="legend-item">
                    <div class="legend-key">
                        <span class="legend-swatch" style="background:${palette[index % palette.length]}"></span>
                        <span>${label}</span>
                    </div>
                    <strong>${formatCurrency(amount)}</strong>
                </div>
            `
        )
        .join("");
}

function renderHistoryBars(history) {
    const container = document.getElementById("history-bars");
    if (!container || !history || !history.length) {
        return;
    }

    const maxValue = Math.max(...history.flatMap((row) => [row.income, row.expenses, 1]));
    container.innerHTML = history
        .map((row) => {
            const incomeWidth = `${Math.max((row.income / maxValue) * 100, 10)}%`;
            const expenseWidth = `${Math.max((row.expenses / maxValue) * 100, 10)}%`;
            return `
                <div class="bar-row" style="--income-width:${incomeWidth}; --expense-width:${expenseWidth};">
                    <div class="bar-header">
                        <span>${row.label}</span>
                        <span>${formatCurrency(row.remaining)} left</span>
                    </div>
                    <div class="bar-track">
                        <div class="bar-income" title="Income: ${formatCurrency(row.income)}"></div>
                        <div class="bar-expense" title="Expenses: ${formatCurrency(row.expenses)}"></div>
                    </div>
                </div>
            `;
        })
        .join("");
}

document.addEventListener("DOMContentLoaded", () => {
    const data = window.dashboardData || {};
    renderExpenseDonut(data.active_plan);
    renderHistoryBars(data.history || []);
});
