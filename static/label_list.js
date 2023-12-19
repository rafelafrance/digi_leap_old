import { Label } from "./label.js";

export class LabelList extends Array {
    constructor(labels = []) {
        super();
        labels.forEach(lb => this.push(new Label(lb)));
    }
    hasLabels() {
        return this.length != 0;
    }
    noLabels() {
        return this.length == 0;
    }
    base1(index) {
        return this[index - 1];
    }
    drawBoxes(canvasPlus) {
        this.forEach(lb => lb.drawBox(canvasPlus));
    }
}
