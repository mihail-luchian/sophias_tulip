
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

		this.newInputComponent('R', 'red', this.inputChangeRed.bind(this));
		this.newInputComponent('G', 'green', this.inputChangeGreen.bind(this));
		this.newInputComponent('B', 'blue', this.inputChangeBlue.bind(this));

		this.createPreviewBox();

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

		var x = e.clientX - this.picking_area.offsetLeft;
		var y = e.clientY - this.picking_area.offsetTop;
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
        var elem = document.getElementById('color-picker');
        console.log(elem)
        new ColorPicker(elem);
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

		var PaletteColorSample = function (id) {
			var node = document.createElement('div');
			node.className = 'palette-sample-color';

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


		PaletteColorSample.prototype.updateBgColor = function() {
			this.node.style.backgroundColor = this.color.getColor();
		};

		PaletteColorSample.prototype.updateColor = function(color) {
			this.color.copy(color);
			this.updateBgColor();
		};


		PaletteColorSample.prototype.updateHue = function (color, degree, steps) {
			this.color.copy(color);
			var hue = (steps * degree + this.color.hue) % 360;
			if (hue < 0) hue += 360;
			this.color.setHue(hue);
			this.updateBgColor();
		};

		PaletteColorSample.prototype.updateSaturation = function (color, value, steps) {
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

		PaletteColorSample.prototype.updateLightness = function (color, value, steps) {
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

		PaletteColorSample.prototype.updateBrightness = function (color, value, steps) {
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


		PaletteColorSample.prototype.pickColor = function () {
			UIColorPicker.setColor('picker', this.color);
		};

		PaletteColorSample.prototype.dragStart = function (e) {
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

			container.className = 'palette-container';
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
				var sample = new PaletteColorSample();
				this.samples.push(sample);
				palette.appendChild(sample.node);
			}

			this.container = container;
			this.title = title;
		};

		var createHuePalette = function createHuePalette() {
		    var samples_hue_palette = 8;
			var palette = new Palette('H', samples_hue_palette);

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
		    var samples_sat_palette = 8;
			var palette = new Palette('S', samples_sat_palette);

			UIColorPicker.subscribe('picker', function(color) {
				if (palette.locked === true)
					return;

				for(var i = 0; i < samples_sat_palette; i++) {
					palette.samples[i].updateSaturation(color, -10, i);
				}
			});

			color_palette.appendChild(palette.container);
		};

		/* Brightness or Lightness - depends on the picker mode */
		var createVLPalette = function createSaturationPalette() {
            var samples_vl_palette = 8;
			var palette = new Palette('L', samples_vl_palette);

			UIColorPicker.subscribe('picker', function(color) {
				if (palette.locked === true)
					return;

				if(color.format === 'HSL') {
					palette.title.textContent = 'L';
					for(var i = 0; i < samples_vl_palette; i++)
						palette.samples[i].updateLightness(color, -10, i);
				}
				else {
					palette.title.textContent = 'V';
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


		var getSampleColor = function getSampleColor(id) {
			if (samples[id] !== undefined && samples[id]!== null)
				return new Color(samples[id].color);
		};

		var init = function init() {
			color_palette = getElemById('color-palettes');

			createHuePalette();
			createSaturationPalette();
			createVLPalette();

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

//			info_box = getElemById('color-info');

//			RGBA = new InfoProperty('RGBA');
//			HSLA = new InfoProperty('HSLA');
//			HEXA = new InfoProperty('HEXA');

//			UIColorPicker.subscribe('picker', updateInfo);

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
		var base_color = new HSLColor(0, 0, 100);
		var add_btn;
		var add_btn_pos;

		var ColorSample = function () {
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
            node.querySelector('.delete-color').addEventListener(
			    'click', this.deleteColorIconClick.bind(this));
            node.querySelector('.delete-state').addEventListener(
			    'click', this.deleteStateIconClick.bind(this));
            node.querySelector('.paste-color').addEventListener(
			    'click', this.pasteColorIconClick.bind(this));
            node.querySelector('.paste-state').addEventListener(
			    'click', this.pasteStateIconClick.bind(this));

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

        ColorSample.prototype.deleteColorIconClick = function (e) {
		    this.color = new Color(base_color);
		    this.updateBgColor();
		};

        ColorSample.prototype.deleteStateIconClick = function (e) {
		    this.color = new Color(base_color);
		    this.updateBgColor();
		    this.key_input.value = '';
		    this.meta_input.value = '';
		};

        ColorSample.prototype.pasteStateIconClick = function (e) {
            var states = prompt("Enter your state", "0/ffffff/");
            if( states != null ) {
                var s = parseStates(states);
                var l = s.length;
                for( var i = 0; i < l; i++) {
                    var state = s[i];
                    console.log(state);
                    var color = state[1];
                    var key = state[0];
                    var meta = state[2];
                    if( i+this.uid < samples.length ) {
                        samples[i+this.uid].updateState(color,key,meta);
                    }
                }
            }
		};

        ColorSample.prototype.pasteColorIconClick = function (e) {
            var colors = prompt("Enter your state", "ffffff");
            if( colors != null ) {
                var s = parseColors(colors);
                var l = s.length;

                for( var i = 0; i < l; i++) {
                    var color = s[i];
                    if( i+this.uid < samples.length ) {
                        samples[i+this.uid].updateColor(color);
                    }
                }
            }
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
			var sampleLocation = e.dataTransfer.getData('location');
			if( sampleLocation == 'picker-samples')
			{
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
			}
			else
			{
			    var color = Tool.getSampleColorFrom(e);
			    this.updateColor(color);
			}


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


        var getStateAllColors = function getStateAllColors() {
            var list_hex = [];
            samples.forEach(function(sample) {
                var hex = sample.color.getSimpleHex();
                var state = sample.getDigest();
                // only interested in colors that are not white
                if( hex !== "ffffff") {
                    list_hex.push(state);
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
			container = getElemById('container-samples');

            // Adding lines with samples to the picker
            for (var line=0; line<NUM_STARTING_LINES; line++) {

                var sampleLine = new SampleLine(line);
                container.appendChild(sampleLine.node);
            }


			updateUI();

			active = samples[0];
			active.activate();

			container.addEventListener('click', setActivateSample);

			UIColorPicker.subscribe('picker', function(color) {
				if (active)
					active.updateColor(color);
			});

		};

		return {
			init : init,
			getSampleColor : getSampleColor,
			unsetActiveSample : unsetActiveSample,
			getStateAllColors : getStateAllColors
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
		var node;

		var createPickerModeSwitch = function createPickerModeSwitch() {
			node = getElemById('app-controls');

            var tools_template = document.getElementById('tools-template');
            var contents = document.importNode(tools_template.content, true);
            node.appendChild(contents);

			var hsv = node.querySelector('#hsv');
			var hsl = node.querySelector('#hsl');
			var icon_copy_all = node.querySelector('#copy-all');

			var active = null;
			active = hsl;
			active.setAttribute('data-active', 'true');

			function switchPickingModeTo(elem) {
				active.removeAttribute('data-active');
				active = elem;
				active.setAttribute('data-active', 'true');
                setVoidSample();
				UIColorPicker.setPickerMode('picker', active.textContent);
			};


			icon_copy_all.addEventListener('click', function() {
				var s = ColorPickerSamples.getStateAllColors();
				$('.toast').toast('show');
				// Copy string to clipboard
				navigator.clipboard.writeText(s);

			});

			hsv.addEventListener('click', function() {
				switchPickingModeTo(hsv);
			});
			hsl.addEventListener('click', function() {
				switchPickingModeTo(hsl);
			});

		};

		var setPickerDragAndDrop = function setPickerDragAndDrop() {
			var preview = document.querySelector('#color-picker .preview-color');
			var picking_area = document.querySelector('#color-picker .picking-area');

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

		var setVoidSwitch = function() {
			var void_sample = node.querySelector('#void-sample');
			void_sw = new StateButton(void_sample);
			void_sw.subscribe( function (state) {
				void_sample.setAttribute('data-active', state);
				if (state === true) {
					ColorPickerSamples.unsetActiveSample();
				}
			});
		};

		var unsetVoidSample = function() {
			void_sw.unset();
		};

        var setVoidSample = function() {
			void_sw.set();
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
			setVoidSample : setVoidSample,
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
