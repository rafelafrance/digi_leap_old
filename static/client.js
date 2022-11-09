'use strict';

class CanvasPlus {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.scale = { x: 1.0, y: 1.0 };
        this.image_width = 0;
        this.image_height = 0;
    }
    setCanvasSize(size) {
        this.ctx.canvas.width = size;
        this.ctx.canvas.height = size;
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

        this.scale = { x: 1.0, y: 1.0 };

        if (img_w > ctx_w || img_h > ctx_h) {
            new_h = ctx_h;
            new_w = ctx_w;
            if (img_h > img_w) {
                new_w = new_h * img_w / img_h;
            } else {
                new_h = new_w * img_h / img_w;
            }
            this.scale = { x: new_w / img_w, y: new_h / img_h };
        }
        this.image_width = new_w;
        this.image_height = new_h
        return [ctx_w, ctx_h, new_w, new_h];
    }
    canvasOffset(event) {
        const { pageX, pageY } = event.touches ? event.touches[0] : event;
        const x = pageX - this.canvas.offsetLeft;
        const y = pageY - this.canvas.offsetTop;
        return { x, y };
    }
    insideImage(event) {
        const pos = this.canvasOffset(event);
        return pos.x < this.image_width && pos.y < this.image_height;
    }
}

const SHEET = new CanvasPlus(document.getElementById('sheet-canvas'));
const LABEL = new CanvasPlus(document.getElementById('label-canvas'));

const IMAGE = new Image();  // Upload images here before putting them into a canvas

class Draw {
    constructor() {
        this.reset();
    }
    reset() {
        this.drawing = false;
        this.canDraw = false;
        this.start = { x: 0, y: 0 };
        this.end = { x: 0, y: 0 };
        this.left = 0;
        this.top = 0;
        this.right = 0;
        this.bottom = 0;
    }
    scale(scaleBy) {
        this.left = Math.min(this.start.x, this.end.x) / scaleBy.x;
        this.top = Math.min(this.start.y, this.end.y) / scaleBy.y;
        this.right = Math.max(this.start.x, this.end.x) / scaleBy.x;
        this.bottom = Math.max(this.start.y, this.end.y) / scaleBy.y;
    }
    tooSmall() {
        return (this.right - this.left) < 100 || (this.bottom - this.top) < 100;
    }
    strokeRect() {
        return [
            this.start.x,
            this.start.y,
            this.end.x - this.start.x,
            this.end.y - this.start.y,
        ];
    }
}

const DRAW = new Draw();

let CANVAS_BEFORE_BOX = null;  // Save a sheet image before drawing a new box
let CANVAS_BEFORE_ALL_BOXES = null;  // Save a sheet image before adding any boxes
let FULL_SIZE = null;  // An offscreen canvas that holds the original image
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

const imageFileSelected = async () => {
    const imagefile = document.getElementById('image-file');
    DRAW.reset();
    if (!imagefile.value) {
        SHEET.clear();
        return;
    }

    const url = await readFileAsDataURL(imagefile.files[0]);
    await loadImage(url);

    const img_w = IMAGE.width;
    const img_h = IMAGE.height;
    FULL_SIZE = new CanvasPlus(new OffscreenCanvas(img_w, img_h));
    FULL_SIZE.ctx.drawImage(IMAGE, 0, 0, img_w, img_h, 0, 0, img_w, img_h);

    const [ctx_w, ctx_h, new_w, new_h] = SHEET.getScale(img_w, img_h);

    SHEET.clear();
    SHEET.ctx.drawImage(FULL_SIZE.canvas, 0, 0, img_w, img_h, 0, 0, new_w, new_h);

    CANVAS_BEFORE_ALL_BOXES = SHEET.cloneCanvas();

    ALL_LABELS = [];
    setState();
}

const displayLabel = () => {
    const enabled = ALL_LABELS.length != 0;
    if (!enabled) {
        LABEL.clear();
        return;
    }
    const labelIndex = document.getElementById('label-index');
    let idx = labelIndex.value;
    if (idx < 1) {
        idx = 1;
        labelIndex.value = `1`;
    }
    const label = ALL_LABELS[idx - 1];
    const labelInfo = document.getElementById('label-info');

    document.getElementById('text').value = enabled ? label.text : '';
    showLabelInfo(label);

    const img_w = label.right - label.left;
    const img_h = label.bottom - label.top;
    const [ctx_w, ctx_h, new_w, new_h] = LABEL.getScale(img_w, img_h);

    LABEL.clear();
    const imageType = document.querySelector('input[name="image-type"]:checked').value;
    if (imageType == 'sheet') {
        LABEL.ctx.drawImage(
            FULL_SIZE.canvas, label.left, label.top, img_w, img_h, 0, 0, new_w, new_h
        );
    }
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

// const canvasOffset = (evt) => {
//     const { pageX, pageY } = evt.touches ? evt.touches[0] : evt;
//     const x = pageX - SHEET.canvas.offsetLeft;
//     const y = pageY - SHEET.canvas.offsetTop;
//     return { x, y };
// }

const insideLabel = (evt, lb) => {
    const pos = SHEET.canvasOffset(evt);
    pos.x /= SHEET.scale.x;
    pos.y /= SHEET.scale.y;
    return lb.left <= pos.x && lb.right >= pos.x
        && lb.top <= pos.y && lb.bottom >= pos.y;
}

const mouseDown = (evt) => {
    if (!DRAW.canDraw || !SHEET.insideImage(evt)) { return false; }
    const labelFixOp = document.getElementById('label-fix-op').value;
    if (labelFixOp == 'Draw') {
        DRAW.start = SHEET.canvasOffset(evt);
        DRAW.end = DRAW.start;
        DRAW.drawing = true;
        CANVAS_BEFORE_BOX = SHEET.cloneCanvas();
    }
}

const mouseMove = (evt) => {
    if (!DRAW.drawing) { return };
    DRAW.end = SHEET.canvasOffset(evt);
    SHEET.ctx.drawImage(CANVAS_BEFORE_BOX, 0, 0);
    SHEET.ctx.strokeStyle = '#d95f02';
    SHEET.ctx.lineWidth = 3;
    const [x, y, w, h] = DRAW.strokeRect();
    SHEET.ctx.strokeRect(x, y, w, h);
}

const mouseUp = (evt) => {
    if (!DRAW.canDraw) { return false; }
    const labelFixOp = document.getElementById('label-fix-op').value;
    if (labelFixOp == 'Draw' && DRAW.drawing) {
        DRAW.scale(SHEET.scale);
        if (!DRAW.tooSmall()) {
            ALL_LABELS.push({
                type: 'Typewritten',
                left: DRAW.left,
                top: DRAW.top,
                right: DRAW.right,
                bottom: DRAW.bottom,
                conf: 1.0,
                text: '',
            });
            setState();
            document.getElementById('label-index').value = ALL_LABELS.length;
            displayLabel();
        } else {
            SHEET.ctx.drawImage(CANVAS_BEFORE_BOX, 0, 0);
            alert('The new label is too small.');
        }
        DRAW.drawing = false;
    } else if (['Typewritten', 'Other'].includes(labelFixOp)) {
        ALL_LABELS.forEach((lb, i) => {
            if (insideLabel(evt, lb)) {
                lb.type = labelFixOp;
                drawBoxes();
                setState();
                document.getElementById('label-index').value = i + 1;
                displayLabel();
            }
        });
    } else if (labelFixOp == 'Remove') {
        SHEET.ctx.drawImage(CANVAS_BEFORE_ALL_BOXES, 0, 0);
        ALL_LABELS = ALL_LABELS.filter(lb => !insideLabel(evt, lb));
        drawBoxes();
        setState();
    }
    DRAW.drawing = false;
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
                DRAW.canDraw = true;
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
    const imageFile = document.getElementById('image-file');
    data.append('sheet', imageFile.files[0]);
    data.append('conf', document.getElementById('finder-conf').value);

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
    const imageFile = document.getElementById('image-file');
    data.append('labels', JSON.stringify(ALL_LABELS));
    data.append('sheet', imageFile.files[0]);
    data.append('filter', 'typewritten');

    req.open('POST', `${window.location.href}ocr-labels`, true);
    req.onreadystatechange = labelsOcred;
    req.setRequestHeader('Conteint-Type', 'multipart/form-data');
    req.overrideMimeType('multipart/form-data;');
    req.send(data);
}

const setState = () => {
    const imageFile = document.getElementById('image-file');
    const imageSelected = !!imageFile.value;
    const type = document.querySelector('input[name="image-type"]:checked').value;
    const hasLabels = ALL_LABELS.length != 0;

    if (!imageSelected) {
        ALL_LABELS = [];
        DRAW.canDraw = false;
    }

    const sheetReady = imageSelected && type == 'sheet';
    const canOcr = imageSelected
        && (type == 'label' || (type == 'sheet' && hasLabels));

    document.getElementById('find-labels').disabled = (
        !imageSelected || type != 'sheet');
    document.getElementById('ocr-labels').disabled = !canOcr;
    document.getElementById('finder-conf').disabled = !sheetReady;
    document.getElementById('label-fix-op').disabled = !sheetReady || !DRAW.canDraw;
    document.getElementById('save-labels').disabled = !sheetReady || !hasLabels;
    document.getElementById('save-text').disabled = !ALL_LABELS.some(lb => !!lb.text);

    const labelIndex = document.getElementById('label-index');

    labelIndex.disabled = !hasLabels;
    labelIndex.min = hasLabels ? '1' : '0';
    labelIndex.max = hasLabels ? `${ALL_LABELS.length}` : '0';

    const max = parseInt(labelIndex.max);
    const val = isNaN(parseInt(labelIndex.value)) ? 1 : parseInt(labelIndex.value);

    labelIndex.value = hasLabels ? `${Math.min(max, val)}` : '';

    const textarea = document.getElementById('text');

    textarea.disabled = !hasLabels;
    textarea.value = hasLabels ? ALL_LABELS[0].text : '';

    const labelInfo = document.getElementById('label-info');
    labelInfo.value = hasLabels ? showLabelInfo(ALL_LABELS[0]) : '';

    displayLabel();
    showFinderConf();
}

const showLabelInfo = (label) => {
    const labelInfo = document.getElementById('label-info');
    const type = document.querySelector('input[name="image-type"]:checked').value;
    if (type == 'sheet') {
        const conf = label.conf ? `conf ${label.conf}, ` : ''
        labelInfo.value = `type: ${label.type}, ${conf} `
            + `x: ${label.left}, y: ${label.top}`;
    } else {
        labelInfo.value = '';
    }
}

const showFinderConf = () => {
    const conf = document.getElementById('finder-conf').value;
    document.getElementById('show-finder-conf').value = conf;
}

const nextLabelIndex = () => {
    const labelIndex = document.getElementById('label-index');
    labelIndex.stepUp();
    displayLabel();
}

const prevLabelIndex = () => {
    const labelIndex = document.getElementById('label-index');
    labelIndex.stepDown();
    displayLabel();
}

const reset = () => {
    ALL_LABELS = [];
    setState();
    SHEET.ctx.drawImage(CANVAS_BEFORE_ALL_BOXES, 0, 0);
    DRAW.reset();
}

function removeExtension(fileName) {
    return fileName.substring(0, fileName.lastIndexOf('.')) || fileName;
}

const saveText = async () => {
    const imageFile = document.getElementById('image-file');
    const blob = new Blob([JSON.stringify(ALL_LABELS)], {type: 'text/json'});
    const a = document.createElement('a');
    a.download = `${removeExtension(imageFile.files[0].name)}.json`;
    a.href = URL.createObjectURL(blob);
    a.click();
    a.remove();
}

const saveLabels = () => {
    const imageFile = document.getElementById('image-file');
    const baseName = `${removeExtension(imageFile.files[0].name)}`;

    ALL_LABELS.forEach((lb, i) => {
        const img_w = lb.right - lb.left;
        const img_h = lb.bottom - lb.top;
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        ctx.canvas.width = img_w;
        ctx.canvas.height = img_h;

        ctx.drawImage(
            FULL_SIZE.canvas, lb.left, lb.top, img_w, img_h, 0, 0, img_w, img_h
        );
        const a = document.createElement('a');
        a.download = `${baseName}_${i}_${lb.type}.png`;
        a.href = canvas.toDataURL('image/png');
        a.click();
        a.remove();
        canvas.remove();
    });
}

(() => {
    imageFileSelected();

    document.getElementById('image-file')
        .addEventListener('change', async (evt) => { imageFileSelected(); }, false);

    document.getElementById('find-labels')
        .addEventListener('click', findLabels);

    document.getElementById('ocr-labels')
        .addEventListener('click', ocrLabels);

    document.getElementById('label-index')
        .addEventListener('change', displayLabel);

    document.getElementById('prev-label-index')
        .addEventListener('click', prevLabelIndex);

    document.getElementById('next-label-index')
        .addEventListener('click', nextLabelIndex);

    document.getElementById('save-text')
        .addEventListener('click', saveText);

    document.getElementById('save-labels')
        .addEventListener('click', saveLabels);

    document.getElementById('text')
        .addEventListener('change', () => {
            const labelIndex = document.getElementById('label-index').value;
            const text = document.getElementById('text').value;
            ALL_LABELS[labelIndex.value - 1].text = text;
        });

    document.getElementById('finder-conf')
        .addEventListener('input', showFinderConf);

    document.querySelectorAll('input[name="image-type"]')
        .forEach(r => r.addEventListener('change', reset));

    SHEET.canvas.addEventListener('mousedown', mouseDown);
    SHEET.canvas.addEventListener('mousemove', mouseMove);
    SHEET.canvas.addEventListener('mouseup', mouseUp);

    let width = document.querySelector('.sheet').clientWidth;
    SHEET.setCanvasSize(width);
    LABEL.setCanvasSize(width);
    DRAW.reset();

    setState();
})();
