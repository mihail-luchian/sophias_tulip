'use strict';

var SAMPLES_PER_LINE = 5;
var NUM_STARTING_LINES = 4;
var DIGEST_UNIFIER = '/';

// this is the Whole color picker in the middle to the right
var UIColorPicker = (function UIColorPicker() {

	function getElemById(id) {
		return document.getElementById(id);
	}

	var subscribers = [];
	var pickers = [];

	/**
	 * RGBA Color class
	 *
	 * HSV/HSB and HSL (hue, saturation, value / brightness, lightness)
	 * @param hue			0-360
	 * @param saturation	0-100
	 * @param value 		0-100
	 * @param lightness		0-100
	 */

    // Color constructor
	function Color(color) {

		if(color instanceof Color === true) {
			this.copy(color);
			return;
		}

		this.r = 0;
		this.g = 0;
		this.b = 0;
		this.a = 1;
		this.hue = 0;
		this.saturation = 0;
		this.value = 0;
		this.lightness = 0;
		this.format = 'HSV';
	}

    // Different types of color constructors
	function RGBColor(r, g, b) {
		var color = new Color();
		color.setRGBA(r, g, b, 1);
		return color;
	}

	function RGBAColor(r, g, b, a) {
		var color = new Color();
		color.setRGBA(r, g, b, a);
		return color;
	}

	function HSVColor(h, s, v) {
		var color = new Color();
		color.setHSV(h, s, v);
		return color;
	}

	function HSVAColor(h, s, v, a) {
		var color = new Color();
		color.setHSV(h, s, v);
		color.a = a;
		return color;
	}

	function HSLColor(h, s, l) {
		var color = new Color();
		color.setHSL(h, s, l);
		return color;
	}

	function HSLAColor(h, s, l, a) {
		var color = new Color();
		color.setHSL(h, s, l);
		color.a = a;
		return color;
	}

    // Copy functionality
	Color.prototype.copy = function copy(obj) {
		if(obj instanceof Color !== true) {
			console.log('Typeof parameter not Color');
			return;
		}

		this.r = obj.r;
		this.g = obj.g;
		this.b = obj.b;
		this.a = obj.a;
		this.hue = obj.hue;
		this.saturation = obj.saturation;
		this.value = obj.value;
		this.format = '' + obj.format;
		this.lightness = obj.lightness;
	};

	Color.prototype.setFormat = function setFormat(format) {
		if (format === 'HSV')
			this.format = 'HSV';
		if (format === 'HSL')
			this.format = 'HSL';
	};

	/*========== Methods to set Color Properties ==========*/

	Color.prototype.isValidRGBValue = function isValidRGBValue(value) {
		return (typeof(value) === 'number' && isNaN(value) === false &&
			value >= 0 && value <= 255);
	};

	Color.prototype.setRGBA = function setRGBA(red, green, blue, alpha) {
		if (this.isValidRGBValue(red) === false ||
			this.isValidRGBValue(green) === false ||
			this.isValidRGBValue(blue) === false)
			return;

			this.r = red | 0;
			this.g = green | 0;
			this.b = blue | 0;

		if (this.isValidRGBValue(alpha) === true)
			this.a = alpha | 0;
	};

	Color.prototype.setByName = function setByName(name, value) {
		if (name === 'r' || name === 'g' || name === 'b') {
			if(this.isValidRGBValue(value) === false)
				return;

			this[name] = value;
			this.updateHSX();
		}
	};

	Color.prototype.setHSV = function setHSV(hue, saturation, value) {
		this.hue = hue;
		this.saturation = saturation;
		this.value = value;
		this.HSVtoRGB();
	};

	Color.prototype.setHSL = function setHSL(hue, saturation, lightness) {
		this.hue = hue;
		this.saturation = saturation;
		this.lightness = lightness;
		this.HSLtoRGB();
	};

	Color.prototype.setHue = function setHue(value) {
		if (typeof(value) !== 'number' || isNaN(value) === true ||
			value < 0 || value > 359)
			return;
		this.hue = value;
		this.updateRGB();
	};

	Color.prototype.setSaturation = function setSaturation(value) {
		if (typeof(value) !== 'number' || isNaN(value) === true ||
			value < 0 || value > 100)
			return;
		this.saturation = value;
		this.updateRGB();
	};

	Color.prototype.setValue = function setValue(value) {
		if (typeof(value) !== 'number' || isNaN(value) === true ||
			value < 0 || value > 100)
			return;
		this.value = value;
		this.HSVtoRGB();
	};

	Color.prototype.setLightness = function setLightness(value) {
		if (typeof(value) !== 'number' || isNaN(value) === true ||
			value < 0 || value > 100)
			return;
		this.lightness = value;
		this.HSLtoRGB();
	};

	Color.prototype.setHexa = function setHexa(value) {
		var valid  = /(^#{0,1}[0-9A-F]{6}$)|(^#{0,1}[0-9A-F]{3}$)/i.test(value);

		if (valid !== true)
			return;

		if (value[0] === '#')
			value = value.slice(1, value.length);

		if (value.length === 3)
			value = value.replace(/([0-9A-F])([0-9A-F])([0-9A-F])/i,'$1$1$2$2$3$3');

		this.r = parseInt(value.substr(0, 2), 16);
		this.g = parseInt(value.substr(2, 2), 16);
		this.b = parseInt(value.substr(4, 2), 16);

		this.alpha	= 1;
		this.RGBtoHSV();
	};

	/*========== Conversion Methods ==========*/

	Color.prototype.convertToHSL = function convertToHSL() {
		if (this.format === 'HSL')
			return;

		this.setFormat('HSL');
		this.RGBtoHSL();
	};

	Color.prototype.convertToHSV = function convertToHSV() {
		if (this.format === 'HSV')
			return;

		this.setFormat('HSV');
		this.RGBtoHSV();
	};

	/*========== Update Methods ==========*/

	Color.prototype.updateRGB = function updateRGB() {
		if (this.format === 'HSV') {
			this.HSVtoRGB();
			return;
		}

		if (this.format === 'HSL') {
			this.HSLtoRGB();
			return;
		}
	};

	Color.prototype.updateHSX = function updateHSX() {
		if (this.format === 'HSV') {
			this.RGBtoHSV();
			return;
		}

		if (this.format === 'HSL') {
			this.RGBtoHSL();
			return;
		}
	};

	Color.prototype.HSVtoRGB = function HSVtoRGB() {
		var sat = this.saturation / 100;
		var value = this.value / 100;
		var C = sat * value;
		var H = this.hue / 60;
		var X = C * (1 - Math.abs(H % 2 - 1));
		var m = value - C;
		var precision = 255;

		C = (C + m) * precision | 0;
		X = (X + m) * precision | 0;
		m = m * precision | 0;

		if (H >= 0 && H < 1) {	this.setRGBA(C, X, m);	return; }
		if (H >= 1 && H < 2) {	this.setRGBA(X, C, m);	return; }
		if (H >= 2 && H < 3) {	this.setRGBA(m, C, X);	return; }
		if (H >= 3 && H < 4) {	this.setRGBA(m, X, C);	return; }
		if (H >= 4 && H < 5) {	this.setRGBA(X, m, C);	return; }
		if (H >= 5 && H < 6) {	this.setRGBA(C, m, X);	return; }
	};

	Color.prototype.HSLtoRGB = function HSLtoRGB() {
		var sat = this.saturation / 100;
		var light = this.lightness / 100;
		var C = sat * (1 - Math.abs(2 * light - 1));
		var H = this.hue / 60;
		var X = C * (1 - Math.abs(H % 2 - 1));
		var m = light - C/2;
		var precision = 255;

		C = (C + m) * precision | 0;
		X = (X + m) * precision | 0;
		m = m * precision | 0;

		if (H >= 0 && H < 1) {	this.setRGBA(C, X, m);	return; }
		if (H >= 1 && H < 2) {	this.setRGBA(X, C, m);	return; }
		if (H >= 2 && H < 3) {	this.setRGBA(m, C, X);	return; }
		if (H >= 3 && H < 4) {	this.setRGBA(m, X, C);	return; }
		if (H >= 4 && H < 5) {	this.setRGBA(X, m, C);	return; }
		if (H >= 5 && H < 6) {	this.setRGBA(C, m, X);	return; }
	};

	Color.prototype.RGBtoHSV = function RGBtoHSV() {
		var red		= this.r / 255;
		var green	= this.g / 255;
		var blue	= this.b / 255;

		var cmax = Math.max(red, green, blue);
		var cmin = Math.min(red, green, blue);
		var delta = cmax - cmin;
		var hue = 0;
		var saturation = 0;

		if (delta) {
			if (cmax === red ) { hue = ((green - blue) / delta); }
			if (cmax === green ) { hue = 2 + (blue - red) / delta; }
			if (cmax === blue ) { hue = 4 + (red - green) / delta; }
			if (cmax) saturation = delta / cmax;
		}

		this.hue = 60 * hue | 0;
		if (this.hue < 0) this.hue += 360;
		this.saturation = (saturation * 100) | 0;
		this.value = (cmax * 100) | 0;
	};

	Color.prototype.RGBtoHSL = function RGBtoHSL() {
		var red		= this.r / 255;
		var green	= this.g / 255;
		var blue	= this.b / 255;

		var cmax = Math.max(red, green, blue);
		var cmin = Math.min(red, green, blue);
		var delta = cmax - cmin;
		var hue = 0;
		var saturation = 0;
		var lightness = (cmax + cmin) / 2;
		var X = (1 - Math.abs(2 * lightness - 1));

		if (delta) {
			if (cmax === red ) { hue = ((green - blue) / delta); }
			if (cmax === green ) { hue = 2 + (blue - red) / delta; }
			if (cmax === blue ) { hue = 4 + (red - green) / delta; }
			if (cmax) saturation = delta / X;
		}

		this.hue = 60 * hue | 0;
		if (this.hue < 0) this.hue += 360;
		this.saturation = (saturation * 100) | 0;
		this.lightness = (lightness * 100) | 0;
	};

	/*========== Get Methods ==========*/

	Color.prototype.getHexa = function() {
		var r = this.r.toString(16);
		var g = this.g.toString(16);
		var b = this.b.toString(16);
		if (this.r < 16) r = '0' + r;
		if (this.g < 16) g = '0' + g;
		if (this.b < 16) b = '0' + b;
		var value = '#' + r + g + b;
		return value.toUpperCase();
	};

	Color.prototype.getSimpleHex = function() {
		var r = this.r.toString(16);
		var g = this.g.toString(16);
		var b = this.b.toString(16);
		if (this.r < 16) r = '0' + r;
		if (this.g < 16) g = '0' + g;
		if (this.b < 16) b = '0' + b;
		var value = '' + r + g + b;
		return value;
	};

	Color.prototype.getRGBA = function() {

		var rgb = '(' + this.r + ', ' + this.g + ', ' + this.b;
		var a = '';
		var v = '';
		var x = parseFloat(this.a);
		if (x !== 1) {
			a = 'a';
			v = ', ' + x;
		}

		var value = 'rgb' + a + rgb + v + ')';
		return value;
	};

	Color.prototype.getHSLA = function() {
		if (this.format === 'HSV') {
			var color = new Color(this);
			color.setFormat('HSL');
			color.updateHSX();
			return color.getHSLA();
		}

		var a = '';
		var v = '';
		var hsl = '(' + this.hue + ', ' + this.saturation + '%, ' + this.lightness +'%';
		var x = parseFloat(this.a);
		if (x !== 1) {
			a = 'a';
			v = ', ' + x;
		}

		var value = 'hsl' + a + hsl + v + ')';
		return value;
	};

	Color.prototype.getColor = function() {
		if (this.a | 0 === 1)
			return this.getHexa();
		return this.getRGBA();
	};

	/*=======================================================================*/
	/*=======================================================================*/

	/*========== Capture Mouse Movement ==========*/

	var setMouseTracking = function setMouseTracking(elem, callback) {
		elem.addEventListener('mousedown', function(e) {
			callback(e);
			document.addEventListener('mousemove', callback);
		});

		document.addEventListener('mouseup', function(e) {
			document.removeEventListener('mousemove', callback);
		});
	};

	/*====================*/
	// Color Picker Class
	/*====================*/

	function ColorPicker(node) {
		this.color = new Color();
		this.node = node;
		this.subscribers = [];

		var type = this.node.getAttribute('data-mode');
		var topic = this.node.getAttribute('data-topic');

		this.topic = topic;
		this.picker_mode = (type === 'HSL') ? 'HSL' : 'HSV';
		this.color.setFormat(this.picker_mode);

		this.createPickingArea();
		this.createHueArea();

		this.newInputComponent('H', 'hue', this.inputChangeHue.bind(this));
		this.newInputComponent('S', 'saturation', this.inputChangeSaturation.bind(this));
		this.newInputComponent('V', 'value', this.inputChangeValue.bind(this));
		this.newInputComponent('L', 'lightness', this.inputChangeLightness.bind(this));

		this.createAlphaArea();

		this.newInputComponent('R', 'red', this.inputChangeRed.bind(this));
		this.newInputComponent('G', 'green', this.inputChangeGreen.bind(this));
		this.newInputComponent('B', 'blue', this.inputChangeBlue.bind(this));

		this.createPreviewBox();

		this.newInputComponent('alpha', 'alpha', this.inputChangeAlpha.bind(this));
		this.newInputComponent('hexa', 'hexa', this.inputChangeHexa.bind(this));

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

	ColorPicker.prototype.createAlphaArea = function createAlphaArea() {
		var area = document.createElement('div');
		var mask = document.createElement('div');
		var picker = document.createElement('div');

		area.className = 'alpha';
		mask.className = 'alpha-mask';
		picker.className = 'slider-picker';

		this.alpha_area = area;
		this.alpha_mask = mask;
		this.alpha_picker = picker;
		setMouseTracking(area, this.updateAlphaSlider.bind(this));

		area.appendChild(mask);
		mask.appendChild(picker);
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

	ColorPicker.prototype.newInputComponent = function newInputComponent(title, topic, onChangeFunc) {
		var wrapper = document.createElement('div');
		var input = document.createElement('input');
		var info = document.createElement('span');

		wrapper.className = 'input';
		wrapper.setAttribute('data-topic', topic);
		info.textContent = title;
		info.className = 'name';
		input.setAttribute('type', 'text');

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
		var x = e.pageX - this.picking_area.offsetLeft;
		var y = e.pageY - this.picking_area.offsetTop;
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

		this.updateAlphaGradient();
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

	ColorPicker.prototype.updateAlphaSlider = function updateAlphaSlider(e) {
		var x = e.pageX - this.alpha_area.offsetLeft;
		var width = this.alpha_area.clientWidth;

		if (x < 0) x = 0;
		if (x > width) x = width;

		this.color.a = (x / width).toFixed(2);

		this.updateSliderPosition(this.alpha_picker, x);
		this.updatePreviewColor();

		this.notify('alpha', this.color.a);
		notify(this.topic, this.color);
	};

	ColorPicker.prototype.setHue = function setHue(value) {
		this.color.setHue(value);

		this.updatePickerBackground();
		this.updateAlphaGradient();
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
		this.updateAlphaGradient();
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

	ColorPicker.prototype.updateAlphaPicker = function updateAlphaPicker() {
		var size = this.alpha_area.clientWidth;
		var offset = 1;
		var pos = (this.color.a * size) | 0;
		this.alpha_picker.style.left = pos - offset + 'px';
	};

	/*************************************************************************/
	//						Update background colors
	/*************************************************************************/

	ColorPicker.prototype.updatePickerBackground = function updatePickerBackground() {
		var nc = new Color(this.color);
		nc.setHSV(nc.hue, 100, 100);
		this.picking_area.style.backgroundColor = nc.getHexa();
	};

	ColorPicker.prototype.updateAlphaGradient = function updateAlphaGradient() {
		this.alpha_mask.style.backgroundColor = this.color.getHexa();
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

	ColorPicker.prototype.inputChangeAlpha = function inputChangeAlpha(e) {
		var value = parseFloat(e.target.value);

		if (typeof value === 'number' && isNaN(value) === false &&
			value >= 0 && value <= 1)
			this.color.a = value.toFixed(2);

		e.target.value = this.color.a;
		this.updateAlphaPicker();
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
		this.updateAlphaPicker();
		this.updateAlphaGradient();
		this.updatePreviewColor();

		this.notify('red', this.color.r);
		this.notify('green', this.color.g);
		this.notify('blue', this.color.b);

		this.notify('hue', this.color.hue);
		this.notify('saturation', this.color.saturation);
		this.notify('value', this.color.value);
		this.notify('lightness', this.color.lightness);

		this.notify('alpha', this.color.a);
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

	/*************************************************************************/
	//								UNUSED
	/*************************************************************************/

	var setPickerMode = function setPickerMode(topic, mode) {
		if (pickers[topic])
			pickers[topic].setPickerMode(mode);
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
        var elem = document.getElementById('ui-color-picker');
        console.log(elem)
        new ColorPicker(elem);
	};

	return {
		init : init,
		Color : Color,
		RGBColor : RGBColor,
		RGBAColor : RGBAColor,
		HSVColor : HSVColor,
		HSVAColor : HSVAColor,
		HSLColor : HSLColor,
		HSLAColor : HSLAColor,
		setColor : setColor,
		getColor : getColor,
		subscribe : subscribe,
		unsubscribe : unsubscribe,
		setPickerMode : setPickerMode
	};

})();



'use strict';

window.addEventListener("load", function() {
	ColorPickerTool.init();
});

// this is the middle part of the UI
// the color sampling and management
var ColorPickerTool = (function ColorPickerTool() {

	/*========== Get DOM Element By ID ==========*/

	function getElemById(id) {
		return document.getElementById(id);
	}

	function allowDropEvent(e) {
		e.preventDefault();
	}

	/*========== Make an element resizable relative to it's parent ==========*/

	var UIComponent = (function UIComponent() {

		function makeResizable(elem, axis) {
			var valueX = 0;
			var valueY = 0;
			var action = 0;

			var resizeStart = function resizeStart(e) {
				e.stopPropagation();
				e.preventDefault();
				if (e.button !== 0)
					return;

				valueX = e.clientX - elem.clientWidth;
				valueY = e.clientY - elem.clientHeight;

				document.body.setAttribute('data-resize', axis);
				document.addEventListener('mousemove', mouseMove);
				document.addEventListener('mouseup', resizeEnd);
			};

			var mouseMove = function mouseMove(e) {
				if (action >= 0)
					elem.style.width = e.clientX - valueX + 'px';
				if (action <= 0)
					elem.style.height = e.clientY - valueY + 'px';
			};

			var resizeEnd = function resizeEnd(e) {
				if (e.button !== 0)
					return;

				document.body.removeAttribute('data-resize', axis);
				document.removeEventListener('mousemove', mouseMove);
				document.removeEventListener('mouseup', resizeEnd);
			};

			var handle = document.createElement('div');
			handle.className = 'resize-handle';

			if (axis === 'width') action = 1;
			else if (axis === 'height') action = -1;
			else axis = 'both';

			handle.className = 'resize-handle';
			handle.setAttribute('data-resize', axis);
			handle.addEventListener('mousedown', resizeStart);
			elem.appendChild(handle);
		};

		/*========== Make an element draggable relative to it's parent ==========*/

		var makeDraggable = function makeDraggable(elem, endFunction) {

			var offsetTop;
			var offsetLeft;

			elem.setAttribute('data-draggable', 'true');

			var dragStart = function dragStart(e) {
				e.preventDefault();
				e.stopPropagation();

				if (e.target.getAttribute('data-draggable') !== 'true' ||
					e.target !== elem || e.button !== 0)
					return;

				offsetLeft = e.clientX - elem.offsetLeft;
				offsetTop = e.clientY - elem.offsetTop;

				document.addEventListener('mousemove', mouseDrag);
				document.addEventListener('mouseup', dragEnd);
			};

			var dragEnd = function dragEnd(e) {
				if (e.button !== 0)
					return;

				document.removeEventListener('mousemove', mouseDrag);
				document.removeEventListener('mouseup', dragEnd);
			};

			var mouseDrag = function mouseDrag(e) {
				elem.style.left = e.clientX - offsetLeft + 'px';
				elem.style.top = e.clientY - offsetTop + 'px';
			};

			elem.addEventListener('mousedown', dragStart, false);
		};

		return {
			makeResizable : makeResizable,
			makeDraggable : makeDraggable
		};

	})();

	/*========== Color Class ==========*/

	var Color = UIColorPicker.Color;
	var HSLColor = UIColorPicker.HSLColor;

	/**
	 * ColorPalette
	 */
	// There are the things on top
	// the color pallettes on top, generated from the color in the ColorPicker area
	var ColorPalette = (function ColorPalette() {

		var samples = [];
		var color_palette;
		var complementary;

		var hideNode = function(node) {
			node.setAttribute('data-hidden', 'true');
		};

		var ColorSample = function ColorSample(id) {
			var node = document.createElement('div');
			node.className = 'sample-color';

            // additional color sample information
			this.uid = samples.length;
			this.node = node;
			this.color = new Color();
			this.was_active = false;

			node.setAttribute('sample-id', this.uid);
			node.setAttribute('draggable', 'true');
			node.addEventListener('dragstart', this.dragStart.bind(this));
			node.addEventListener('click', this.pickColor.bind(this));

			samples.push(this);
		};


		ColorSample.prototype.updateBgColor = function() {
			this.node.style.backgroundColor = this.color.getColor();
		};

		ColorSample.prototype.updateColor = function(color) {
			this.color.copy(color);
			this.updateBgColor();
		};


		ColorSample.prototype.updateHue = function updateHue(color, degree, steps) {
			this.color.copy(color);
			var hue = (steps * degree + this.color.hue) % 360;
			if (hue < 0) hue += 360;
			this.color.setHue(hue);
			this.updateBgColor();
		};

		ColorSample.prototype.updateSaturation = function updateSaturation(color, value, steps) {
			var saturation = color.saturation + value * steps;
			if (saturation <= 0) {
				this.node.setAttribute('data-hidden', 'true');
				return;
			}

			this.node.removeAttribute('data-hidden');
			this.color.copy(color);
			this.color.setSaturation(saturation);
			this.updateBgColor();
		};

		ColorSample.prototype.updateLightness = function updateLightness(color, value, steps) {
			var lightness = color.lightness + value * steps;
			if (lightness <= 0) {
				this.node.setAttribute('data-hidden', 'true');
				return;
			}
			this.node.removeAttribute('data-hidden');
			this.color.copy(color);
			this.color.setLightness(lightness);
			this.updateBgColor();
		};

		ColorSample.prototype.updateBrightness = function updateBrightness(color, value, steps) {
			var brightness = color.value + value * steps;
			if (brightness <= 0) {
				this.node.setAttribute('data-hidden', 'true');
				return;
			}
			this.node.removeAttribute('data-hidden');
			this.color.copy(color);
			this.color.setValue(brightness);
			this.updateBgColor();
		};

		ColorSample.prototype.updateAlpha = function updateAlpha(color, value, steps) {
			var alpha = parseFloat(color.a) + value * steps;
			if (alpha <= 0) {
				this.node.setAttribute('data-hidden', 'true');
				return;
			}
			this.node.removeAttribute('data-hidden');
			this.color.copy(color);
			this.color.a = parseFloat(alpha.toFixed(2));
			this.updateBgColor();
		};

		ColorSample.prototype.pickColor = function pickColor() {
			UIColorPicker.setColor('picker', this.color);
		};

		ColorSample.prototype.dragStart = function dragStart(e) {
			e.dataTransfer.setData('sampleID', this.uid);
			e.dataTransfer.setData('location', 'palette-samples');
		};

        // this is the general class for the palette on top
		var Palette = function Palette(text, size) {
			this.samples = [];
			this.locked = false;

			var palette = document.createElement('div');
			var title = document.createElement('div');
			var controls = document.createElement('div');
			var container = document.createElement('div');
			var lock = document.createElement('div');

			container.className = 'container';
			title.className = 'title';
			palette.className = 'palette';
			controls.className = 'controls';
			lock.className = 'lock';
			title.textContent = text;

			controls.appendChild(lock);
			container.appendChild(title);
			container.appendChild(controls);
			container.appendChild(palette);

			lock.addEventListener('click', function () {
				this.locked = !this.locked;
				lock.setAttribute('locked-state', this.locked);
			}.bind(this));

			for(var i = 0; i < size; i++) {
				var sample = new ColorSample();
				this.samples.push(sample);
				palette.appendChild(sample.node);
			}

			this.container = container;
			this.title = title;
		};

		var createHuePalette = function createHuePalette() {
		    var samples_hue_palette = 12;
			var palette = new Palette('Hue', samples_hue_palette);

			UIColorPicker.subscribe('picker', function(color) {
				if (palette.locked === true)
					return;

				for(var i = 0; i < samples_hue_palette; i++) {
					palette.samples[i].updateHue(color, 5, i);
				}
			});

			color_palette.appendChild(palette.container);
		};

		var createSaturationPalette = function createSaturationPalette() {
			var palette = new Palette('Saturation', 11);

			UIColorPicker.subscribe('picker', function(color) {
				if (palette.locked === true)
					return;

				for(var i = 0; i < 11; i++) {
					palette.samples[i].updateSaturation(color, -10, i);
				}
			});

			color_palette.appendChild(palette.container);
		};

		/* Brightness or Lightness - depends on the picker mode */
		var createVLPalette = function createSaturationPalette() {
			var palette = new Palette('Lightness', 11);

			UIColorPicker.subscribe('picker', function(color) {
				if (palette.locked === true)
					return;

				if(color.format === 'HSL') {
					palette.title.textContent = 'Lightness';
					for(var i = 0; i < 11; i++)
						palette.samples[i].updateLightness(color, -10, i);
				}
				else {
					palette.title.textContent = 'Value';
					for(var i = 0; i < 11; i++)
						palette.samples[i].updateBrightness(color, -10, i);
				}
			});

			color_palette.appendChild(palette.container);
		};

		var isBlankPalette = function isBlankPalette(container, value) {
			if (value === 0) {
				container.setAttribute('data-collapsed', 'true');
				return true;
			}

			container.removeAttribute('data-collapsed');
			return false;
		};

		var createAlphaPalette = function createAlphaPalette() {
			var palette = new Palette('Alpha', 10);

			UIColorPicker.subscribe('picker', function(color) {
				if (palette.locked === true)
					return;

				for(var i = 0; i < 10; i++) {
					palette.samples[i].updateAlpha(color, -0.1, i);
				}
			});

			color_palette.appendChild(palette.container);
		};

		var getSampleColor = function getSampleColor(id) {
			if (samples[id] !== undefined && samples[id]!== null)
				return new Color(samples[id].color);
		};

		var init = function init() {
			color_palette = getElemById('color-palette');

			createHuePalette();
			createSaturationPalette();
			createVLPalette();
			createAlphaPalette();

		};

		return {
			init : init,
			getSampleColor : getSampleColor
		};

	})();

	/**
	 * ColorInfo
	 */
	var ColorInfo = (function ColorInfo() {

		var info_box;
		var select;
		var RGBA;
		var HEXA;
		var HSLA;

		var updateInfo = function updateInfo(color) {
			if (color.a | 0 === 1) {
				RGBA.info.textContent = 'RGB';
				HSLA.info.textContent = 'HSL';
			}
			else {
				RGBA.info.textContent = 'RGBA';
				HSLA.info.textContent = 'HSLA';
			}

			RGBA.value.value = color.getRGBA();
			HSLA.value.value = color.getHSLA();
			HEXA.value.value = color.getHexa();
		};

		var InfoProperty = function InfoProperty(info) {

			var node = document.createElement('div');
			var title = document.createElement('div');
			var value = document.createElement('input');
			var copy = document.createElement('div');

			node.className = 'property';
			title.className = 'type';
			value.className = 'value';
			copy.className = 'copy';

			title.textContent = info;
			value.setAttribute('type', 'text');

			copy.addEventListener('click', function() {
				value.select();
				// this copies value to clipboard
				document.execCommand("copy");
			});

			node.appendChild(title);
			node.appendChild(value);
			node.appendChild(copy);

			this.node = node;
			this.value = value;
			this.info = title;

			info_box.appendChild(node);
		};

		var init = function init() {

			info_box = getElemById('color-info');

			RGBA = new InfoProperty('RGBA');
			HSLA = new InfoProperty('HSLA');
			HEXA = new InfoProperty('HEXA');

			UIColorPicker.subscribe('picker', updateInfo);

		};

		return {
			init: init
		};

	})();

	/**
	 * ColorPicker Samples
	 */
	// there are the sample colors that are managed in the middle area
	var ColorPickerSamples = (function ColorPickerSamples() {

		var samples = [];
		var nr_samples = 0;
		var active = null;
		var container = null;
		var trash_can = null;
		var base_color = new HSLColor(0, 0, 100);
		var add_btn;
		var add_btn_pos;

		var ColorSample = function ColorSample() {
            // this is the overall node that will hold all sample information
            var node = document.createElement('div');
            node.className = 'sample';
            var sample_contents_template = document.getElementById('sample-template');
            var contents = document.importNode(sample_contents_template.content, true);
            node.appendChild(contents);

            // settings all the other necessary values
			this.uid = samples.length;
			this.index = nr_samples++;
			this.node = node;
			this.sampleColor = node.querySelector('.sample-color');
			this.color = new Color(base_color);

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
			node.querySelector('.copy-line').addEventListener(
			    'click', this.copyLineIconClick.bind(this));

			this.updateBgColor();
			samples.push(this);

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

        ColorSample.prototype.updateState = function(color,key_value,meta_value) {
			this.updateColor(color);
			this.key_input.value = key_value;
			this.meta_input.value = meta_value;
		};

		ColorSample.prototype.activate = function activate() {
			UIColorPicker.setColor('picker', this.color);
			this.node.setAttribute('data-active', 'true');
		};

		ColorSample.prototype.deactivate = function deactivate() {
			this.node.removeAttribute('data-active');
		};

		ColorSample.prototype.dragStart = function (e) {
		    console.log("Started dragging:" + this.uid);
			e.dataTransfer.setData('sampleID', this.uid);
			e.dataTransfer.setData('location', 'picker-samples');
		};

        ColorSample.prototype.copyColorIconClick = function (e) {
		    navigator.clipboard.writeText(this.color.getSimpleHex());
		};

        ColorSample.prototype.copyStateIconClick = function (e) {
		    navigator.clipboard.writeText(this.getDigest());
		};

        ColorSample.prototype.copyLineIconClick = function (e) {

            var list_hex = [];
            var my_line = Math.trunc(this.uid / SAMPLES_PER_LINE);
            for (var i = 0; i < SAMPLES_PER_LINE; i++) {
                var current_sample_id = my_line*SAMPLES_PER_LINE + i;
                var hex = samples[current_sample_id].color.getSimpleHex();
                var digest = samples[current_sample_id].getDigest();
                if( hex !== "ffffff") {
                    list_hex.push(digest);
                }

            }

            var final_string = 'NO_COLORS_IN_THIS_LINE';
            if( list_hex.length > 0 ) {
                final_string = list_hex.join('-');
            }

		    navigator.clipboard.writeText(final_string);
		};

		ColorSample.prototype.dragDrop = function (e) {
			e.stopPropagation();
			var sampleID = e.dataTransfer.getData('sampleID');
			console.log("Dropping over:" + sampleID);
			console.log("Being dropped on:" + this.uid);

            var dragged_sample = samples[sampleID];
            var dragged_color = dragged_sample.color;
            var dragged_key_value = dragged_sample.key_input.value;
            var dragged_meta_value = dragged_sample.meta_input.value;

			var old_color = getSampleColor(this.uid);
			var old_key_value = this.key_input.value;
			var old_meta_value = this.meta_input.value;

			// updating the color of the sample on which it is dropped
			this.updateState(
			    dragged_color,dragged_key_value,dragged_meta_value);
			dragged_sample.updateState(
			    old_color,old_key_value,old_meta_value);
		};

		ColorSample.prototype.deleteSample = function deleteSample() {
			container.removeChild(this.node);
			samples[this.uid] = null;
			nr_samples--;
		};

		var updateUI = function updateUI() {

			var nr = samples.length;
			for (var i=0; i < nr; i++)
				if (samples[i] !== null) {
					samples[i].updateBgColor();
				}

		};

		var deleteSample = function deleteSample(e) {
			trash_can.parentElement.setAttribute('drag-state', 'none');

			var location = e.dataTransfer.getData('location');
			if (location !== 'picker-samples')
				return;

			var sampleID = e.dataTransfer.getData('sampleID');
			// We do not want to delete it
//			samples[sampleID].deleteSample();
            // just reset it
			samples[sampleID].color = new Color(base_color);
			updateUI();
		};

		var setActivateSample = function setActivateSample(e) {
			if (e.target.parentNode.className !== 'sample')
				return;
			unsetActiveSample(active);
			Tool.unsetVoidSample();
			active = samples[e.target.parentNode.getAttribute('sample-id')];
			active.activate();
		};

		var unsetActiveSample = function unsetActiveSample() {
			if (active)
				active.deactivate();
			active = null;
		};

		var getSampleColor = function getSampleColor(id) {
			if (samples[id] !== undefined && samples[id]!== null)
				return new Color(samples[id].color);
		};


        var getAllColorsAsString = function getAllColorsAsString() {
            var list_hex = [];
            samples.forEach(function(sample) {
                var hex = sample.color.getSimpleHex();
                // only interested in colors that are not white
                if( hex !== "ffffff") {
                    list_hex.push(hex);
                }
            });

            if( list_hex.length > 0 ) {
                return list_hex.join('-');
            }
            else {
                return "";
            }
        }


        var SampleLine = function(line_id)  {

            var node = document.createElement('div');
            this.node = node;
			this.line_id = line_id;

            node.setAttribute('line-id', line_id);
            node.className = 'sample-line';

            for (var i=0; i<SAMPLES_PER_LINE; i++) {
                var sample = new ColorSample();
                node.appendChild(sample.node)
            }

            var line_toolbar = document.createElement('div');
            line_toolbar.textContent = '+';
            line_toolbar.className = 'line-toolbar';
            node.appendChild(line_toolbar);

        };

		var init = function init() {
			container = getElemById('picker-samples');
			trash_can = getElemById('trash-can');

//			AddSampleButton.init();

            // Adding lines with samples to the picker
            for (var line=0; line<NUM_STARTING_LINES; line++) {

                var sampleLine = new SampleLine(line);
                container.appendChild(sampleLine.node);
            }


			updateUI();

			active = samples[0];
			active.activate();

			container.addEventListener('click', setActivateSample);

			trash_can.addEventListener('dragover', allowDropEvent);
			trash_can.addEventListener('dragenter', function() {
				this.parentElement.setAttribute('drag-state', 'enter');
			});
			trash_can.addEventListener('dragleave', function(e) {
				this.parentElement.setAttribute('drag-state', 'none');
			});
			trash_can.addEventListener('drop', deleteSample);

			UIColorPicker.subscribe('picker', function(color) {
				if (active)
					active.updateColor(color);
			});

		};

		return {
			init : init,
			getSampleColor : getSampleColor,
			unsetActiveSample : unsetActiveSample,
			getAllColorsAsString : getAllColorsAsString
		};

	})();

	var StateButton = function StateButton(node, state) {
		this.state = false;
		this.callback = null;

		node.addEventListener('click', function() {
			this.state = !this.state;
			if (typeof this.callback === "function")
				this.callback(this.state);
		}.bind(this));
	};

	StateButton.prototype.set = function set() {
		this.state = true;
		if (typeof this.callback === "function")
			this.callback(this.state);
	};

	StateButton.prototype.unset = function unset() {
		this.state = false;
		if (typeof this.callback === "function")
			this.callback(this.state);
	};

	StateButton.prototype.subscribe = function subscribe(func) {
		this.callback = func;
	};


	/**
	 * Tool
	 */
	 // this is the toolbar on the right side
	var Tool = (function Tool() {

		var samples = [];
		var controls = null;
		var void_sw;

		var createPickerModeSwitch = function createPickerModeSwitch() {
			var parent = getElemById('controls');
			var icon_copy_all = document.createElement('div');
			var button = document.createElement('div');
			var hsv = document.createElement('div');
			var hsl = document.createElement('div');
			var active = null;

			icon_copy_all.className = 'icon copy-icon';
			button.className = 'switch';
			button.appendChild(hsv);
			button.appendChild(hsl);

			hsv.textContent = 'HSV';
			hsl.textContent = 'HSL';

			active = hsl;
			active.setAttribute('data-active', 'true');

			function switchPickingModeTo(elem) {
				active.removeAttribute('data-active');
				active = elem;
				active.setAttribute('data-active', 'true');
				UIColorPicker.setPickerMode('picker', active.textContent);
			};


			icon_copy_all.addEventListener('click', function() {

				var s = ColorPickerSamples.getAllColorsAsString();
				console.log(s);
				// Copy string to clipboard
				navigator.clipboard.writeText(s);
			});

			hsv.addEventListener('click', function() {
				switchPickingModeTo(hsv);
			});
			hsl.addEventListener('click', function() {
				switchPickingModeTo(hsl);
			});

			parent.appendChild(icon_copy_all);
			parent.appendChild(button);
		};

		var setPickerDragAndDrop = function setPickerDragAndDrop() {
			var preview = document.querySelector('#picker .preview-color');
			var picking_area = document.querySelector('#picker .picking-area');

			preview.setAttribute('draggable', 'true');
			preview.addEventListener('drop', drop);
			preview.addEventListener('dragstart', dragStart);
			preview.addEventListener('dragover', allowDropEvent);

			picking_area.addEventListener('drop', drop);
			picking_area.addEventListener('dragover', allowDropEvent);

			function drop(e) {
				var color = getSampleColorFrom(e);
				UIColorPicker.setColor('picker', color);
			};

			function dragStart(e) {
				e.dataTransfer.setData('sampleID', 'picker');
				e.dataTransfer.setData('location', 'picker');
			};
		};

		var getSampleColorFrom = function getSampleColorFrom(e) {
			var sampleID = e.dataTransfer.getData('sampleID');
			var location = e.dataTransfer.getData('location');

			if (location === 'picker')
				return UIColorPicker.getColor(sampleID);
			if (location === 'picker-samples')
				return ColorPickerSamples.getSampleColor(sampleID);
			if (location === 'palette-samples')
				return ColorPalette.getSampleColor(sampleID);
		};

		var setVoidSwitch = function setVoidSwitch() {
			var void_sample = getElemById('void-sample');
			void_sw = new StateButton(void_sample);
			void_sw.subscribe( function (state) {
				void_sample.setAttribute('data-active', state);
				if (state === true) {
					ColorPickerSamples.unsetActiveSample();
				}
			});
		};

		var unsetVoidSample = function unsetVoidSample() {
			void_sw.unset();
		};

		var init = function init() {
			controls = getElemById('controls');

			var color = new Color();
			color.setHSL(0, 51, 51);
			UIColorPicker.setColor('picker', color);

			setPickerDragAndDrop();
			createPickerModeSwitch();
			setVoidSwitch();
		};

		return {
			init : init,
			unsetVoidSample : unsetVoidSample,
			getSampleColorFrom : getSampleColorFrom
		};

	})();

	var init = function init() {
		UIColorPicker.init();
		ColorInfo.init();
		ColorPalette.init();
		ColorPickerSamples.init();
		Tool.init();
	};

	return {
		init : init
	};

})();
