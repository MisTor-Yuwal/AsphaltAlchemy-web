/*
fetch('/admin/profit-loss')
      .then(res => res.json())
      .then(data => {
        const dates = data.map(entry => entry.date);
        const profits = data.map(entry => entry.profit);

        const options = {
        chart: {
          type: 'line',
          height: 350,
          toolbar: { show: false }
        },
        series: [{
          name: 'Profit / Loss',
          data: profits
        }],
        xaxis: {
          categories: dates,
          title: { text: 'Date' }
        },
        yaxis: {
          title: { text: 'Amount (Rs)' }
        },
        stroke: {
          curve: 'smooth',
          width: 3
        },
        markers: {
          size: 5,
          colors: ['#FFA41B'],
          strokeColors: '#fff',
          strokeWidth: 2
        },
        tooltip: {
          y: {
            formatter: val => val >= 0 ? `Profit: Rs ${val}` : `Loss: Rs ${Math.abs(val)}`
          }
        },
        colors: ['#00E396'], 
        responsive: [{
          breakpoint: 600,
          options: {
            chart: { height: 300 }
          }
        }]
      };

        const chart = new ApexCharts(document.querySelector("#profitLossChart"), options);
        chart.render();
      });
      */