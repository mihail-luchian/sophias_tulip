'use strict'

// this is the Whole color picker in the middle to the right
var ColorPicker = (function () {

    var subscribers = [];
    var pickers = [];


    /*========== Capture Mouse Movement ==========*/

    var setMouseTracking = function setMouseTracking(elem, callback) {
        elem.addEventListener('mousedown', function(e) {
            callback(e);
            document.getElementById("container-controls").setAttribute("expand-palette","false");
            document.addEventListener('mousemove', callback);
        });

        document.addEventListener('mouseup', function(e) {
            document.getElementById("container-controls").setAttribute("expand-palette","true");
            document.removeEventListener('mousemove', callback);
        });
    };

    /*====================*/
    // Color Picker Class
    /*====================*/

    function ColorPicker() {
        this.color = new Color();
        this.node = document.getElementById('color-picker');;
        this.subscribers = [];

        var type = this.node.getAttribute('data-mode');
        var topic = this.node.getAttribute('data-topic');

        this.topic = topic;
        this.picker_mode = (type === 'HSL') ? 'HSL' : 'HSV';
        this.color.setFormat(this.picker_mode);

        this.createPickingArea();
        this.createHueArea();

        this.newInputComponent('H', 'hue', this.inputChangeHue.bind(this),'number');
        this.newInputComponent('S', 'saturation', this.inputChangeSaturation.bind(this),'number');
        this.newInputComponent('V', 'value', this.inputChangeValue.bind(this),'number');
        this.newInputComponent('L', 'lightness', this.inputChangeLightness.bind(this),'number');

        this.newInputComponent('R', 'red', this.inputChangeRed.bind(this),'number');
        this.newInputComponent('G', 'green', this.inputChangeGreen.bind(this),'number');
        this.newInputComponent('B', 'blue', this.inputChangeBlue.bind(this),'number');

        this.createPreviewBox();

        this.newInputComponent('hexa', 'hexa', this.inputChangeHexa.bind(this),'text');

        this.setColor(this.color);
        pickers[topic] = this;
    }

    /*************************************************************************/
    //				Function for generating the color-picker
    /*************************************************************************/

    ColorPicker.prototype.createPickingArea = function createPickingArea() {
        var area = document.createElement('div');
        var picker = document.createElement('div');

        area.className = 'picking-area';
        picker.className = 'picker';

        this.picking_area = area;
        this.color_picker = picker;
        setMouseTracking(area, this.updateColor.bind(this));

        area.appendChild(picker);
        this.node.appendChild(area);
    };

    ColorPicker.prototype.createHueArea = function createHueArea() {
        var area = document.createElement('div');
        var picker = document.createElement('div');

        area.className = 'hue';
        picker.className ='slider-picker';

        this.hue_area = area;
        this.hue_picker = picker;
        setMouseTracking(area, this.updateHueSlider.bind(this));

        area.appendChild(picker);
        this.node.appendChild(area);
    };


    ColorPicker.prototype.createPreviewBox = function createPreviewBox(e) {
        var preview_box = document.createElement('div');
        var preview_color = document.createElement('div');

        preview_box.className = 'preview';
        preview_color.className = 'preview-color';

        this.preview_color = preview_color;

        preview_box.appendChild(preview_color);
        this.node.appendChild(preview_box);
    };

    ColorPicker.prototype.newInputComponent = function newInputComponent(title, topic, onChangeFunc,type) {
        var wrapper = document.createElement('div');
        var input = document.createElement('input');
        var info = document.createElement('span');

        wrapper.className = 'input';
        wrapper.setAttribute('data-topic', topic);
        info.textContent = title;
        info.className = 'name';
        input.setAttribute('type', type);

        wrapper.appendChild(info);
        wrapper.appendChild(input);
        this.node.appendChild(wrapper);

        input.addEventListener('change', onChangeFunc);
        input.addEventListener('click', function() {
            this.select();
        });

        this.subscribe(topic, function(value) {
            input.value = value;
        });
    };


    /*************************************************************************/
    //					Updates properties of UI elements
    /*************************************************************************/

    ColorPicker.prototype.updateColor = function updateColor(e) {

        // the fuck if I understand how this voodoo works
        var rect = this.picking_area.getBoundingClientRect();
        var docEl = document.documentElement;

        var x = e.pageX - (rect.left + window.pageXOffset - docEl.clientLeft);
        var y = e.pageY - (rect.top + window.pageYOffset - docEl.clientTop);
        var picker_offset = 5;

        // width and height should be the same
        var size = this.picking_area.clientWidth;

        if (x > size) x = size;
        if (y > size) y = size;
        if (x < 0) x = 0;
        if (y < 0) y = 0;

        var value = 100 - (y * 100 / size) | 0;
        var saturation = x * 100 / size | 0;

        if (this.picker_mode === 'HSV')
            this.color.setHSV(this.color.hue, saturation, value);
        if (this.picker_mode === 'HSL')
            this.color.setHSL(this.color.hue, saturation, value);

        this.color_picker.style.left = x - picker_offset + 'px';
        this.color_picker.style.top = y - picker_offset + 'px';

        this.updatePreviewColor();

        this.notify('value', value);
        this.notify('lightness', value);
        this.notify('saturation', saturation);

        this.notify('red', this.color.r);
        this.notify('green', this.color.g);
        this.notify('blue', this.color.b);
        this.notify('hexa', this.color.getHexa());

        notify(this.topic, this.color);
    };

    ColorPicker.prototype.updateHueSlider = function updateHueSlider(e) {
        var x = e.pageX - this.hue_area.offsetLeft;
        var width = this.hue_area.clientWidth;

        if (x < 0) x = 0;
        if (x > width) x = width;

        // TODO 360 => 359
        var hue = ((359 * x) / width) | 0;
        // if (hue === 360) hue = 359;

        this.updateSliderPosition(this.hue_picker, x);
        this.setHue(hue);
    };


    ColorPicker.prototype.setHue = function setHue(value) {
        this.color.setHue(value);

        this.updatePickerBackground();
        this.updatePreviewColor();

        this.notify('red', this.color.r);
        this.notify('green', this.color.g);
        this.notify('blue', this.color.b);
        this.notify('hexa', this.color.getHexa());
        this.notify('hue', this.color.hue);

        notify(this.topic, this.color);
    };

    // Updates when one of Saturation/Value/Lightness changes
    ColorPicker.prototype.updateSLV = function updateSLV() {
        this.updatePickerPosition();
        this.updatePreviewColor();

        this.notify('red', this.color.r);
        this.notify('green', this.color.g);
        this.notify('blue', this.color.b);
        this.notify('hexa', this.color.getHexa());

        notify(this.topic, this.color);
    };

    /*************************************************************************/
    //				Update positions of various UI elements
    /*************************************************************************/

    ColorPicker.prototype.updatePickerPosition = function updatePickerPosition() {
        var size = this.picking_area.clientWidth;
        var value = 0;
        var offset = 5;

        if (this.picker_mode === 'HSV')
            value = this.color.value;
        if (this.picker_mode === 'HSL')
            value = this.color.lightness;

        var x = (this.color.saturation * size / 100) | 0;
        var y = size - (value * size / 100) | 0;

        this.color_picker.style.left = x - offset + 'px';
        this.color_picker.style.top = y - offset + 'px';
    };

    ColorPicker.prototype.updateSliderPosition = function updateSliderPosition(elem, pos) {
        elem.style.left = Math.max(pos - 3, -2) + 'px';
    };

    ColorPicker.prototype.updateHuePicker = function updateHuePicker() {
        var size = this.hue_area.clientWidth;
        var offset = 1;
        var pos = (this.color.hue * size / 360 ) | 0;
        this.hue_picker.style.left = pos - offset + 'px';
    };


    /*************************************************************************/
    //						Update background colors
    /*************************************************************************/

    ColorPicker.prototype.updatePickerBackground = function updatePickerBackground() {
        var nc = new Color(this.color);
        nc.setHSV(nc.hue, 100, 100);
        this.picking_area.style.backgroundColor = nc.getHexa();
    };


    ColorPicker.prototype.updatePreviewColor = function updatePreviewColor() {
        this.preview_color.style.backgroundColor = this.color.getColor();
    };

    /*************************************************************************/
    //						Update input elements
    /*************************************************************************/

    ColorPicker.prototype.inputChangeHue = function inputChangeHue(e) {
        var value = parseInt(e.target.value);
        this.setHue(value);
        this.updateHuePicker();
    };

    ColorPicker.prototype.inputChangeSaturation = function inputChangeSaturation(e) {
        var value = parseInt(e.target.value);
        this.color.setSaturation(value);
        e.target.value = this.color.saturation;
        this.updateSLV();
    };

    ColorPicker.prototype.inputChangeValue = function inputChangeValue(e) {
        var value = parseInt(e.target.value);
        this.color.setValue(value);
        e.target.value = this.color.value;
        this.updateSLV();
    };

    ColorPicker.prototype.inputChangeLightness = function inputChangeLightness(e) {
        var value = parseInt(e.target.value);
        this.color.setLightness(value);
        e.target.value = this.color.lightness;
        this.updateSLV();
    };

    ColorPicker.prototype.inputChangeRed = function inputChangeRed(e) {
        var value = parseInt(e.target.value);
        this.color.setByName('r', value);
        e.target.value = this.color.r;
        this.setColor(this.color);
    };

    ColorPicker.prototype.inputChangeGreen = function inputChangeGreen(e) {
        var value = parseInt(e.target.value);
        this.color.setByName('g', value);
        e.target.value = this.color.g;
        this.setColor(this.color);
    };

    ColorPicker.prototype.inputChangeBlue = function inputChangeBlue(e) {
        var value = parseInt(e.target.value);
        this.color.setByName('b', value);
        e.target.value = this.color.b;
        this.setColor(this.color);
    };

    ColorPicker.prototype.inputChangeHexa = function inputChangeHexa(e) {
        var value = e.target.value;
        this.color.setHexa(value);
        this.setColor(this.color);
    };

    /*************************************************************************/
    //							Internal Pub/Sub
    /*************************************************************************/

    ColorPicker.prototype.subscribe = function subscribe(topic, callback) {
        this.subscribers[topic] = callback;
    };

    ColorPicker.prototype.notify = function notify(topic, value) {
        if (this.subscribers[topic])
            this.subscribers[topic](value);
    };

    /*************************************************************************/
    //							Set Picker Properties
    /*************************************************************************/

    ColorPicker.prototype.setColor = function setColor(color) {
        if(color instanceof Color !== true) {
            console.log('Typeof parameter not Color');
            return;
        }

        if (color.format !== this.picker_mode) {
            color.setFormat(this.picker_mode);
            color.updateHSX();
        }

        this.color.copy(color);
        this.updateHuePicker();
        this.updatePickerPosition();
        this.updatePickerBackground();
        this.updatePreviewColor();

        this.notify('red', this.color.r);
        this.notify('green', this.color.g);
        this.notify('blue', this.color.b);

        this.notify('hue', this.color.hue);
        this.notify('saturation', this.color.saturation);
        this.notify('value', this.color.value);
        this.notify('lightness', this.color.lightness);

        this.notify('hexa', this.color.getHexa());
        notify(this.topic, this.color);
    };

    ColorPicker.prototype.setPickerMode = function setPickerMode(mode) {
        if (mode !== 'HSV' && mode !== 'HSL')
            return;

        this.picker_mode = mode;
        this.node.setAttribute('data-mode', this.picker_mode);
        this.setColor(this.color);
    };

    // wrapper for the ColorPicker.prototype.setPickerMode function
    var setPickerMode = function setPickerMode(topic, mode) {
        if (pickers[topic]) {
            pickers[topic].setPickerMode(mode);
        }
    };

    var setColor = function setColor(topic, color) {
        if (pickers[topic])
            pickers[topic].setColor(color);
    };

    var getColor = function getColor(topic) {
        if (pickers[topic])
            return new Color(pickers[topic].color);
    };

    var subscribe = function subscribe(topic, callback) {
        if (subscribers[topic] === undefined)
            subscribers[topic] = [];

        subscribers[topic].push(callback);
    };

    var unsubscribe = function unsubscribe(callback) {
        subscribers.indexOf(callback);
        subscribers.splice(index, 1);
    };

    var notify = function notify(topic, value) {
        if (subscribers[topic] === undefined || subscribers[topic].length === 0)
            return;

        var color = new Color(value);
        for (var i in subscribers[topic])
            subscribers[topic][i](color);
    };

    var init = function init() {
        new ColorPicker();
    };

    return {
        init : init,
        setColor : setColor,
        getColor : getColor,
        subscribe : subscribe,
        unsubscribe : unsubscribe,
        setPickerMode : setPickerMode
    };

})();