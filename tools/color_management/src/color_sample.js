var BASE_COLOR = new HSLColor(0, 0, 100);

var ColorSample = function (line,uid) {


    // this is the overall node that will hold all sample information
    var node = document.createElement('div');
    node.className = 'sample';
    var sample_contents_template = document.getElementById('sample-template');
    var contents = document.importNode(sample_contents_template.content, true);
    node.appendChild(contents);

    // settings all the other necessary values
    this.uid = uid;
    this.node = node;
    this.line = line;

    this.sampleColor = node.querySelector('.sample-color');
    this.color = new Color(BASE_COLOR);

    this.key_input = node.querySelector('.sample-key');
    this.meta_input = node.querySelector('.sample-meta');

    node.setAttribute('sample-id', this.uid);
    this.sampleColor.setAttribute('draggable', 'true');

    this.sampleColor.addEventListener('dragstart', this.dragStart.bind(this));
    this.sampleColor.addEventListener('dragover' , allowDropEvent);
    this.sampleColor.addEventListener('drop'     , this.dragDrop.bind(this));
    node.querySelector('.copy-color').addEventListener(
        'click', this.copyColorIconClick.bind(this));
    node.querySelector('.copy-state').addEventListener(
        'click', this.copyStateIconClick.bind(this));
    node.querySelector('.delete-color').addEventListener(
        'click', this.deleteColorIconClick.bind(this));
    node.querySelector('.delete-state').addEventListener(
        'click', this.deleteStateIconClick.bind(this));
    node.querySelector('.paste-color').addEventListener(
        'click', this.pasteColorIconClick.bind(this));
    node.querySelector('.paste-state').addEventListener(
        'click', this.pasteStateIconClick.bind(this));

    this.updateBgColor();

};

ColorSample.prototype.updateBgColor = function updateBgColor() {
    this.sampleColor.style.backgroundColor = this.color.getColor();
};

ColorSample.prototype.getDigest = function() {
    var color_string = this.color.getSimpleHex();
    var key_value = '';
    if( this.key_input.value.length == 0 ) {
        key_value = this.uid;
    }
    else {
        key_value = this.key_input.value;
    }
    var digest = '' + key_value + DIGEST_UNIFIER
        + color_string + DIGEST_UNIFIER
        + this.meta_input.value;
    return digest;
};

ColorSample.prototype.updateColor = function updateColor(color) {
    this.color.copy(color);
    this.updateBgColor();
};

ColorSample.prototype.updateState = function(s) {
    this.updateColor(s[1]);
    this.key_input.value = s[0];
    this.meta_input.value = s[2];
};

ColorSample.prototype.activate = function activate() {
    UIColorPicker.setColor('picker', this.color);
    this.node.setAttribute('data-active', 'true');
    this.node.parentNode.setAttribute('data-active', 'true');
};

ColorSample.prototype.deactivate = function deactivate() {
    this.node.removeAttribute('data-active');
    this.node.parentNode.removeAttribute('data-active');
};

ColorSample.prototype.dragStart = function (e) {
    console.log("Started dragging:" + this.uid);
    e.dataTransfer.setData('sampleID', this.uid);
    e.dataTransfer.setData('sampleState', this.getDigest());
    e.dataTransfer.setData('color', this.color.getHexa());
    e.dataTransfer.setData('location', 'picker-samples');
};

ColorSample.prototype.copyColorIconClick = function (e) {
    navigator.clipboard.writeText(this.color.getSimpleHex());
};

ColorSample.prototype.copyStateIconClick = function (e) {
    navigator.clipboard.writeText(this.getDigest());
};

ColorSample.prototype.deleteColorIconClick = function (e) {
    this.deleteColor();
};

ColorSample.prototype.deleteColor = function() {
    this.color = new Color(BASE_COLOR);
    this.updateBgColor();
}

ColorSample.prototype.deleteState = function() {
    this.deleteColor();
    this.key_input.value = '';
    this.meta_input.value = '';
}

ColorSample.prototype.deleteStateIconClick = function (e) {
    this.deleteState();
};

ColorSample.prototype.pasteStateIconClick = function (e) {

    var state = prompt("Enter your state", "ffffff");
    if( state != null ) {
        if( state.includes('-') ) {
            this.line.pasteLineState(state);
        }
        else {
            this.updateState(parseState(state));
        }
    }
};

ColorSample.prototype.pasteColorIconClick = function (e) {

    var colors = prompt("Enter your color", "ffffff");
    if( colors != null ) {
        if( colors.includes('-') ) {
            this.line.pasteLineColors(colors);
        }
        else {
            this.updateColor(parseColor(colors));
        }
    }
};


ColorSample.prototype.dragDrop = function (e) {

    e.stopPropagation();

    var sampleID = e.dataTransfer.getData('sampleID');
    var sampleLocation = e.dataTransfer.getData('location');
    if( sampleLocation == 'picker-samples')
    {
        var old_digest = this.getDigest();
        var digest = e.dataTransfer.getData('sampleState');
        var s = parseState(digest);
        this.updateState(s);
        console.log("Dropping over:" + sampleID);
        console.log("Being dropped on:" + this.uid);
        this.line.updateSample(sampleID,old_digest);
    }
    else
    {
        var color = e.dataTransfer.getData('color');
        this.updateColor(parseColor(color));
    }


};
