const url = 'uploadSVG';
const input = document.getElementById('fileUpload');

const drawGraph = (data) => {

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

    Plotly.newPlot('divGraph', data);


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
        console.log(json) // Handle the success response object
        drawGraph(json)
    }
    ).catch(
        error => console.log(error) // Handle the error response object
    );
};

const onSelectFile = () => upload(input.files[0]);
input.addEventListener('change', onSelectFile);