import { CanvasPlus } from "./canvas_plus.js";
import { Draw } from "./draw.js";
import { ORANGE, GREEN, Label } from "./label.js";
import { LabelList  } from "./label_list.js";

const DRAW = new Draw();
const SHEET = new CanvasPlus(document.getElementById('sheet-canvas'));
const LABEL = new CanvasPlus(document.getElementById('label-canvas'));
const IMAGE = new Image();  // Upload images here before putting them into a canvas

let CANVAS_BEFORE_BOX = null;  // Save a sheet image before drawing a new box
let CANVAS_BEFORE_ANY_BOX = null;  // Save a sheet image before adding any boxes
let FULL_SIZE = null;  // An offscreen canvas that holds the original image
let LABEL_LIST = new LabelList();

const imageFileSelected = async () => {
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

    const imageFile = document.getElementById('image-file');
    DRAW.reset();
    if (!imageFile.value) {
        SHEET.clear();
        return;
    }

    const url = await readFileAsDataURL(imageFile.files[0]);
    await loadImage(url);

    FULL_SIZE = new CanvasPlus(new OffscreenCanvas(IMAGE.width, IMAGE.height));
    FULL_SIZE.ctx.drawImage(
        IMAGE, 0, 0, IMAGE.width, IMAGE.height, 0, 0, IMAGE.width, IMAGE.height
    );

    SHEET.clear();
    const [ctx_w, ctx_h, new_w, new_h] = SHEET.getScale(IMAGE.width, IMAGE.height);
    SHEET.ctx.drawImage(FULL_SIZE.canvas, 0, 0, IMAGE.width, IMAGE.height, 0, 0, new_w, new_h);

    CANVAS_BEFORE_ANY_BOX = SHEET.cloneCanvas();

    LABEL_LIST = new LabelList();
    setState();
}

const displayLabel = () => {
    if (!LABEL_LIST.hasLabels()) {
        LABEL.clear();
        return;
    }
    const labelIndex = document.getElementById('label-index');
    let idx = labelIndex.value;
    if (idx < 1) {
        idx = 1;
        labelIndex.value = `1`;
    }
    const label = LABEL_LIST.base1(idx);
    const labelInfo = document.getElementById('label-info');

    document.getElementById('text').value = LABEL_LIST.hasLabels() ? label.text : '';
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

const mouseDown = (event) => {
    if (!DRAW.canDraw || !SHEET.insideImage(event)) { return false; }
    const labelFixOp = document.getElementById('label-fix-op').value;
    if (labelFixOp == 'Draw') {
        DRAW.start = SHEET.canvasOffset(event);
        DRAW.end = DRAW.start;
        DRAW.drawing = true;
        CANVAS_BEFORE_BOX = SHEET.cloneCanvas();
    }
}

const mouseMove = (event) => {
    if (!DRAW.drawing || !SHEET.insideImage(event)) { return };
    DRAW.end = SHEET.canvasOffset(event);
    SHEET.ctx.drawImage(CANVAS_BEFORE_BOX, 0, 0);
    SHEET.ctx.strokeStyle = ORANGE;
    SHEET.ctx.lineWidth = 3;
    const [x, y, w, h] = DRAW.strokeRect();
    SHEET.ctx.strokeRect(x, y, w, h);
}

const mouseUp = (event) => {
    if (!DRAW.canDraw) { return false; }
    const labelFixOp = document.getElementById('label-fix-op').value;
    if (labelFixOp == 'Draw' && DRAW.drawing) {
        DRAW.scale(SHEET.scale);
        const tooSmall = DRAW.tooSmall();
        if (!tooSmall) {
            LABEL_LIST.push(new Label({
                type: 'Typewritten',
                left: DRAW.left,
                top: DRAW.top,
                right: DRAW.right,
                bottom: DRAW.bottom,
                conf: 1.0,
                text: '',
            }));
            setState();
            document.getElementById('label-index').value = LABEL_LIST.length;
            displayLabel();
        } else {
            SHEET.ctx.drawImage(CANVAS_BEFORE_BOX, 0, 0);
            alert(tooSmall);
        }
        DRAW.drawing = false;
    } else if (['Typewritten', 'Other'].includes(labelFixOp)) {
        LABEL_LIST.forEach((lb, i) => {
            if (lb.insideLabel(event, SHEET)) {
                lb.type = labelFixOp;
                LABEL_LIST.drawBoxes(SHEET);
                setState();
                document.getElementById('label-index').value = i + 1;
                displayLabel();
            }
        });
    } else if (labelFixOp == 'Remove') {
        SHEET.ctx.drawImage(CANVAS_BEFORE_ANY_BOX, 0, 0);
        LABEL_LIST = new LabelList(LABEL_LIST.filter(lb => !lb.insideLabel(event, SHEET)));
        LABEL_LIST.drawBoxes(SHEET);
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
                const text = JSON.parse(req.responseText);
                LABEL_LIST = new LabelList(JSON.parse(text));
                DRAW.canDraw = true;
                LABEL_LIST.drawBoxes(SHEET);
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
                const text = JSON.parse(req.responseText);
                LABEL_LIST = new LabelList(JSON.parse(text));
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
    data.append('labels', JSON.stringify(LABEL_LIST));
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
    const hasLabels = LABEL_LIST.hasLabels();

    if (!imageSelected) {
        LABEL_LIST = new LabelList();
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
    document.getElementById('save-text').disabled = !LABEL_LIST.some(lb => !!lb.text);

    const labelIndex = document.getElementById('label-index');

    labelIndex.disabled = !hasLabels;
    labelIndex.min = hasLabels ? '1' : '0';
    labelIndex.max = hasLabels ? `${LABEL_LIST.length}` : '0';

    const max = parseInt(labelIndex.max);
    const val = isNaN(parseInt(labelIndex.value)) ? 1 : parseInt(labelIndex.value);

    labelIndex.value = hasLabels ? `${Math.min(max, val)}` : '';

    const textarea = document.getElementById('text');

    textarea.disabled = !hasLabels;
    textarea.value = hasLabels ? LABEL_LIST[0].text : '';

    const labelInfo = document.getElementById('label-info');
    labelInfo.value = hasLabels ? showLabelInfo(LABEL_LIST[0]) : '';

    displayLabel();
    showFinderConf();
}

const showLabelInfo = (label) => {
    const labelInfo = document.getElementById('label-info');
    const type = document.querySelector('input[name="image-type"]:checked').value;
    labelInfo.value = type == 'sheet' ? label.info() : '';
}

const showFinderConf = () => {
    const conf = document.getElementById('finder-conf').value;
    document.getElementById('show-finder-conf').value = conf;
}

function removeExtension(fileName) {
    return fileName.substring(0, fileName.lastIndexOf('.')) || fileName;
}

const saveText = async () => {
    const imageFile = document.getElementById('image-file');
    const blob = new Blob([JSON.stringify(LABEL_LIST)], {type: 'text/json'});
    const a = document.createElement('a');
    a.download = `${removeExtension(imageFile.files[0].name)}.json`;
    a.href = URL.createObjectURL(blob);
    a.click();
    a.remove();
}

const saveLabels = () => {
    const imageFile = document.getElementById('image-file');
    const baseName = `${removeExtension(imageFile.files[0].name)}`;

    LABEL_LIST.forEach((lb, i) => {
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
        .addEventListener('change', async (event) => { imageFileSelected(); }, false);

    document.getElementById('find-labels')
        .addEventListener('click', findLabels);

    document.getElementById('ocr-labels')
        .addEventListener('click', ocrLabels);

    document.getElementById('label-index')
        .addEventListener('change', displayLabel);

    document.getElementById('prev-label-index')
        .addEventListener('click', () => {
            const labelIndex = document.getElementById('label-index');
            labelIndex.stepDown();
            displayLabel();
        });

    document.getElementById('next-label-index')
        .addEventListener('click', () => {
            const labelIndex = document.getElementById('label-index');
            labelIndex.stepUp();
            displayLabel();
        });

    document.getElementById('save-text')
        .addEventListener('click', saveText);

    document.getElementById('save-labels')
        .addEventListener('click', saveLabels);

    document.getElementById('text')
        .addEventListener('change', () => {
            const labelIndex = document.getElementById('label-index').value;
            const text = document.getElementById('text').value;
            LABEL_LIST.base1(labelIndex.value).text = text;
        });

    document.getElementById('finder-conf')
        .addEventListener('input', showFinderConf);

    document.querySelectorAll('input[name="image-type"]')
        .forEach(r => r.addEventListener('change', () => {
            LABEL_LIST = new LabelList();
            setState();
            SHEET.ctx.drawImage(CANVAS_BEFORE_ANY_BOX, 0, 0);
            DRAW.reset();
        }));

    SHEET.canvas.addEventListener('mousedown', mouseDown);
    SHEET.canvas.addEventListener('mousemove', mouseMove);

    document.querySelector('body')
        .addEventListener('mouseup', mouseUp);

    let width = document.querySelector('.sheet').clientWidth;
    SHEET.setCanvasSize(width);
    LABEL.setCanvasSize(width);
    DRAW.reset();

    setState();
})();
