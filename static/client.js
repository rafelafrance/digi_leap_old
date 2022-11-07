'use strict';

class CanvasPlus {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.scale = {x: 1.0, y: 1.0};
    }

    cloneCanvas() {
        let newCanvas = document.createElement('canvas');
        let ctx2 = newCanvas.getContext('2d');

        newCanvas.width = this.canvas.width;
        newCanvas.height = this.canvas.height;

        ctx2.drawImage(this.canvas, 0, 0);
        return newCanvas;
    }

    clear() {
        const ctx_w = this.ctx.canvas.width;
        const ctx_h = this.ctx.canvas.height;
        this.ctx.clearRect(0, 0, ctx_w, ctx_h);
    }

    getScale(img_w, img_h) {
        const ctx_w = this.ctx.canvas.width;
        const ctx_h = this.ctx.canvas.height;
        let new_w = img_w;
        let new_h = img_h;

        this.scale = {x: 1.0, y: 1.0}

        if (img_w > ctx_w || img_h > ctx_h) {
            new_h = ctx_h;
            new_w = ctx_w;
            if (img_h > img_w) {
                new_w = new_h * img_w / img_h;
            } else {
                new_h = new_w * img_h / img_w;
            }
            this.scale = {x: new_w / img_w, y: new_h / img_h}
        }
        return [ctx_w, ctx_h, new_w, new_h];
    }
}

const SHEET = new CanvasPlus(document.getElementById('sheet-canvas'));
const LABEL = new CanvasPlus(document.getElementById('label-canvas'));

const IMAGE = new Image();  // Upload images here before putting them into a canvas

const DRAW = {
    active: false,
    start: {x: 0, y: 0},
    end: {x: 0, y: 0},
};

let BEFORE_DRAW = null;  // Save a sheet image before drawing a new box
let CLEAN_SHEET = null;  // Save a sheet image before adding any boxes
let ORIGINAL = null;  // An offscreen canvas that holds the original image
let ALL_LABELS = [];

const readFileAsDataURL = (file) => {
    return new Promise((resolve, reject) => {
        let reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(reader);
        reader.readAsDataURL(file);
    });
}

const loadImage = (url) => new Promise((resolve, reject) => {
    IMAGE.addEventListener('load', () => resolve(IMAGE));
    IMAGE.addEventListener('error', (err) => reject(err));
    IMAGE.src = url;
});

const displaySheet = async () => {
    const image_file = document.getElementById('image-file');
    if (!image_file.value) {
        SHEET.clear();
        return;
    }

    const url = await readFileAsDataURL(image_file.files[0]);
    await loadImage(url);

    const img_w = IMAGE.width;
    const img_h = IMAGE.height;
    ORIGINAL = new CanvasPlus(new OffscreenCanvas(img_w, img_h));
    ORIGINAL.ctx.drawImage(IMAGE, 0, 0, img_w, img_h, 0, 0, img_w, img_h);

    const [ctx_w, ctx_h, new_w, new_h] = SHEET.getScale(img_w, img_h);

    SHEET.clear();
    SHEET.ctx.drawImage(ORIGINAL.canvas, 0, 0, img_w, img_h, 0, 0, new_w, new_h);

    CLEAN_SHEET = SHEET.cloneCanvas();

    ALL_LABELS = [];
    setState();
}

const displayLabel = () => {
    const enabled = ALL_LABELS.length != 0;
    if (!enabled) {
        LABEL.clear();
        return;
    }
    const index = document.getElementById('index');
    const label = ALL_LABELS[index.value - 1];
    const info = document.getElementById('info');

    document.getElementById('text').value = enabled ? label.text : '';
    showLabelInfo(label);

    const img_w = label.right - label.left;
    const img_h = label.bottom - label.top;
    const [ctx_w, ctx_h, new_w, new_h] = LABEL.getScale(img_w, img_h);

    LABEL.clear();
    LABEL.ctx.drawImage(
        ORIGINAL.canvas, label.left, label.top, img_w, img_h, 0, 0, new_w, new_h
    );
}

const canvasOffset = (evt) => {
    const {pageX, pageY} = evt.touches ? evt.touches[0] : evt;
    const x = pageX - SHEET.canvas.offsetLeft;
    const y = pageY - SHEET.canvas.offsetTop;
    return {x, y};
}

const drawBoxes = () => {
    ALL_LABELS.forEach(lb => {
        SHEET.ctx.strokeStyle = lb.type == 'Typewritten' ? '#d95f02' : '#1b9e77';
        SHEET.ctx.lineWidth = 3;
        SHEET.ctx.strokeRect(
            lb.left * SHEET.scale.x,
            lb.top * SHEET.scale.y,
            (lb.right - lb.left) * SHEET.scale.x,
            (lb.bottom - lb.top) * SHEET.scale.y,
        );
    });
}

const insideLabel = (evt, lb) => {
    const pos = canvasOffset(evt);
    pos.x /= SHEET.scale.x;
    pos.y /= SHEET.scale.y;
    return lb.left <= pos.x && lb.right >= pos.x
        && lb.top <= pos.y && lb.bottom >= pos.y;
}

const mouseDownListener = (evt) => {
    const fixing = document.getElementById('fix').value;
    if (fixing == 'Draw') {
        DRAW.start = canvasOffset(evt);
        DRAW.active = true;
        BEFORE_DRAW = SHEET.cloneCanvas();
    } else if (['Typewritten', 'Other', 'Remove'].includes(fixing)) {
    } else {
        return false;
    }
}

const mouseMoveListener = (evt) => {
    if(!DRAW.active) { return };

    DRAW.end = canvasOffset(evt);

    SHEET.ctx.drawImage(BEFORE_DRAW, 0, 0);

    SHEET.ctx.strokeStyle = '#d95f02';
    SHEET.ctx.lineWidth = 3;
    SHEET.ctx.strokeRect(
        DRAW.start.x,
        DRAW.start.y,
        DRAW.end.x - DRAW.start.x,
        DRAW.end.y - DRAW.start.y,
    );
}

const mouseUpListener = (evt) => {
    const fix = document.getElementById('fix').value;
    if (fix == 'Draw') {
        ALL_LABELS.push({
            type: 'Typewritten',
            left: Math.min(DRAW.start.x, DRAW.end.x) / SHEET.scale.x,
            top: Math.min(DRAW.start.y, DRAW.end.y) / SHEET.scale.y,
            right: Math.max(DRAW.start.x, DRAW.end.x) / SHEET.scale.x,
            bottom: Math.max(DRAW.start.y, DRAW.end.y) / SHEET.scale.y,
            conf: 1.0,
            text: '',
        });
        setState();
        document.getElementById('index').value = ALL_LABELS.length;
        displayLabel();
    } else if (['Typewritten', 'Other'].includes(fix)) {
        ALL_LABELS.forEach((lb, i) => {
            if (insideLabel(evt, lb)) {
                lb.type = fix;
                drawBoxes();
                setState();
                document.getElementById('index').value = i + 1;
                displayLabel();
            }
        });
    } else if (fix == 'Remove') {
        SHEET.ctx.drawImage(CLEAN_SHEET, 0, 0);
        ALL_LABELS = ALL_LABELS.filter(lb => !insideLabel(evt, lb));
        drawBoxes();
        setState();
    }
    DRAW.active = false;
}

const findLabels = () => {
    let req = new XMLHttpRequest();
    const button = document.getElementById('find-labels');
    button.classList.add('loading');

    const labelsFound = () => {
        if (req.readyState === XMLHttpRequest.DONE) {
            if (req.status === 200) {
                ALL_LABELS = JSON.parse(req.responseText);
                ALL_LABELS = JSON.parse(ALL_LABELS);  // WTF?!
                drawBoxes();
                setState();
            } else {
                let err = JSON.parse(req.responseText);
                alert(`Find labels error: ${err.detail[0].msg}`);
            }
        }
        button.classList.remove('loading');
    }
    const data = new FormData();
    const image_file = document.getElementById('image-file');
    data.append('sheet', image_file.files[0]);
    data.append('conf', document.getElementById('conf').value);

    req.open('POST', `${window.location.href}find-labels`, true);
    req.onreadystatechange = labelsFound;
    req.setRequestHeader('Conteint-Type', 'multipart/form-data');
    req.overrideMimeType('multipart/form-data;');
    req.send(data);
}


const ocrLabels = () => {
    let req = new XMLHttpRequest();
    const button = document.getElementById('ocr-labels');
    button.classList.add('loading');

    const labelsOcred = () => {
        if (req.readyState === XMLHttpRequest.DONE) {
            if (req.status === 200) {
                let labels = JSON.parse(req.responseText);
                ALL_LABELS = JSON.parse(labels);  // WTF?!
                setState();
            } else {
                let err = JSON.parse(req.responseText);
                alert(`OCR labels error: ${err.detail[0].msg}`);
            }
        }
        button.classList.remove('loading');
    }
    const data = new FormData();
    const image_file = document.getElementById('image-file');
    data.append('labels', JSON.stringify(ALL_LABELS));
    data.append('sheet', image_file.files[0]);
    data.append('filter', 'typewritten');

    req.open('POST', `${window.location.href}ocr-labels`, true);
    req.onreadystatechange = labelsOcred;
    req.setRequestHeader('Conteint-Type', 'multipart/form-data');
    req.overrideMimeType('multipart/form-data;');
    req.send(data);
}

const setState = () => {
    const image_file = document.getElementById('image-file');
    const image_selected = !!image_file.value;
    const type = document.querySelector('input[name="image-type"]:checked').value;
    const has_labels = ALL_LABELS.length != 0;

    if (!image_selected) { ALL_LABELS = []; }

    const sheet_ready = image_selected && type == 'sheet';
    const can_ocr = image_selected && (type == 'label' || (type == 'sheet' && has_labels));
    document.getElementById('find-labels').disabled = !image_selected || type != 'sheet';
    document.getElementById('ocr-labels').disabled = !can_ocr;
    document.getElementById('conf').disabled = !sheet_ready;
    document.getElementById('fix').disabled = !sheet_ready || !has_labels;

    const index = document.getElementById('index');
    index.disabled = !has_labels;
    index.min = has_labels ? '1' : '0';
    index.max = has_labels ? `${ALL_LABELS.length}` : '0';
    const max = parseInt(index.max);
    const val = isNaN(parseInt(index.value)) ? 1 : parseInt(index.value);
    index.value = has_labels ? `${Math.min(max, val)}` : '';

    const textarea = document.getElementById('text');
    textarea.disabled = !has_labels;
    textarea.value = has_labels ? ALL_LABELS[0].text : '';

    const info = document.getElementById('info');
    info.value = has_labels ? showLabelInfo(ALL_LABELS[0]) : '';
    displayLabel();
    showConf();
}

const showLabelInfo = (label) => {
    const info = document.getElementById('info');
    const type = document.querySelector('input[name="image-type"]:checked').value;
    if (type == 'sheet') {
        const conf = label.conf ? `conf ${label.conf}, ` : ''
        info.value = `type: ${label.type}, ${conf} x: ${label.left}, y: ${label.top}`;
    } else {
        info.value = '';
    }
}

const showConf = () => {
    document.getElementById('show-conf').value = conf.value;
}

const reset = () => {
    ALL_LABELS = [];
    setState();
    SHEET.ctx.drawImage(CLEAN_SHEET, 0, 0);
}

const nextLabel = () => {
    const index = document.getElementById('index');
    index.stepUp();
    displayLabel();
}

const prevLabel = () => {
    const index = document.getElementById('index');
    index.stepDown();
    displayLabel();
}

(() => {
    displaySheet();

    document.getElementById('image-file')
        .addEventListener('change', async (evt) => { displaySheet(); }, false);

    document.getElementById('find-labels')
        .addEventListener('click', findLabels);

    document.getElementById('ocr-labels')
        .addEventListener('click', ocrLabels);

    document.getElementById('index')
        .addEventListener('change', displayLabel);

    document.getElementById('prev-label')
        .addEventListener('click', prevLabel);

    document.getElementById('next-label')
        .addEventListener('click', nextLabel);

    document.getElementById('text')
        .addEventListener('change', () => {
        const index = document.getElementById('index');
        ALL_LABELS[index.value - 1].text = document.getElementById('text').value;
    });

    document.getElementById('conf')
        .addEventListener('input', showConf);

    document.querySelectorAll('input[name="image-type"]')
        .forEach(r => r.addEventListener('change', reset));

    SHEET.canvas.addEventListener('mousedown', mouseDownListener);
    SHEET.canvas.addEventListener('mousemove', mouseMoveListener);
    SHEET.canvas.addEventListener('mouseup', mouseUpListener);

    let width = document.querySelector('.sheet').clientWidth;
    SHEET.ctx.canvas.width = width;
    SHEET.ctx.canvas.height = width;
    LABEL.ctx.canvas.width = width;
    LABEL.ctx.canvas.height = width;
})();
