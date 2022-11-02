'use strict';

const CANVAS = document.querySelector('canvas');
const CTX = CANVAS.getContext('2d');
CTX.canvas.width = 1000;
CTX.canvas.height = 1000;

let OLD_CANVAS = null;

let SCALE = {x: 1.0, y: 1.0};
let LABELS = [];

const IMAGE = new Image();

let START_POS = {x: 0, y: 0};
let END_POS = {x: 0, y: 0};
let DRAWING = false;


const cloneCanvas = (oldCanvas)  => {
    let newCanvas = document.createElement('canvas');
    let ctx2 = newCanvas.getContext('2d');

    newCanvas.width = oldCanvas.width;
    newCanvas.height = oldCanvas.height;

    ctx2.drawImage(oldCanvas, 0, 0);

    return newCanvas;
}

const canvasOffset = (evt) => {
    const {pageX, pageY} = evt.touches ? evt.touches[0] : evt;
    const x = pageX - CANVAS.offsetLeft;
    const y = pageY - CANVAS.offsetTop;
    return {x, y};
}

const drawRectangle = async () => {
    CTX.strokeStyle = "#d95f02";
    CTX.lineWidth = 3;
    CTX.strokeRect(
        START_POS.x,
        START_POS.y,
        END_POS.x - START_POS.x,
        END_POS.y - START_POS.y,
    );
}

const drawBoxes = () => {
    LABELS.forEach((lb) => {
        CTX.strokeStyle = lb.type.toLowerCase() == "typewritten" ? "#d95f02" : "#1b9e77";
        CTX.lineWidth = 3;
        CTX.strokeRect(
            lb.left * SCALE.x,
            lb.top * SCALE.y,
            (lb.right - lb.left) * SCALE.x,
            (lb.bottom - lb.top) * SCALE.y,
        );
    });
}

const mouseDownListener = (evt) => {
    START_POS = canvasOffset(evt);
    DRAWING = true;
    OLD_CANVAS = cloneCanvas(CANVAS);
}

const mouseMoveListener = (evt) => {
  if(!DRAWING) { return };

  END_POS = canvasOffset(evt);

  CTX.drawImage(OLD_CANVAS, 0, 0);

  drawRectangle();
}

const mouseUpListener = (evt) => {
  DRAWING = false;
}

const loadImage = (url) => new Promise((resolve, reject) => {
    IMAGE.addEventListener('load', () => resolve(IMAGE));
    IMAGE.addEventListener('error', (err) => reject(err));
    IMAGE.src = url;
});

function readFileAsDataURL(file) {
    return new Promise((resolve, reject) => {
        let reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(reader);
        reader.readAsDataURL(file);
    });
}

async function displaySheet() {
    if (!files.value) { return; }

    const url = await readFileAsDataURL(files.files[0]);
    await loadImage(url);

    let width = IMAGE.width;
    let height = IMAGE.height;

    SCALE.x = 1.0;
    SCALE.y = 1.0;

    if (IMAGE.width > CTX.canvas.width || IMAGE.height > CTX.canvas.height) {
        if (IMAGE.height > IMAGE.width) {
            let ratio = IMAGE.width / IMAGE.height;
            height = CTX.canvas.height;
            width = height * ratio;
        } else {
            let ratio = IMAGE.height / IMAGE.width;
            width = CTX.canvas.width;
            height = width * ratio;
        }
        SCALE.y = height / IMAGE.height;
        SCALE.x = width / IMAGE.width;
    }

    CTX.clearRect(0, 0, CTX.canvas.width, CTX.canvas.height);
    CTX.drawImage(IMAGE, 0, 0, IMAGE.width, IMAGE.height, 0, 0, width, height);
}

const findLabels = () => {
    let req = new XMLHttpRequest();
    const labelsFound = () => {
        if (req.readyState === XMLHttpRequest.DONE) {
            if (req.status === 200) {
                LABELS = JSON.parse(req.responseText);
                LABELS = JSON.parse(LABELS);  // WTF?!
                drawBoxes();
            } else {
                alert('Find labels error');
            }
        }
    }
    const data = new FormData();
    data.append('sheet', files.files[0]);
    data.append('conf', document.getElementById('conf').value);

    req.open('POST', `${window.location.href}find-labels`, true);
    req.onreadystatechange = labelsFound;
    req.setRequestHeader('Conteint-Type', 'multipart/form-data');
    req.overrideMimeType('multipart/form-data;');
    req.send(data);
}


const ocrLabels = () => {
    let req = new XMLHttpRequest();
    const labelsOcred = () => {
        if (req.readyState === XMLHttpRequest.DONE) {
            if (req.status === 200) {
                let labels = JSON.parse(req.responseText);
                labels = JSON.parse(labels);  // WTF?!
                LABELS = labels;
                console.log(labels)
                let text = "";
                labels.forEach((lb) => {
                    text += lb.text;
                });
                document.querySelector('textarea').value = text;
            } else {
                alert('OCR labels error');
            }
        }
    }
    const data = new FormData();
    data.append('labels', JSON.stringify(LABELS));
    data.append('sheet', files.files[0]);

    req.open('POST', `${window.location.href}ocr-labels`, true);
    req.onreadystatechange = labelsOcred;
    req.setRequestHeader('Conteint-Type', 'multipart/form-data');
    req.overrideMimeType('multipart/form-data;');
    req.send(data);
}


document
    .getElementById('files')
    .addEventListener('change', async (evt) => { displaySheet(); }, false);

document
    .getElementById('find-labels')
    .addEventListener('click', findLabels);

document
    .getElementById('ocr-labels')
    .addEventListener('click', ocrLabels);

CANVAS.addEventListener('mousedown', mouseDownListener);
CANVAS.addEventListener('mousemove', mouseMoveListener);
CANVAS.addEventListener('mouseup', mouseUpListener);

displaySheet();
