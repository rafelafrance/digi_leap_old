'use strict';

export class CanvasPlus {
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
        return pos.x >= 0 && pos.x < this.image_width
            && pos.y >= 0 && pos.y < this.image_height;
    }
}
