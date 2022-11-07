'use strict';

class Canvas {
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
}

const SHEET_IMAGE = new Image();

const SHEET = new Canvas(document.getElementById('sheet-canvas'));
const LABEL = new Canvas(document.getElementById('label-canvas'));

const DRAW = {
    active: false,
    start: {x: 0, y: 0},
    end: {x: 0, y: 0},
};

let BEFORE_DRAW = null;
let CLEAN_SHEET = null;
let FULL_SIZE = null;
let ALL_LABELS = [];

const getScale = (pic, img_w, img_h) => {
    const ctx_w = pic.ctx.canvas.width;
    const ctx_h = pic.ctx.canvas.height;
    let new_w = img_w;
    let new_h = img_h;

    pic.scale.x = 1.0;
    pic.scale.y = 1.0;

    if (img_w > ctx_w || img_h > ctx_h) {
        new_h = ctx_h;
        new_w = ctx_w;
        if (img_h > img_w) {
            new_w = new_h * img_w / img_h;
        } else {
            new_h = new_w * img_h / img_w;
        }
        pic.scale.x = new_w / img_w;
        pic.scale.y = new_h / img_h;
    }
    return [ctx_w, ctx_h, new_w, new_h];
}

const readFileAsDataURL = (file) => {
    return new Promise((resolve, reject) => {
        let reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(reader);
        reader.readAsDataURL(file);
    });
}

const loadImage = (url) => new Promise((resolve, reject) => {
    SHEET_IMAGE.addEventListener('load', () => resolve(SHEET_IMAGE));
    SHEET_IMAGE.addEventListener('error', (err) => reject(err));
    SHEET_IMAGE.src = url;
});

const displaySheet = async () => {
    const files = document.getElementById('files');
    if (!files.value) { return; }

    const url = await readFileAsDataURL(files.files[0]);
    await loadImage(url);

    const img_w = SHEET_IMAGE.width;
    const img_h = SHEET_IMAGE.height;
    FULL_SIZE = new Canvas(new OffscreenCanvas(img_w, img_h));
    FULL_SIZE.ctx.drawImage(SHEET_IMAGE, 0, 0, img_w, img_h, 0, 0, img_w, img_h);

    const [ctx_w, ctx_h, new_w, new_h] = getScale(LABEL, img_w, img_h);

    SHEET.ctx.clearRect(0, 0, ctx_w, ctx_h);
    SHEET.ctx.drawImage(FULL_SIZE.canvas, 0, 0, img_w, img_h, 0, 0, new_w, new_h);

    CLEAN_SHEET = SHEET.cloneCanvas();

    ALL_LABELS = [];
    setState();
}

const updateLabel = () => {
    const index = document.getElementById('index');
    const textarea = document.getElementById('text');
    const enabled = ALL_LABELS.length != 0;
    const label = ALL_LABELS[index.value - 1];
    const info = document.getElementById('info');

    textarea.value = enabled ? label.text : '';
    info.value = `type: ${label.type}, x: ${label.left}, y: ${label.top}`;

    const img_w = label.right - label.left;
    const img_h = label.bottom - label.top;
    const [ctx_w, ctx_h, new_w, new_h] = getScale(LABEL, img_w, img_h);

    LABEL.ctx.clearRect(0, 0, ctx_w, ctx_h);
    LABEL.ctx.drawImage(
        FULL_SIZE.canvas, label.left, label.top, img_w, img_h, 0, 0, new_w, new_h
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

const insideLabel = (evt, lb) => {
    const pos = canvasOffset(evt);
    pos.x /= SHEET.scale.x;
    pos.y /= SHEET.scale.y;
    return lb.left <= pos.x && lb.right >= pos.x
        && lb.top <= pos.y && lb.bottom >= pos.y;
}

const mouseUpListener = (evt) => {
    const fix = document.getElementById('fix').value;
    if (fix == 'Draw') {
        // Build new label
    } else if (['Typewritten', 'Other'].includes(fix)) {
        const pos = canvasOffset(evt);
        ALL_LABELS.forEach(lb => {
            if (insideLabel(evt, lb)) { lb.type = fix; }
        });
        drawBoxes();
    } else if (fix == 'Remove') {
        SHEET.ctx.drawImage(CLEAN_SHEET, 0, 0);
        ALL_LABELS = ALL_LABELS.filter(lb => !insideLabel(evt, lb));
        drawBoxes();
    }
    DRAW.active = false;
}

const findLabels = () => {
    let req = new XMLHttpRequest();
    const labelsFound = () => {
        if (req.readyState === XMLHttpRequest.DONE) {
            if (req.status === 200) {
                ALL_LABELS = JSON.parse(req.responseText);
                ALL_LABELS = JSON.parse(ALL_LABELS);  // WTF?!
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
                ALL_LABELS = labels;
                let text = '';
                labels.forEach(lb => {
                    text += lb.text;
                });
                document.getElementById('text').value = text;
                setState();
            } else {
                alert('OCR labels error');
            }
        }
    }
    const data = new FormData();
    data.append('labels', JSON.stringify(ALL_LABELS));
    data.append('sheet', files.files[0]);
    data.append(
        'filter',
        document.querySelector('input[name="which"]:checked').value,
    );

    req.open('POST', `${window.location.href}ocr-labels`, true);
    req.onreadystatechange = labelsOcred;
    req.setRequestHeader('Conteint-Type', 'multipart/form-data');
    req.overrideMimeType('multipart/form-data;');
    req.send(data);
}

const setState = () => {
    const image_selected = !!files.value;
    const type = document.querySelector('input[name="type"]:checked').value;
    const has_labels = ALL_LABELS.length != 0;
    const has_text = ALL_LABELS.some(lb => !!lb.text);

    const toggleImageType = ({image_selected, type, has_labels}) => {
        const sheet_ready = image_selected && type == 'sheet';
        const labels_ready = sheet_ready && has_labels;
        const can_ocr = image_selected && (type == 'label' || (type == 'sheet' && has_labels));
        document.getElementById('find-labels').disabled = !image_selected || type != 'sheet';
        document.getElementById('ocr-labels').disabled = !can_ocr;
        document.getElementById('conf').disabled = !sheet_ready;
        document.querySelectorAll('input[name="which"]').forEach(r => r.disabled = !sheet_ready);
        document.getElementById('fix').disabled = !labels_ready;
    }

    const toggleText = ({has_text}) => {
    }

    if (!image_selected) { ALL_LABELS = []; }

    toggleImageType({image_selected, type, has_labels});

    const index = document.getElementById('index');
    index.disabled = !has_text;
    index.min = has_text ? '1' : '0';
    index.max = has_text ? `${ALL_LABELS.length}` : '0';
    index.value = has_text ? '1' : '';

    const textarea = document.getElementById('text');
    textarea.disabled = !has_text;
    textarea.value = has_text ? ALL_LABELS[0].text : '';

    const info = document.getElementById('info');
    info.value = '';
    if (has_text) {
        info.value = `${ALL_LABELS[0].type} `
            + `(${ALL_LABELS[0].left}, ${ALL_LABELS[0].top})`;
    }
}

const showConf = () => {
    document.getElementById('show-conf').value = conf.value;
}

(() => {
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
        .addEventListener('change', updateLabel);

    document.getElementById('text')
        .addEventListener('change', () => {
        const index = document.getElementById('index');
        ALL_LABELS[index.value - 1].text = document.getElementById('text').value;
    });

    document.getElementById('conf')
        .addEventListener('change', showConf);

    document.querySelectorAll('input[name="type"]')
        .forEach(r => r.addEventListener('change', setState));

    SHEET.canvas.addEventListener('mousedown', mouseDownListener);
    SHEET.canvas.addEventListener('mousemove', mouseMoveListener);
    SHEET.canvas.addEventListener('mouseup', mouseUpListener);

    let width = document.querySelector('.sheet').clientWidth;
    SHEET.ctx.canvas.width = width;
    SHEET.ctx.canvas.height = width;
    LABEL.ctx.canvas.width = width;
    LABEL.ctx.canvas.height = width;
})();
