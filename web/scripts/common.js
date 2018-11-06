const urlUpload = 'uploadSVG';
const urlPlot = 'plot';

const input = document.getElementById('fileUpload');
const plot = document.getElementById('btnPlot');
const calcCtrls = document.getElementById('divCalcCtrl').getElementsByTagName("input");
const scale = document.getElementById("scale");
const drawGraph = (data) => {

    sessionStorage.jdataOrg = JSON.stringify(data);

    var cords = {
        x: data.x,
        y: data.y.map((y) => y * -1),
        mode: 'lines',
        type: 'scatter',
        name: 'Path'    };

    var data = [cords];

    Plotly.newPlot('divGraphOrg', data);
    onCalcChanged(); //trigger right graph

}
const upload = (file) => {
    fetch(urlUpload, {
        method: 'POST',
        body: file // This is your file object
    }).then(
        response => response.json()
    ).then((json) => {
        console.log(json); // Handle the success response object
        drawGraph(json);
    }).catch(
        error => console.log(error) // Handle the error response object
    );
};

const updateGraph = (scale, xOffset, yOffset) => {
    data = JSON.parse(sessionStorage.jdataOrg);
    newX = data.x.map(x => Math.round(((x * scale) + xOffset)));
    newY = data.y.map(y => Math.round(((y * scale) + yOffset)));
    pen =data.p

    var cords = {
        x: newX,
        y: newY,
        mode: 'lines',
        type: 'scatter',
        name: 'Path'
    };
   
    var layout = {
        xaxis: {
            range: [15, 350]
        },
        yaxis: {
            range: [400, 15]
        }
    };
    var data = [cords];

    sessionStorage.jdataMod = JSON.stringify({
        x: newX,
        y: newY,
        p: pen        
    });

    Plotly.newPlot('divGraphCalc', data, layout);
}
const onCalcChanged = () => {
    let scale = Number(document.getElementById("scale").value) / 100;
    let xOffset = Number(document.getElementById("xOffset").value);
    let yOffset = Number(document.getElementById("yOffset").value);
    updateGraph(scale, xOffset, yOffset);
};

const onScaleChange = () => {
    document.getElementById('txtRange').innerText = document.getElementById("scale").value + '%';
};

const onPlot = () => {

    fetch(urlPlot, {
        method: "POST",
        body: sessionStorage.jdataMod
    });
};

const onSelectFile = () => upload(input.files[0]);
input.addEventListener('change', onSelectFile);
scale.addEventListener('change', onScaleChange);
plot.addEventListener('click', onPlot);
Array.from(calcCtrls).forEach(element => {
    element.addEventListener('change', onCalcChanged);
});
onScaleChange();