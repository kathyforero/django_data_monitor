/**
 * For usage, visit Chart.js docs https://www.chartjs.org/docs/latest/
 */
const lineConfig = {
  type: 'line',
  data: {
    labels: ['Hito 1', 'Hito 2', 'Hito 3', 'Hito 4', 'Hito 5', 'Hito 6', 'Hito 7'],
    datasets: [
      {
        label: 'Serie 1',
        /**
         * These colors come from Tailwind CSS palette
         * https://tailwindcss.com/docs/customizing-colors/#default-color-palette
         */
        backgroundColor: '#0694a2',
        borderColor: '#0694a2',
        data: [43, 48, 40, 54, 67, 73, 70],
        fill: false,
      },
      {
        label: 'Serie 2',
        fill: false,
        /**
         * These colors come from Tailwind CSS palette
         * https://tailwindcss.com/docs/customizing-colors/#default-color-palette
         */
        backgroundColor: '#7e3af2',
        borderColor: '#7e3af2',
        data: [24, 50, 64, 74, 52, 51, 65],
      },
    ],
  },
  options: {
    responsive: true,
    /**
     * Default legends are ugly and impossible to style.
     * See examples in charts.html to add your own legends
     *  */
    legend: {
      display: false,
    },
    tooltips: {
      mode: 'index',
      intersect: false,
    },
    hover: {
      mode: 'nearest',
      intersect: true,
    },
    scales: {
      x: {
        display: true,
        scaleLabel: {
          display: true,
          labelString: 'Month',
        },
      },
      y: {
        display: true,
        scaleLabel: {
          display: true,
          labelString: 'Value',
        },
      },
    },
  },
}

// change this to the id of your chart element in HMTL
const lineCtx = document.getElementById('line')

// Cargar datos dinámicos desde el template Django
const chartDataElement = document.getElementById('chart-data')
if (chartDataElement) {
  const dynamicData = JSON.parse(chartDataElement.textContent)
  
  // Actualizar configuración con datos reales
  lineConfig.data.labels = dynamicData.labels
  lineConfig.data.datasets = [
    {
      label: 'Reseñas Acumuladas',
      backgroundColor: '#0694a2',
      borderColor: '#0694a2',
      data: dynamicData.data,
      fill: false,
      tension: 0.4, // Línea suave
    }
  ]
  
  // Actualizar opciones
  lineConfig.options.scales = {
    x: {
      display: true,
      title: {
        display: true,
        text: 'Fechas'
      }
    },
    y: {
      display: true,
      title: {
        display: true,
        text: 'Total de Reseñas'
      },
      beginAtZero: true
    }
  }
}

window.myLine = new Chart(lineCtx, lineConfig)
