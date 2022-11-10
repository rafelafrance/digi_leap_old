export const ORANGE = '#d95f02';
export const GREEN = '#1b9e77';

export class Label {
    constructor(label) {
        this.type = label.type;
        this.left = label.left;
        this.top = label.top;
        this.right = label.right;
        this.bottom = label.bottom;
        this.conf = label.conf;
        this.text = label.text;
    }
    info() {
        const conf = this.conf ? `conf ${this.conf}, ` : ''
        return `type: ${this.type}, ${conf} x: ${this.left}, y: ${this.top}`;
    }
    color() {
        return this.type == 'Typewritten' ? ORANGE : GREEN;
    }
    drawBox(canvasPlus) {
        canvasPlus.ctx.strokeStyle = this.color();
        canvasPlus.ctx.lineWidth = 3;
        canvasPlus.ctx.strokeRect(
            this.left * canvasPlus.scale.x,
            this.top * canvasPlus.scale.y,
            (this.right - this.left) * canvasPlus.scale.x,
            (this.bottom - this.top) * canvasPlus.scale.y,
        );
    }
    insideLabel(event, canvasPlus) {
        const pos = canvasPlus.canvasOffset(event);
        pos.x /= canvasPlus.scale.x;
        pos.y /= canvasPlus.scale.y;
        return this.left <= pos.x && this.right >= pos.x
            && this.top <= pos.y && this.bottom >= pos.y;
    }
}
