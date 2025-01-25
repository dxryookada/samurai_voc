// --- 共通のグラフ描画関数 --- //
function createChart(ctx, options = {}) {
  return new Chart(ctx, {
    type: 'bar',
    maintainAspectRatio: true, // 比率を維持
    data: {
      labels: ["質問1", "質問2"], // 初期ラベル
      datasets: [{
        data: [0, 0], // 初期データ
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
        barThickness: 20 // 棒グラフの太さ
      }]
    },
    options: Object.assign({
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { beginAtZero: true, max: 5 },
        y: { ticks: { autoSkip: false } }
      },
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      }
    }, options)
  });
}

// --- グラフ更新関数 --- //
function updateChart(chart, url) {
  fetch(url)
    .then(res => res.json())
    .then(data => {
      if (data.questions && Array.isArray(data.questions)) {
        chart.data.labels = data.questions.map(q => q.question);
        chart.data.datasets[0].data = data.questions.map(q => q.average_scores[0]);
      } else {
        chart.data.labels = ["質問1", "質問2"];
        chart.data.datasets[0].data = [0, 0];
      }
      chart.update(); // グラフを再描画
    })
    .catch(e => {
      alert(`通信に失敗しました: ${e}`);
    });
}

// --- グラフの初期化 --- //
const ctxUser = document.getElementById('survey-chart').getContext('2d');
const userSurveyChart = createChart(ctxUser);

const ctxTop1User = document.getElementById('survey-top1-chart').getContext('2d');
const userTop1SurveyChart = createChart(ctxTop1User);

// 年代のラジオボタン変更時にグラフを更新
document.querySelectorAll('input[name="age"]').forEach(radio => {
  radio.addEventListener('change', function() {
    const ageGroupId = this.value; // 選択された年代ID

    // 棒グラフを再描画
    const url = `/general/api/survey-data/?age_group=${ageGroupId}`;
    updateChart(userSurveyChart, url);
  });
});

// --- 初期化時にデータ取得 --- //
updateChart(userSurveyChart, 'api/survey-data/?age_group=all');
updateChart(userTop1SurveyChart, 'api/survey-data/?age_group=all');