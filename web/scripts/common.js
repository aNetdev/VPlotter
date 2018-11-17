const urlUpload = 'uploadSVG';
const urlPlot = 'plot';
const urlProgress = 'progress';
const urlStep = 'step';
const urlMoveTo = 'moveTo';

const input = document.getElementById('fileUpload');
const plot = document.getElementById('btnPlot');
const calcCtrls = document.getElementById('divCalcCtrl').getElementsByTagName("input");
const scale = document.getElementById("scale");
const progressBar = document.getElementsByClassName("progress-bar")[0];
const dirDiv = document.getElementById("dirBtns");
const moveTo = document.getElementById("btnMove");
const drawGraph = (data) => {

    sessionStorage.jdataOrg = JSON.stringify(data);

    var cords = {
        x: data.x,
        y: data.y.map((y) => y * -1),
        mode: 'lines',
        type: 'scatter',
        name: 'Path'
    };

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
    pen = data.p

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

    var data = {
        x: [],
        y: [],
        mode: 'lines',
        type: 'scatter',
        name: 'Progress',
        line: {
            color: 'green'
        }

    };
    Plotly.newPlot('divGraphProg', [data], layout);
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
const updateProgress = (cords, prg) => {
    progressBar.style.width = prg + '%'
    progressBar.setAttribute('aria-valuenow', prg);
    console.log(cords);
    Plotly.animate('divGraphProg', {
        data: [{
            x: cords.x,
            y: cords.y
        }],
        traces: [0],
        layout: {},
    }, {
        transition: {
            duration: 500,
            easing: 'cubic-in-out'
        },
        frame: {
            duration: 500
        }
    });
};
const listenForProgress = () => {
    var ws = new WebSocket("ws://" + location.host + "/" + urlProgress);
    cords = {
        x: [],
        y: []
    };
    ws.onopen = function () {
        ws.send("Listening for progress");
        console.log("Message sent...Listening for progress..");
    };

    ws.onmessage = function (evt) {
        var received_msg = evt.data;
        j = JSON.parse(received_msg);
        console.log(j);
        cords.x = cords.x.concat(j.x)
        cords.y = cords.y.concat(j.y)
        updateProgress(cords, j.prg);
    };

    ws.onclose = function () {

        // websocket is closed.
        console.log("Connection is closed...");
    };
}
const onPlot = () => {
    cords = JSON.parse(sessionStorage.jdataMod);
    orgX = document.getElementById('orgX').value;
    orgY = document.getElementById('orgY').value;

    fetch(urlPlot, {
        method: "POST",
        body: JSON.stringify({
            orgX: orgX,
            orgY: orgY,
            cords: cords
        })
    }).then(
        response => response.json()
    ).then(json => {
        switch (json.status) {
            case "Started":
                {
                    // message success and start listening for progress
                    listenForProgress();
                    break;
                }
            case "InProgress":
                {
                    // message another plot is in progress
                    break;
                }
        }
    });
};
const onStep = (dir, steps) => {

    fetch(urlStep, {
        method: "POST",
        body: JSON.stringify({
            dir: dir,
            steps: steps
        })
    }).then(
        response => response.json()
    ).then(json => {

    });

}

const onMoveTo = () => {
    var orgX = Number(document.getElementById("orgX").value);
    var orgY = Number(document.getElementById("orgY").value);

    var curX = Number(document.getElementById("fromX").value);
    var curY = Number(document.getElementById("fromY").value);

    var moveX = Number(document.getElementById("moveX").value);
    var moveY = Number(document.getElementById("moveY").value);
    
    var pen = Number(document.getElementById("selPen").value);

    fetch(urlMoveTo, {
        method: "POST",
        body: JSON.stringify({
            fromX: orgX ? orgX : curX,
            fromY: orgY ? orgY : curY,
            toX: moveX,
            toY: moveY,
            pen: pen
        })
    }).then(() => {
            document.getElementById("fromX").value = moveX;
            document.getElementById("fromY").value = moveY;
        }
    );

}

const onSelectFile = () => {
    upload(input.files[0]);
};
input.addEventListener('change', onSelectFile);
scale.addEventListener('change', onScaleChange);
plot.addEventListener('click', onPlot);
Array.from(calcCtrls).forEach(element => {
    element.addEventListener('change', onCalcChanged);
});
dirDiv.addEventListener('click', (e) => {
    var btn
    if (e.target.tagName == 'BUTTON') {
        btn = e.target;
    } else if (e.target.parentNode && e.target.parentNode.tagName == 'BUTTON') {
        btn = e.target.parentNode;
    }
    var dir = btn.getAttribute("data");
    var steps = document.getElementById('txtSteps').value;
    onStep(dir, steps);
});

moveTo.addEventListener("click", onMoveTo);

onScaleChange();