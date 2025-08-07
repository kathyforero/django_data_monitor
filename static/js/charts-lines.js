document.addEventListener("DOMContentLoaded", () => {
  const ratingsByStar = JSON.parse(document.getElementById('ratings-data').textContent);
  const lineConfig = {
    type: 'line',
    data: {
      labels: ['1 ⭐', '2 ⭐', '3 ⭐', '4 ⭐', '5 ⭐'],
      datasets: [
        {
          label: 'Número de reseñas',
          backgroundColor: '#0694a2',
          borderColor: '#0694a2',
          data: ratingsByStar, // usamos la variable enviada desde Django
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true,
        },
        tooltip: {
          mode: 'index',
          intersect: false,
        },
      },
      interaction: {
        mode: 'nearest',
        intersect: true,
      },
      scales: {
        x: {
          title: {
            display: true,
            text: 'Estrellas',
          },
        },
        y: {
          title: {
            display: true,
            text: 'Cantidad de reseñas',
          },
          beginAtZero: true,
          precision: 0,
          ticks: {
            stepSize: 1,
          },
        },
      },
    },
  };

  const lineCtx = document.getElementById('line');
  window.myLine = new Chart(lineCtx, lineConfig);
});