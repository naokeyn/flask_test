// loadingの制御
window.onload = () => {
    let loading = document.getElementById('loading-canvas')
    loading.classList.add('loaded')
}

const canvas = document.getElementById("myCanvas");
const ctx = canvas.getContext("2d");

let degree = 0;

// canvas の描画
// writen by s.teragami
let draw = () => {
    ctx.save();
    ctx.beginPath();
    ctx.clearRect(0, 0, 400, 400);

    ctx.translate(200, 200);
    ctx.rotate(--degree * 2 * Math.PI / 180);
    ctx.translate(-200, -200);

    ctx.beginPath();
    ctx.arc(200, 200, 80, 0, Math.PI * 2, false);
    ctx.fillStyle = "#d3d3d3";
    ctx.fill();
    ctx.closePath();

    ctx.beginPath();
    ctx.moveTo(200, 200);
    ctx.lineTo(256.65, 143.25);
    ctx.lineTo(256.65, 256.75);
    ctx.fillStyle = "#fff";
    ctx.fill();
    ctx.closePath();


    ctx.beginPath();
    ctx.arc(200, 200, 80, Math.PI * 1.75, Math.PI * 2.25, false);
    ctx.fillStyle = "#fff";
    ctx.fill();
    ctx.closePath();


    ctx.beginPath();
    ctx.arc(200, 200, 80, Math.PI * 0.25, Math.PI * 1.75, false);
    ctx.strokeStyle = "#000000";
    ctx.stroke();
    ctx.closePath();

    ctx.beginPath();
    ctx.moveTo(200, 200);
    ctx.lineTo(256.65, 256.75);
    ctx.stroke();
    ctx.closePath();

    ctx.beginPath();
    ctx.moveTo(200, 200);
    ctx.lineTo(256.65, 143.25);
    ctx.stroke();
    ctx.closePath();

    const str1 = "N,o,w, ,L,o,a,d,i,n,g";
    const c1 = str1.split(",");

    for (let i = 0; i < 11; i++) {
        ctx.fillStyle = "#000000";
        ctx.font = '48px serif';
        ctx.translate(200, 200);
        ctx.rotate(22.5 * Math.PI / 180);
        ctx.translate(-200, -200);

        ctx.fillText(c1[i], 200, 100);
    }

    ctx.restore();
}

setInterval(draw, 20);