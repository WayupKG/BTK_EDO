var m_done_count = document.getElementById('m_done_count').innerHTML
var m_process_count = document.getElementById('m_process_count').innerHTML
var m_not_executed_count = document.getElementById('m_not_executed_count').innerHTML

var d_done_count = document.getElementById('d_done_count').innerHTML
var d_process_count = document.getElementById('d_process_count').innerHTML
var d_not_executed_count = document.getElementById('d_not_executed_count').innerHTML

var submitted = document.getElementById('submitted').innerHTML
var rejected = document.getElementById('rejected').innerHTML
var approved = document.getElementById('approved').innerHTML
var done = document.getElementById('done').innerHTML

var inbox_config = {
    type: 'doughnut',
    data: {
        labels: ["Выполнено", "В процессе", "Не выполнено"],
        datasets: [{
            backgroundColor: ["rgba(5, 235, 12, 0.5)", "#daeb23", "#bf4343"],
            data: [m_done_count, m_process_count, m_not_executed_count],
            borderWidth: [0, 0, 0]}]
    },
    options: {
        maintainAspectRatio: false,
        legend: {
            position :"bottom",
            display: false,
            labels: {fontColor: '#ddd', boxWidth:15}}, tooltips: {displayColors:false}},
        title: {display: true, text: 'Chart.js Doughnut Chart'},
        animation: {animateScale: true, animateRotate: true}
    };

var shipped_config = {
    type: 'doughnut',
    data: {
        labels: ["Выполнено", "В процессе", "Не выполнено"],
        datasets: [{
            backgroundColor: ["rgba(5, 235, 12, 0.5)", "#daeb23", "#bf4343"],
            data: [d_done_count, d_process_count, d_not_executed_count],
            borderWidth: [0, 0, 0]}]
    },
    options: {
        maintainAspectRatio: false,
        legend: {
            position :"bottom",
            display: false,
            labels: {fontColor: '#ddd', boxWidth:15}}, tooltips: {displayColors:false}},
        title: {display: true, text: 'Chart.js Doughnut Chart'},
        animation: {animateScale: true, animateRotate: true}
    };

window.onload = function() {
    var inbox = document.getElementById('InboxDoc').getContext('2d');
    var shipped = document.getElementById('ShippedDoc').getContext('2d');

    window.InboxDoc = new Chart(inbox, inbox_config);
    window.ShippedDoc = new Chart(shipped, shipped_config);
};

var statement_config = {
    type: 'doughnut',
    data: {
        labels: ["Подано", "Отклонено", "Утверждено", "Выполнено"],
        datasets: [{
            backgroundColor: ["#daeb23", "#bf4343", "#436fbf", "#16b81b"],
            data: [submitted, rejected, approved, done],
            borderWidth: [0, 0, 0, 0]}]
    },
    options: {
        maintainAspectRatio: false,
        legend: {
            position :"bottom",
            display: false,
            labels: {fontColor: '#ddd', boxWidth:15}}, tooltips: {displayColors:false}},
        title: {display: true, text: 'Chart.js Doughnut Chart'},
        animation: {animateScale: true, animateRotate: true}
    };

window.onload = function() {
    var inbox = document.getElementById('InboxDoc').getContext('2d');
    var shipped = document.getElementById('ShippedDoc').getContext('2d');
    var statement = document.getElementById('ShippedStat').getContext('2d');

    window.InboxDoc = new Chart(inbox, inbox_config);
    window.ShippedDoc = new Chart(shipped, shipped_config);
    window.ShippedStat = new Chart(statement, statement_config);
};


document.getElementById('InboxChangeCircleSize').addEventListener('click', function() {
    if (window.InboxDoc.options.circumference === Math.PI) {
        window.InboxDoc.options.circumference = 2 * Math.PI;
        window.InboxDoc.options.rotation = -Math.PI / 2;
    } else {
        window.InboxDoc.options.circumference = Math.PI;
        window.InboxDoc.options.rotation = -Math.PI;
    }
    window.InboxDoc.update();
});  
document.getElementById('ShippedChangeCircleSize').addEventListener('click', function() {
    if (window.ShippedDoc.options.circumference === Math.PI) {
        window.ShippedDoc.options.circumference = 2 * Math.PI;
        window.ShippedDoc.options.rotation = -Math.PI / 2;
    } else {
        window.ShippedDoc.options.circumference = Math.PI;
        window.ShippedDoc.options.rotation = -Math.PI;
    }
    window.ShippedDoc.update();
});  
document.getElementById('StatChangeCircleSize').addEventListener('click', function() {
    if (window.ShippedStat.options.circumference === Math.PI) {
        window.ShippedStat.options.circumference = 2 * Math.PI;
        window.ShippedStat.options.rotation = -Math.PI / 2;
    } else {
        window.ShippedStat.options.circumference = Math.PI;
        window.ShippedStat.options.rotation = -Math.PI;
    }
    window.ShippedStat.update();
});  