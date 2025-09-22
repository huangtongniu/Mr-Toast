const API_BASE_URL = "http://127.0.0.1:5002";
    let l2PriceChart;

    function formatCurrency(num) {
        if (typeof num !== 'number') return '$0.00';
        return  `$${num.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    }

    function initializeCharts() {
        Chart.defaults.color = 'white';
        const l2ctx = document.getElementById('l2-price-chart').getContext('2d');
        l2PriceChart = new Chart(l2ctx, { type: 'line', data: { labels: [], datasets: [{ label: '价格', data: [], borderColor: '#3498db', fill: false }]}, options: { scales: { x: { ticks: { color: 'white' }}, y: { ticks: { color: 'white', callback: v => `$${v}` }} }, plugins: { legend: { display: false } } }});
    }

    // --- 这里是修改的核心 ---
    // 修改后的 renderGame 函数不再负责跳转页面
    function renderGame(data) {
        // 如果后端数据是第3关或更高，此页面不处理，直接返回
        if (data.currentLevel >= 3) {
            console.log("收到了第3关的数据，但此页面不渲染它。等待跳转指令...");
            return;
        }

        document.querySelectorAll('.scene').forEach(s => s.classList.remove('active'));
        const currentLevel = data.currentLevel;
        document.getElementById(`level-${currentLevel}-scene`).classList.add('active');
        document.getElementById('level-indicator').textContent = currentLevel;

        if (currentLevel === 1) renderLevel1(data);
        else if (currentLevel === 2) renderLevel2(data);
    }

    function renderLevel1(data) {
        document.getElementById('l1-principal').textContent = formatCurrency(data.principal);
        document.getElementById('l1-interest-earned').textContent = formatCurrency(data.interestEarned);
        document.getElementById('l1-goal').textContent = formatCurrency(data.goal);
        
        const optionsDiv = document.getElementById('l1-rates-options');
        optionsDiv.innerHTML = '';
        data.availableRates.forEach(opt => {
            optionsDiv.innerHTML += `<button onclick="performAction({action: 'deposit', period: ${opt.period}, rate: ${opt.rate}})">Save ${opt.period} days (annual rate ${opt.rate * 100}%)</button> `;
        });
        document.getElementById('l1-advance-btn').disabled = !data.isGoalMet;
    }

    function renderLevel2(data) {
        document.getElementById('l2-cash').textContent = formatCurrency(data.cash);
        document.getElementById('l2-total-value').textContent = formatCurrency(data.totalValue);
        document.getElementById('l2-goal').textContent = formatCurrency(data.goal);
        
        document.getElementById('l2-stock-info').innerHTML = `
            <h3>${data.stock.name} (${data.stock.ticker})</h3>
            <p>Today's Price: <strong>${formatCurrency(data.stock.price)}</strong></p>
            <p>Your Holdings: <strong>${data.stock.holding} shares</strong></p>
            <p>Date: ${data.date}</p>`;
                        
        l2PriceChart.data.labels = data.priceHistory.map(h => h.date);
        l2PriceChart.data.datasets[0].data = data.priceHistory.map(h => h.price);
        l2PriceChart.update();
        document.getElementById('l2-advance-btn').disabled = !data.isGoalMet;
    }

    async function apiCall(endpoint, method = 'GET', body = null) {
        try {
            const options = { method, headers: { 'Content-Type': 'application/json' } };
            if (body) options.body = JSON.stringify(body);
            const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
            if (!response.ok) {
                const data = await response.json();
                alert(`Operation failed: ${data.error || 'Unknown error'}`);
                return null;
            }
            const data = await response.json();
            // apiCall 仍然调用 renderGame，但新的 renderGame 不会跳转
            renderGame(data); 
            return data; // 将后端返回的数据传递出去
        } catch (error) {
            console.error("API call failed:", error);
            alert("Unable to connect to the backend server. Please make sure the Python backend script is running.");
            return null;
        }
    }
    
    function performAction(actionData) { apiCall('/api/perform_action', 'POST', actionData); }

    document.addEventListener('DOMContentLoaded', () => {
        initializeCharts();
        apiCall('/api/game_state');

        document.getElementById('reset-btn').addEventListener('click', () => {
            if (confirm("Are you sure you want to restart from level 1? All progress will be lost.")) {
                apiCall('/api/reset', 'POST');
            }
        });
        
        document.getElementById('l1-advance-btn').addEventListener('click', () => {
            if(confirm('Awesome! Ready to move on to the next level?')) apiCall('/api/advance_level', 'POST');
        });
        
        // --- 这里是修改的核心 ---
        // 修改后的按钮事件处理器，显式地处理跳转逻辑
        document.getElementById('l2-advance-btn').addEventListener('click', async () => {
            if(confirm('Awesome! Ready for the final level?')) {
                // 1. 调用API并等待它完成
                const result = await apiCall('/api/advance_level', 'POST');
                
                // 2. 只有在API调用成功返回结果，并且确认是第3关时，才执行跳转
                if (result && result.currentLevel === 3) {
                    window.location.href = '/game/part2';
                }
            }
        });


        document.getElementById('l2-buy-btn').addEventListener('click', () => performAction({ action: 'buy', quantity: document.getElementById('l2-quantity').value }));
        document.getElementById('l2-sell-btn').addEventListener('click', () => performAction({ action: 'sell', quantity: document.getElementById('l2-quantity').value }));
        document.getElementById('l2-next-day-btn').addEventListener('click', () => performAction({action: 'next_day'}));
    });

    // 语言包
const LANG = {
    zh: {
        mainTitle: "Legacy Guardians - 第 <span id='level-indicator'>1</span> 关",
        reset: "全部重玩",
        level1: {
            title: "第一关：银行储蓄",
            desc: "欢迎来到财富之旅的第一站！学习利用银行储蓄，让你的财富通过“复利”的力量慢慢增长。选择一个存款方案，看看你的资金会如何变化。",
            principal: "当前本金",
            interest: "已赚利息",
            goal: "通关目标",
            advance: "恭喜通关！进入下一关",
            tipsTitle: "知识小贴士",
            tips1: "<strong>本金 (Principal):</strong> 你最初存入的钱。",
            tips2: "<strong>利率 (Interest Rate):</strong> 银行付给你钱的百分比，通常是年化利率。",
            tips3: "<strong>复利 (Compound Interest):</strong> 不仅你的本金可以赚取利息，你赚到的利息也能继续赚取利息。这就是爱因斯坦所说的“世界第八大奇迹”！",
            formulas_title: "计算公式",
            formula_interest: "<strong>单利:</strong> 利息 = 本金 × 年化利率 × (天数 / 365)",
            formula_compound: "<strong>复利:</strong> A = P(1 + r/n)<sup>nt</sup><br><small style='opacity:0.8'>其中: A=最终金额, P=本金, r=年利率, n=年复利次数, t=年数</small>"
        
        },
        level2: {
            title: "第二关：初识股票",
            desc: "你已掌握了储蓄的基础，现在来体验风险与收益并存的股票市场吧！在本关，你将专注于一支科技股 TECH_A，通过低买高卖来增加你的资产。",
            buy: "买入",
            sell: "卖出",
            nextDay: "等待一天 (不操作)",
            advance: "恭喜通关！进入第三关",
            cash: "当前现金",
            totalValue: "总资产",
            goal: "通关目标"
        },
        level3: {
            title: "第三关：投资组合",
            desc: "欢迎来到最终挑战！在本关你需要同时管理多种资产，包括股票和现金流。通过合理配置投资组合，实现财富的稳健增长。",
            nextDay: "下一天",
            reset: "重新开始",
            cashFlow: "现金流",
            totalAssets: "总资产",
            advance: "恭喜通关！完成全部关卡！"
        },
        english: "English",
        chinese: "中文"
    },
    en: {
        mainTitle: "Legacy Guardians - Level <span id='level-indicator'>1</span>",
        reset: "Restart All",
        level1: {
            title: "Level 1: Bank Savings",
            desc: "Welcome to the first stop of your wealth journey! Learn to use bank savings and let your wealth grow through the power of compound interest. Choose a deposit plan and see how your money changes.",
            principal: "Principal",
            interest: "Interest Earned",
            goal: "Goal",
            advance: "Congratulations! Next Level",
            tipsTitle: "Knowledge Tips",
            tips1: "<strong>Principal:</strong> The money you initially deposit.",
            tips2: "<strong>Interest Rate:</strong> The percentage the bank pays you, usually annualized.",
            tips3: "<strong>Compound Interest:</strong> Not only does your principal earn interest, but your earned interest also earns interest. This is the 'eighth wonder of the world' according to Einstein!",
            formulas_title: "Formulas",
            formula_interest: "<strong>Simple Interest:</strong> Interest = Principal × Annual Rate × (Days / 365)",
            formula_compound: "<strong>Compound Interest:</strong> A = P(1 + r/n)<sup>nt</sup><br><small style='opacity:0.8'>Where: A=Final Amount, P=Principal, r=Annual Rate, n=Compounding periods, t=Years</small>"
        },
        level2: {
            title: "Level 2: Introduction to Stocks",
            desc: "You have mastered the basics of savings, now experience the risks and rewards of the stock market! In this level, you will focus on one tech stock, TECH_A, and try to increase your wealth by buying low and selling high.",
            buy: "Buy",
            sell: "Sell",
            nextDay: "Wait one day (no action)",
            advance: "Congratulations! Proceed to Level 3",
            cash: "Current Cash",
            totalValue: "Total Value",
            goal: "Goal"
        },
        level3: {
            title: "Level 3: Investment Portfolio",
            desc: "Welcome to the final challenge! In this level, you need to manage multiple assets, including stocks and cash flow. By allocating your portfolio wisely, achieve sustainable wealth growth.",
            nextDay: "Next Day",
            reset: "Restart",
            cashFlow: "Cash Flow",
            totalAssets: "Total Assets",
            advance: "Congratulations! You have completed all levels!"
        },
        english: "English",
        chinese: "中文"
    }
};

let currentLang = 'zh';

function switchLanguage(canToggle = true) { 
    // 只有当 canToggle 为 true 时（即用户点击按钮时），才切换语言
    if (canToggle) {
        currentLang = (currentLang === 'zh') ? 'en' : 'zh';
    }
    
    const lang = LANG[currentLang];


    // 标题
    document.getElementById('main-title').innerHTML = lang.mainTitle;
    document.getElementById('reset-btn').textContent = lang.reset;
    document.getElementById('lang-toggle-btn').textContent = currentLang === 'zh' ? lang.english : lang.chinese;

    // Level 1
    if (document.getElementById('level-1-scene').classList.contains('active')) {
        const langL1 = lang.level1;
        document.querySelector('#level-1-scene .panel h2').textContent = langL1.title;
        document.querySelector('#level-1-scene .panel p').textContent = langL1.desc;
        document.querySelector('#l1-principal').previousElementSibling.textContent = langL1.principal;
        document.querySelector('#l1-interest-earned').previousElementSibling.textContent = langL1.interest;
        document.querySelector('#l1-goal').previousElementSibling.textContent = langL1.goal;
        document.getElementById('l1-advance-btn').textContent = langL1.advance;
        
        // Tips and Formulas
        document.getElementById('l1_tips_title').textContent = langL1.tipsTitle;
        document.getElementById('l1_tip_principal').innerHTML = langL1.tips1;
        document.getElementById('l1_tip_rate').innerHTML = langL1.tips2;
        document.getElementById('l1_tip_compound').innerHTML = langL1.tips3;
        
        // --- ↓↓↓ 新增的翻译代码 ↓↓↓ ---
        document.getElementById('l1_formulas_title').textContent = langL1.formulas_title;
        document.getElementById('l1_formula_interest').innerHTML = langL1.formula_interest;
        document.getElementById('l1_formula_compound').innerHTML = langL1.formula_compound;
    }
    
    // level 2
    if (document.getElementById('level-2-scene').classList.contains('active')) {
        const langL2 = lang.level2;
        document.querySelector('#level-2-scene .panel h2').textContent = langL2.title;
        document.querySelector('#level-2-scene .panel p').textContent = langL2.desc;
        document.getElementById('l2-buy-btn').textContent = langL2.buy;
        document.getElementById('l2-sell-btn').textContent = langL2.sell;
        document.getElementById('l2-next-day-btn').textContent = langL2.nextDay;
        document.getElementById('l2-advance-btn').textContent = langL2.advance;
        document.getElementById('l2-cash').previousElementSibling.textContent = langL2.cash;
        document.getElementById('l2-total-value').previousElementSibling.textContent = langL2.totalValue;
        document.getElementById('l2-goal').previousElementSibling.textContent = langL2.goal;
    }

    // Level 3
    if (document.getElementById('level-3-scene')?.classList.contains('active')) {
        const langL3 = lang.level3;
        document.querySelector('#level-3-scene .panel h2').textContent = langL3.title;
        document.querySelector('#level-3-scene .panel p').textContent = langL3.desc;
        document.getElementById('next-day-btn').textContent = langL3.nextDay;
        document.getElementById('reset-btn').textContent = langL3.reset;
        document.querySelectorAll('.footer-item p')[0].textContent = langL3.cashFlow;
        document.querySelectorAll('.footer-item p')[1].textContent = langL3.totalAssets;
        document.getElementById('l3-advance-btn').textContent = langL3.advance;
    }
}

// 绑定事件
document.addEventListener('DOMContentLoaded', () => {
    // ...existing code...
    document.getElementById('lang-toggle-btn').addEventListener('click', switchLanguage);
});

