const ctx = document.getElementById('surveyChart').getContext('2d');
let surveyChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ["質問1", "質問2"], // Y軸の質問ラベル
    datasets: [{
      data: [0, 0], // 評価値をセット
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      borderColor: 'rgba(75, 192, 192, 1)',
      borderWidth: 1,
      barThickness: 20 // 棒グラフの太さ
    }]
  },
  options: {
    indexAxis: 'y', // 横棒グラフ
    responsive: true,
    maintainAspectRatio: false, // レイアウトを柔軟に調整
    scales: {
      x: {
        beginAtZero: true,
        max: 5 // 最大スコア
      },
      y: {
        ticks: {
          autoSkip: false // 全てのラベルを表示
        }
      }
    },
    plugins: {
      legend: {
        display: false // 凡例を完全非表示
      },
      tooltip: {
        enabled: false // ツールチップを非表示
      }
    }
  }
});

// 年代のラジオボタン変更時にグラフを更新
document.querySelectorAll('input[name="age"]').forEach(radio => {
  radio.addEventListener('change', function() {
    const ageGroupId = this.value; // 選択された年代ID

    // 棒グラフを再描画
    updateChart(ageGroupId);
  });
});

// 棒グラフ描画Ajax関数
function updateChart(ageGroupId) {
  const url = `api/survey-data/?age_group=${ageGroupId}`;
  fetch(url)
    .then(res => res.json())
    .then(data => {
      // console.log(data); // デバッグ用にレスポンスを確認
      if (data.questions && Array.isArray(data.questions)) {
        surveyChart.data.labels = data.questions.map(q => q.question);
        surveyChart.data.datasets[0].data = data.questions.map(q => q.average_scores[0]);
      } else {
        // データが空の場合の処理
        surveyChart.data.labels = ["質問1", "質問2"];
        surveyChart.data.datasets[0].data = [0, 0];
      }
      // 棒グラフを再描画
      surveyChart.update();
    })
    .catch(e => {
      alert(`通信に失敗しました: ${e}`);
    });
}

updateChart('');