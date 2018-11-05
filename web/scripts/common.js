const url = 'uploadSVG';
const input = document.getElementById('fileUpload');
const calcCtrls = document.getElementById('divCalcCtrl').getElementsByTagName("input");

const drawGraph = (data) => {

    sessionStorage.jdata = JSON.stringify(data);

    var moveTo = {
        x: data.moveToX,
        y: data.moveToY,
        mode: 'markers',
        type: 'scatter'
    };

    var lineTo = {
        x: data.lineToX,
        y: data.lineToY,
        mode: 'lines',
        type: 'scatter'
    };

    var data = [moveTo, lineTo];

    Plotly.newPlot('divGraphOrg', data);


}
const upload = (file) => {
    fetch(url, { // Your POST endpoint
        method: 'POST',
        //   headers: {
        //     "Content-Type": ""
        //   },
        body: file // This is your file object
    }).then(
        response => response.json()
    ).then((json) => {
        console.log(json); // Handle the success response object
        drawGraph(json);
    }
    ).catch(
        error => console.log(error) // Handle the error response object
    );
};

const updateGraph = (scale, xOffset, yOffset) => {
    data = JSON.parse(sessionStorage.jdata);
    newMoveToX = data.moveToX.map(x => {
        return Math.round(((x * scale) + xOffset))
    });
    newMoveToY = data.moveToY.map(y => {
        return Math.round(((y * scale) + xOffset))
    });
    newLineToX = data.lineToX.map(x => {
        return Math.round(((x * scale) + xOffset))
    });
    newLineToY = data.lineToY.map(y => {
        return Math.round(((y * scale) + xOffset))
    });


    var moveTo = {
        x: newMoveToX,
        y: newMoveToY,
        mode: 'markers',
        type: 'scatter'
    };

    var lineTo = {
        x: newLineToX,
        y: newLineToY,
        mode: 'lines',
        type: 'scatter'
    };

    var data = [moveTo, lineTo];

    Plotly.newPlot('divGraphCalc', data);
}
const watchCalcControls = () => {
    let scale = Number(document.getElementById("scale").value);
    let xOffset = Number(document.getElementById("xOffset").value);
    let yOffset = Number(document.getElementById("yOffset").value);
    updateGraph(scale, xOffset, yOffset);
};



const onSelectFile = () => upload(input.files[0]);
input.addEventListener('change', onSelectFile);

Array.from(calcCtrls).forEach(element => {
    element.addEventListener('change', watchCalcControls);
});



