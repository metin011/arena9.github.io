// Arena 9 - Chart.js Konfiqurasiyası
// Oyunçu və maç statistikaları üçün qrafiklər

// Rəng paleti
const chartColors = {
    primary: '#2ECC71',
    secondary: '#3498DB',
    danger: '#E74C3C',
    warning: '#F39C12',
    info: '#9B59B6',
    dark: '#1a1a1a',
    light: '#f8fafc',
    grid: '#262626'
};

// Chart.js default konfiqurasiya
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = '#262626';
Chart.defaults.font.family = 'Space Grotesk';

// 1. Oyunçu Statistika Radar Chart
function createPlayerStatsChart(canvasId, playerData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Pace', 'Shooting', 'Passing', 'Dribbling', 'Defending', 'Physical'],
            datasets: [{
                label: playerData.name,
                data: [
                    playerData.pace,
                    playerData.shooting,
                    playerData.passing,
                    playerData.dribbling,
                    playerData.defending,
                    playerData.physical
                ],
                backgroundColor: 'rgba(46, 204, 113, 0.2)',
                borderColor: chartColors.primary,
                borderWidth: 2,
                pointBackgroundColor: chartColors.primary,
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: chartColors.primary
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        backdropColor: 'transparent'
                    },
                    grid: {
                        color: chartColors.grid
                    },
                    pointLabels: {
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// 2. Sezon Müqayisə Bar Chart
function createSeasonComparisonChart(canvasId, seasonData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: seasonData.seasons,
            datasets: [
                {
                    label: 'Qollar',
                    data: seasonData.goals,
                    backgroundColor: chartColors.primary,
                    borderRadius: 8
                },
                {
                    label: 'Assistlər',
                    data: seasonData.assists,
                    backgroundColor: chartColors.secondary,
                    borderRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: chartColors.grid
                    },
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                }
            }
        }
    });
}

// 3. Qol Trend Xətti (Line Chart)
function createGoalTrendChart(canvasId, trendData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: trendData.matches,
            datasets: [{
                label: 'Qollar',
                data: trendData.goals,
                borderColor: chartColors.primary,
                backgroundColor: 'rgba(46, 204, 113, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 7,
                pointBackgroundColor: chartColors.primary,
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: chartColors.grid
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// 4. Mövqe üzrə Ortalama Reytinq (Horizontal Bar)
function createPositionAverageChart(canvasId, positionData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: positionData.positions,
            datasets: [{
                label: 'Ortalama Reytinq',
                data: positionData.ratings,
                backgroundColor: [
                    chartColors.primary,
                    chartColors.secondary,
                    chartColors.info,
                    chartColors.warning,
                    chartColors.danger
                ],
                borderRadius: 8
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: chartColors.grid
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// 5. Dashboard Statistika Donut Chart
function createDashboardStatsChart(canvasId, statsData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: statsData.labels,
            datasets: [{
                data: statsData.values,
                backgroundColor: [
                    chartColors.primary,
                    chartColors.secondary,
                    chartColors.info,
                    chartColors.warning
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    });
}

// 6. Oyunçu Müqayisə Radar Chart (2 oyunçu)
function createPlayerComparisonChart(canvasId, player1, player2) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Pace', 'Shooting', 'Passing', 'Dribbling', 'Defending', 'Physical'],
            datasets: [
                {
                    label: player1.name,
                    data: [
                        player1.pace,
                        player1.shooting,
                        player1.passing,
                        player1.dribbling,
                        player1.defending,
                        player1.physical
                    ],
                    backgroundColor: 'rgba(46, 204, 113, 0.2)',
                    borderColor: chartColors.primary,
                    borderWidth: 2,
                    pointBackgroundColor: chartColors.primary
                },
                {
                    label: player2.name,
                    data: [
                        player2.pace,
                        player2.shooting,
                        player2.passing,
                        player2.dribbling,
                        player2.defending,
                        player2.physical
                    ],
                    backgroundColor: 'rgba(52, 152, 219, 0.2)',
                    borderColor: chartColors.secondary,
                    borderWidth: 2,
                    pointBackgroundColor: chartColors.secondary
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        backdropColor: 'transparent'
                    },
                    grid: {
                        color: chartColors.grid
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                }
            }
        }
    });
}

// 7. Forma Qrafiki (Son 5 maç - W/D/L)
function createFormChart(canvasId, formData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // W = Win (yaşıl), D = Draw (sarı), L = Loss (qırmızı)
    const colors = formData.results.map(result => {
        if (result === 'W') return chartColors.primary;
        if (result === 'D') return chartColors.warning;
        return chartColors.danger;
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: formData.matches,
            datasets: [{
                label: 'Forma',
                data: formData.results.map(r => r === 'W' ? 3 : r === 'D' ? 1 : 0),
                backgroundColor: colors,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 3,
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            if (value === 3) return 'W';
                            if (value === 1) return 'D';
                            if (value === 0) return 'L';
                            return '';
                        }
                    },
                    grid: {
                        color: chartColors.grid
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const result = formData.results[context.dataIndex];
                            if (result === 'W') return 'Qələbə';
                            if (result === 'D') return 'Heç-heçə';
                            return 'Məğlubiyyət';
                        }
                    }
                }
            }
        }
    });
}
