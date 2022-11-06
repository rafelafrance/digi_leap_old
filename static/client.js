'use strict';

const CANVAS = document.querySelector('canvas');
const CTX = CANVAS.getContext('2d');
CTX.canvas.width = 1000;
CTX.canvas.height = 1000;

let BEFORE_DRAW = null;
let BEFORE_BOXES = null;

let SCALE = {x: 1.0, y: 1.0};
let LABELS = [];

const IMAGE = new Image();

let START_POS = {x: 0, y: 0};
let END_POS = {x: 0, y: 0};
let FIXING = false;


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
    BEFORE_BOXES = cloneCanvas(CANVAS);

    LABELS = [];
    setState();
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
    LABELS.forEach(lb => {
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
    const fix = document.getElementById('fix').value;
    if (fix == "Draw") {
        START_POS = canvasOffset(evt);
        FIXING = true;
        BEFORE_DRAW = cloneCanvas(CANVAS);
    } else if (["Typewritten", "Other", "Remove"].includes(fix)) {
    } else {
        return false;
    }
}

const mouseMoveListener = (evt) => {
    if(!FIXING) { return };

    END_POS = canvasOffset(evt);

    CTX.drawImage(BEFORE_DRAW, 0, 0);

    drawRectangle();
}

const inLabel = (evt, lb) => {
    const pos = canvasOffset(evt);
    pos.x /= SCALE.x;
    pos.y /= SCALE.y;
    return lb.left <= pos.x && lb.right >= pos.x && lb.top <= pos.y && lb.bottom >= pos.y;
}

const mouseUpListener = (evt) => {
    const fix = document.getElementById('fix').value;
    if (fix == 'Draw') {
        // Build new label
    } else if (["Typewritten", "Other"].includes(fix)) {
        const pos = canvasOffset(evt);
        LABELS.forEach(lb => {
            if (inLabel(evt, lb)) { lb.type = fix; }
        });
        drawBoxes();
    } else if (fix == "Remove") {
        CTX.drawImage(BEFORE_BOXES, 0, 0);
        LABELS = LABELS.filter(lb => !inLabel(evt, lb));
        drawBoxes();
    }
    FIXING = false;
}

const findLabels = () => {
    let req = new XMLHttpRequest();
    const labelsFound = () => {
        if (req.readyState === XMLHttpRequest.DONE) {
            if (req.status === 200) {
                LABELS = JSON.parse(req.responseText);
                LABELS = JSON.parse(LABELS);  // WTF?!
                drawBoxes();
                setState();
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
                labels.forEach(lb => {
                    text += lb.text;
                });
                document.querySelector('textarea').value = text;
                setState();
            } else {
                alert('OCR labels error');
            }
        }
    }
    const data = new FormData();
    data.append('labels', JSON.stringify(LABELS));
    data.append('sheet', files.files[0]);
    data.append(
        "filter",
        document.querySelector('input[name="which"]:checked').value,
    );

    req.open('POST', `${window.location.href}ocr-labels`, true);
    req.onreadystatechange = labelsOcred;
    req.setRequestHeader('Conteint-Type', 'multipart/form-data');
    req.overrideMimeType('multipart/form-data;');
    req.send(data);
}

const updateText = () => {
    const index = document.getElementById("index");
    const textarea = document.querySelector("textarea");
    const active = LABELS.length != 0; // && !args.disabled;
    const label = LABELS[index.value - 1];
    textarea.value = active ? label.text : "";
    info.value = !active ? "" : `${label.type} (${label.left}, ${label.top})`;
}

const setState = () => {
    const image_selected = !!files.value;
    const type = document.querySelector('input[name="type"]:checked').value;
    const has_labels = LABELS.length != 0;
    const has_text = LABELS.some(lb => !!lb.text);

    const toggleImageType = ({image_selected, type, has_labels}) => {
        const sheet_ready = image_selected && type == "sheet";
        const labels_ready = sheet_ready && has_labels;
        const can_ocr = image_selected && (type == "label" || (type == "sheet" && has_labels));
        document.getElementById("find-labels").disabled = !image_selected || type != "sheet";
        document.getElementById("ocr-labels").disabled = !can_ocr;
        document.getElementById("conf").disabled = !sheet_ready;
        document.querySelectorAll('input[name="which"]').forEach(r => r.disabled = !sheet_ready);
        document.getElementById("fix").disabled = !labels_ready;
        document.getElementById("save-labels").disabled = !labels_ready;
    }

    const toggleText = ({has_text}) => {
        const index = document.getElementById("index");
        index.disabled = !has_text;
        index.min = has_text ? "1" : "0";
        index.max = has_text ? `${LABELS.length}` : "0";
        index.value = has_text ? "1" : "";

        const textarea = document.querySelector("textarea");
        textarea.disabled = !has_text;
        textarea.value = has_text ? LABELS[0].text : "";

        const info = document.getElementById("info");
        info.value = has_text ? `${LABELS[0].type} (${LABELS[0].left}, ${LABELS[0].top})` : "";

        document.getElementById("save-text").disabled = !has_text;
    }

    if (!image_selected) {
        LABELS = [];
    }
    toggleImageType({image_selected, type, has_labels});
    toggleText({has_text});
}


const initialize = () => {
    displaySheet();
    setState();
    showConf();

    document.getElementById('files')
        .addEventListener('change', async (evt) => { displaySheet(); }, false);

    document.getElementById('find-labels')
        .addEventListener('click', findLabels);

    document.getElementById('ocr-labels')
        .addEventListener('click', ocrLabels);

    document.getElementById('index')
        .addEventListener('change', updateText);

    document.querySelector('textarea')
        .addEventListener('change', () => {
        const index = document.getElementById("index");
        LABELS[index.value - 1].text = document.querySelector("textarea").value;
    });

    document.getElementById('conf')
        .addEventListener('change', () => {
            document.getElementById("show-conf").value = conf.value;
        });

    document.querySelectorAll('input[name="type"]')
        .forEach(r => r.addEventListener('change', setState));


    CANVAS.addEventListener('mousedown', mouseDownListener);
    CANVAS.addEventListener('mousemove', mouseMoveListener);
    CANVAS.addEventListener('mouseup', mouseUpListener);
}

initialize();
