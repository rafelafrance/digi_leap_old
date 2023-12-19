'use strict';

export class Draw {
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
    size() {
        return [Math.abs(this.end.x - this.start.x), Math.abs(this.end.y - this.start.y)];
    }
    scale(scaleBy) {
        this.left = Math.min(this.start.x, this.end.x) / scaleBy.x;
        this.top = Math.min(this.start.y, this.end.y) / scaleBy.y;
        this.right = Math.max(this.start.x, this.end.x) / scaleBy.x;
        this.bottom = Math.max(this.start.y, this.end.y) / scaleBy.y;
    }
    tooSmall() {
        const limit = 20;
        const [w, h] = this.size();
        const msg = `The new label is too small. width = ${w} < ${limit} or height = ${h} < ${limit}`;
        return w < limit || h < limit ? msg : false;
    }
    strokeRect() {
        const [w, h] = this.size();
        return [this.start.x, this.start.y, w, h];
    }
}
