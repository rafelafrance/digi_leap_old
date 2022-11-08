'use strict';

class CanvasPlus {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.scale = { x: 1.0, y: 1.0 };
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
        return [ctx_w, ctx_h, new_w, new_h];
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
        this.active = false;
        this.can_draw = false;
        this.start = { x: 0, y: 0 };
        this.end = { x: 0, y: 0 };
        this.left = 0;
        this.top = 0;
        this.right = 0;
        this.bottom = 0;
    }

    scale(scale_by) {
        this.left = Math.min(this.start.x, this.end.x) / scale_by.x;
        this.top = Math.min(this.start.y, this.end.y) / scale_by.y;
        this.right = Math.max(this.start.x, this.end.x) / scale_by.x;
        this.bottom = Math.max(this.start.y, this.end.y) / scale_by.y;
    }

    too_small() {
        return (this.right - this.left) < 100 || (this.bottom - this.top) < 100;
    }

    strokeRect() {
        return [this.start.x, this.start.y, this.end.x - this.start.x, this.end.y - this.start.y];
    }
}

const DRAW = new Draw();

let BEFORE_DRAW = null;  // Save a sheet image before drawing a new box
let CLEAN_SHEET = null;  // Save a sheet image before adding any boxes
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
    const image_file = document.getElementById('image-file');
    DRAW.reset();
    if (!image_file.value) {
        SHEET.clear();
        return;
    }

    const url = await readFileAsDataURL(image_file.files[0]);
    await loadImage(url);

    const img_w = IMAGE.width;
    const img_h = IMAGE.height;
    FULL_SIZE = new CanvasPlus(new OffscreenCanvas(img_w, img_h));
    FULL_SIZE.ctx.drawImage(IMAGE, 0, 0, img_w, img_h, 0, 0, img_w, img_h);

    const [ctx_w, ctx_h, new_w, new_h] = SHEET.getScale(img_w, img_h);

    SHEET.clear();
    SHEET.ctx.drawImage(FULL_SIZE.canvas, 0, 0, img_w, img_h, 0, 0, new_w, new_h);

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

    const label_index = document.getElementById('label-index');
    let idx = label_index.value;
    if (idx < 1) {
        idx = 1;
        label_index.value = `1`;
    }
    const label = ALL_LABELS[idx - 1];
    const label_info = document.getElementById('label-info');

    document.getElementById('text').value = enabled ? label.text : '';
    showLabelInfo(label);

    const img_w = label.right - label.left;
    const img_h = label.bottom - label.top;
    const [ctx_w, ctx_h, new_w, new_h] = LABEL.getScale(img_w, img_h);

    LABEL.clear();
    const image_type = document.querySelector('input[name="image-type"]:checked').value;
    if (image_type == 'sheet') {
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

const canvasOffset = (evt) => {
    const { pageX, pageY } = evt.touches ? evt.touches[0] : evt;
    const x = pageX - SHEET.canvas.offsetLeft;
    const y = pageY - SHEET.canvas.offsetTop;
    return { x, y };
}

const insideLabel = (evt, lb) => {
    const pos = canvasOffset(evt);
    pos.x /= SHEET.scale.x;
    pos.y /= SHEET.scale.y;
    return lb.left <= pos.x && lb.right >= pos.x
        && lb.top <= pos.y && lb.bottom >= pos.y;
}

const mouseDown = (evt) => {
    if (!DRAW.can_draw) { return false; }
    const label_fix_op = document.getElementById('label-fix-op').value;
    if (label_fix_op == 'Draw') {
        DRAW.start = canvasOffset(evt);
        DRAW.active = true;
        BEFORE_DRAW = SHEET.cloneCanvas();
    }
}

const mouseMove = (evt) => {
    if (!DRAW.active) { return };

    DRAW.end = canvasOffset(evt);

    SHEET.ctx.drawImage(BEFORE_DRAW, 0, 0);

    SHEET.ctx.strokeStyle = '#d95f02';
    SHEET.ctx.lineWidth = 3;
    const [x, y, w, h] = DRAW.strokeRect();
    SHEET.ctx.strokeRect(x, y, w, h);
}

const mouseUp = (evt) => {
    if (!DRAW.can_draw) { return false; }
    const label_fix_op = document.getElementById('label-fix-op').value;
    if (label_fix_op == 'Draw') {
        DRAW.scale(SHEET.scale);
        if (!DRAW.too_small()) {
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
            SHEET.ctx.drawImage(BEFORE_DRAW, 0, 0);
            alert('The new label is too small.');
        }
    } else if (['Typewritten', 'Other'].includes(label_fix_op)) {
        ALL_LABELS.forEach((lb, i) => {
            if (insideLabel(evt, lb)) {
                lb.type = label_fix_op;
                drawBoxes();
                setState();
                document.getElementById('label-index').value = i + 1;
                displayLabel();
            }
        });
    } else if (label_fix_op == 'Remove') {
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
                DRAW.can_draw = true;
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

    if (!image_selected) {
        ALL_LABELS = [];
        DRAW.can_draw = false;
    }

    const sheet_ready = image_selected && type == 'sheet';
    const can_ocr = image_selected && (type == 'label' || (type == 'sheet' && has_labels));

    document.getElementById('find-labels').disabled = !image_selected || type != 'sheet';
    document.getElementById('ocr-labels').disabled = !can_ocr;
    document.getElementById('finder-conf').disabled = !sheet_ready;
    document.getElementById('label-fix-op').disabled = !sheet_ready || !DRAW.can_draw;
    document.getElementById('save-labels').disabled = !sheet_ready || !has_labels;
    document.getElementById('save-text').disabled = !ALL_LABELS.some(lb => !!lb.text);

    const label_index = document.getElementById('label-index');

    label_index.disabled = !has_labels;
    label_index.min = has_labels ? '1' : '0';
    label_index.max = has_labels ? `${ALL_LABELS.length}` : '0';

    const max = parseInt(label_index.max);
    const val = isNaN(parseInt(label_index.value)) ? 1 : parseInt(label_index.value);

    label_index.value = has_labels ? `${Math.min(max, val)}` : '';

    const textarea = document.getElementById('text');

    textarea.disabled = !has_labels;
    textarea.value = has_labels ? ALL_LABELS[0].text : '';

    const label_info = document.getElementById('label-info');

    label_info.value = has_labels ? showLabelInfo(ALL_LABELS[0]) : '';

    displayLabel();
    showFinderConf();
}

const showLabelInfo = (label) => {
    const label_info = document.getElementById('label-info');
    const type = document.querySelector('input[name="image-type"]:checked').value;
    if (type == 'sheet') {
        const conf = label.conf ? `conf ${label.conf}, ` : ''
        label_info.value = `type: ${label.type}, ${conf} x: ${label.left}, y: ${label.top}`;
    } else {
        label_info.value = '';
    }
}

const showFinderConf = () => {
    const conf = document.getElementById('finder-conf').value;
    document.getElementById('show-finder-conf').value = conf;
}

const nextLabelIndex = () => {
    const label_index = document.getElementById('label-index');
    label_index.stepUp();
    displayLabel();
}

const prevLabelIndex = () => {
    const label_index = document.getElementById('label-index');
    label_index.stepDown();
    displayLabel();
}

const reset = () => {
    ALL_LABELS = [];
    setState();
    SHEET.ctx.drawImage(CLEAN_SHEET, 0, 0);
    DRAW.reset();
}

function removeExtension(file_name) {
    return file_name.substring(0, file_name.lastIndexOf('.')) || file_name;
}

const saveText = async () => {
    const image_file = document.getElementById('image-file');
    const blob = new Blob([JSON.stringify(ALL_LABELS)], {type: 'text/json'});
    const a = document.createElement('a');
    a.download = `${removeExtension(image_file.files[0].name)}.json`;
    a.href = URL.createObjectURL(blob);
    a.click();
    a.remove();
}

const saveLabels = () => {
    const image_file = document.getElementById('image-file');
    const base_name = `${removeExtension(image_file.files[0].name)}`;

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
        a.download = `${base_name}_${i}_${lb.type}.png`;
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
            const label_index = document.getElementById('label-index').value;
            ALL_LABELS[label_index.value - 1].text = document.getElementById('text').value;
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
